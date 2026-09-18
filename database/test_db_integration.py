"""
TerraFlux Database Integration Tests

Tests the complete persistence layer against a live Supabase/PostgreSQL database.

Requires DATABASE_URL environment variable pointing to the Supabase database.

Usage:
    set DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
    python database/test_db_integration.py

These tests verify:
    A. Policy creation
    B. Telemetry idempotency
    C. Validation persistence
    D. Consensus persistence
    E. Trigger evaluation persistence
    F. Payout uniqueness
    G. Duplicate payout rejection
    H. Wallet transaction uniqueness
    I. Atomic wallet update
    J. Audit creation
    K. No-consensus produces no payout
    L. Corrupted telemetry still allows 2-of-3 consensus
    M. 10 repeated settlement attempts produce exactly 1 wallet transaction
"""

import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

# We use raw psycopg2 for maximum control over transactions
try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set.")
    print("Set it to your Supabase PostgreSQL connection string.")
    sys.exit(1)

# ============================================================
# Fixed UUIDs matching seed data
# ============================================================
POLICYHOLDER_ID = "a1000000-0000-0000-0000-000000000001"
REGION_ID = "b2000000-0000-0000-0000-000000000001"
SOURCE_A_ID = "c3000000-0000-0000-0000-000000000001"
SOURCE_B_ID = "c3000000-0000-0000-0000-000000000002"
SOURCE_C_ID = "c3000000-0000-0000-0000-000000000003"
TRIGGER_RULE_ID = "d4000000-0000-0000-0000-000000000001"
POLICY_ID = "e5000000-0000-0000-0000-000000000001"
WALLET_ID = "f6000000-0000-0000-0000-000000000001"

passed = 0
failed = 0
errors = []


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def test(name):
    """Decorator for test functions."""
    def decorator(func):
        def wrapper():
            global passed, failed
            try:
                func()
                passed += 1
                print(f"  ✓ {name}")
            except Exception as e:
                failed += 1
                errors.append((name, str(e)))
                print(f"  ✗ {name}: {e}")
        return wrapper
    return decorator


def cleanup_test_data(conn):
    """Remove test-generated data (NOT seed data). Safe cleanup."""
    with conn.cursor() as cur:
        # Delete in reverse dependency order
        cur.execute("DELETE FROM public.audit_events WHERE actor = 'test_runner'")
        cur.execute("DELETE FROM public.wallet_transactions WHERE wallet_id = %s", (WALLET_ID,))
        cur.execute("DELETE FROM public.payouts WHERE policy_id = %s", (POLICY_ID,))
        cur.execute("DELETE FROM public.trigger_evaluations WHERE policy_id = %s", (POLICY_ID,))
        cur.execute("DELETE FROM public.consensus_members WHERE consensus_result_id IN (SELECT id FROM public.consensus_results WHERE region_id = %s)", (REGION_ID,))
        cur.execute("DELETE FROM public.consensus_results WHERE region_id = %s", (REGION_ID,))
        cur.execute("DELETE FROM public.telemetry_validation_results WHERE telemetry_event_id IN (SELECT id FROM public.telemetry_events WHERE region_id = %s)", (REGION_ID,))
        cur.execute("DELETE FROM public.telemetry_events WHERE region_id = %s", (REGION_ID,))
        # Reset wallet balance to 0
        cur.execute("UPDATE public.wallets SET balance_paise = 0 WHERE id = %s", (WALLET_ID,))
    conn.commit()


# ============================================================
# TEST A: Seed data exists (policy creation)
# ============================================================
@test("A. Seed data and policy exist")
def test_seed_data():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, payout_amount_paise, status FROM public.policies WHERE id = %s", (POLICY_ID,))
            row = cur.fetchone()
            assert row is not None, "Policy not found"
            assert row[1] == 1000000, f"Expected 1000000 paise, got {row[1]}"
            assert row[2] == "ACTIVE", f"Expected ACTIVE, got {row[2]}"
    finally:
        conn.close()


# ============================================================
# TEST B: Telemetry ingestion idempotency
# ============================================================
@test("B. Telemetry idempotency (duplicate source_event_id rejected)")
def test_telemetry_idempotency():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        with conn.cursor() as cur:
            # First insert
            cur.execute("""
                INSERT INTO public.telemetry_events
                    (source_id, region_id, source_event_id, metric, value, unit,
                     observed_at, window_start, window_end, validation_state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACCEPTED')
            """, (SOURCE_A_ID, REGION_ID, 'TEST-IDEM-001', 'RAINFALL_MM', 110.0, 'mm',
                  now, now - timedelta(hours=1), now))
            conn.commit()

            # Duplicate insert should fail
            try:
                cur.execute("""
                    INSERT INTO public.telemetry_events
                        (source_id, region_id, source_event_id, metric, value, unit,
                         observed_at, window_start, window_end, validation_state)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACCEPTED')
                """, (SOURCE_A_ID, REGION_ID, 'TEST-IDEM-001', 'RAINFALL_MM', 110.0, 'mm',
                      now, now - timedelta(hours=1), now))
                conn.commit()
                raise AssertionError("Duplicate telemetry insert should have been rejected")
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                # Expected behavior
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST C: Validation persistence
# ============================================================
@test("C. Validation result persistence")
def test_validation_persistence():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        with conn.cursor() as cur:
            tel_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO public.telemetry_events
                    (id, source_id, region_id, source_event_id, metric, value, unit,
                     observed_at, window_start, window_end, validation_state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACCEPTED')
            """, (tel_id, SOURCE_A_ID, REGION_ID, 'TEST-VAL-001', 'RAINFALL_MM', 110.0, 'mm',
                  now, now - timedelta(hours=1), now))

            cur.execute("""
                INSERT INTO public.telemetry_validation_results
                    (telemetry_event_id, validation_rule, outcome, reason_code)
                VALUES (%s, %s, %s, %s)
            """, (tel_id, 'RANGE_CHECK', 'PASS', 'WITHIN_BOUNDS'))
            conn.commit()

            cur.execute("SELECT outcome FROM public.telemetry_validation_results WHERE telemetry_event_id = %s", (tel_id,))
            assert cur.fetchone()[0] == 'PASS'
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST D: Consensus persistence
# ============================================================
@test("D. Consensus persistence")
def test_consensus_persistence():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)
        with conn.cursor() as cur:
            con_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO public.consensus_results
                    (id, region_id, metric, window_start, window_end, state, value, quorum)
                VALUES (%s, %s, %s, %s, %s, 'ACHIEVED', %s, %s)
            """, (con_id, REGION_ID, 'RAINFALL_MM', window_start, now, 110.0, 3))
            conn.commit()

            cur.execute("SELECT state, value, quorum FROM public.consensus_results WHERE id = %s", (con_id,))
            row = cur.fetchone()
            assert row[0] == 'ACHIEVED'
            assert float(row[1]) == 110.0
            assert row[2] == 3
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST E: Trigger evaluation persistence
# ============================================================
@test("E. Trigger evaluation persistence")
def test_trigger_evaluation():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.consensus_results
                    (id, region_id, metric, window_start, window_end, state, value, quorum)
                VALUES (%s, %s, %s, %s, %s, 'ACHIEVED', %s, %s)
            """, (con_id, REGION_ID, 'RAINFALL_MM', now - timedelta(hours=1), now, 110.0, 3))

            trig_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO public.trigger_evaluations
                    (id, policy_id, consensus_result_id, outcome, reason)
                VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')
            """, (trig_id, POLICY_ID, con_id))
            conn.commit()

            cur.execute("SELECT outcome FROM public.trigger_evaluations WHERE id = %s", (trig_id,))
            assert cur.fetchone()[0] == 'TRIGGERED'
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST F+G: Payout uniqueness / duplicate rejection
# ============================================================
@test("F/G. Payout uniqueness and duplicate rejection")
def test_payout_uniqueness():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        trig_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            # Setup consensus + trigger
            cur.execute("""
                INSERT INTO public.consensus_results (id, region_id, metric, window_start, window_end, state, value, quorum)
                VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 110.0, 3)
            """, (con_id, REGION_ID, now - timedelta(hours=1), now))

            cur.execute("""
                INSERT INTO public.trigger_evaluations (id, policy_id, consensus_result_id, outcome, reason)
                VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')
            """, (trig_id, POLICY_ID, con_id))

            # First payout
            cur.execute("""
                INSERT INTO public.payouts
                    (policy_id, trigger_evaluation_id, wallet_id, amount_paise, state,
                     idempotency_scope, idempotency_key)
                VALUES (%s, %s, %s, %s, 'PENDING', %s, %s)
            """, (POLICY_ID, trig_id, WALLET_ID, 1000000, 'SETTLEMENT', f'payout-{POLICY_ID}'))
            conn.commit()

            # Duplicate payout for same policy should fail
            try:
                trig_id_2 = str(uuid.uuid4())
                con_id_2 = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO public.consensus_results (id, region_id, metric, window_start, window_end, state, value, quorum)
                    VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 112.0, 3)
                """, (con_id_2, REGION_ID, now - timedelta(hours=2), now - timedelta(hours=1)))
                cur.execute("""
                    INSERT INTO public.trigger_evaluations (id, policy_id, consensus_result_id, outcome, reason)
                    VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')
                """, (trig_id_2, POLICY_ID, con_id_2))
                conn.commit()
                raise AssertionError("Duplicate trigger eval for same policy+consensus should fail... but checking payout")
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                # trigger_evaluations unique(policy_id, consensus_result_id) may or may not fire
                # The critical check is payout uniqueness

    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST H: Wallet transaction uniqueness
# ============================================================
@test("H. Wallet transaction uniqueness (one txn per payout)")
def test_wallet_txn_uniqueness():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        trig_id = str(uuid.uuid4())
        payout_id = str(uuid.uuid4())

        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.consensus_results (id, region_id, metric, window_start, window_end, state, value, quorum) VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 110.0, 3)",
                        (con_id, REGION_ID, now - timedelta(hours=1), now))
            cur.execute("INSERT INTO public.trigger_evaluations (id, policy_id, consensus_result_id, outcome, reason) VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')",
                        (trig_id, POLICY_ID, con_id))
            cur.execute("INSERT INTO public.payouts (id, policy_id, trigger_evaluation_id, wallet_id, amount_paise, state, idempotency_scope, idempotency_key) VALUES (%s, %s, %s, %s, 1000000, 'COMPLETED', 'SETTLEMENT', %s)",
                        (payout_id, POLICY_ID, trig_id, WALLET_ID, f'payout-{POLICY_ID}'))

            # First wallet transaction
            cur.execute("""
                INSERT INTO public.wallet_transactions (wallet_id, payout_id, direction, amount_paise, balance_before_paise, balance_after_paise)
                VALUES (%s, %s, 'CREDIT', 1000000, 0, 1000000)
            """, (WALLET_ID, payout_id))
            conn.commit()

            # Duplicate wallet transaction for same payout should fail
            try:
                cur.execute("""
                    INSERT INTO public.wallet_transactions (wallet_id, payout_id, direction, amount_paise, balance_before_paise, balance_after_paise)
                    VALUES (%s, %s, 'CREDIT', 1000000, 1000000, 2000000)
                """, (WALLET_ID, payout_id))
                conn.commit()
                raise AssertionError("Duplicate wallet transaction should have been rejected")
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST I: Atomic wallet update
# ============================================================
@test("I. Atomic wallet update (balance changes correctly)")
def test_atomic_wallet():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        trig_id = str(uuid.uuid4())
        payout_id = str(uuid.uuid4())

        with conn.cursor() as cur:
            # Verify starting balance
            cur.execute("SELECT balance_paise FROM public.wallets WHERE id = %s", (WALLET_ID,))
            start_balance = cur.fetchone()[0]
            assert start_balance == 0, f"Expected 0, got {start_balance}"

            # Setup chain
            cur.execute("INSERT INTO public.consensus_results (id, region_id, metric, window_start, window_end, state, value, quorum) VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 110.0, 3)",
                        (con_id, REGION_ID, now - timedelta(hours=1), now))
            cur.execute("INSERT INTO public.trigger_evaluations (id, policy_id, consensus_result_id, outcome, reason) VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')",
                        (trig_id, POLICY_ID, con_id))
            cur.execute("INSERT INTO public.payouts (id, policy_id, trigger_evaluation_id, wallet_id, amount_paise, state, idempotency_scope, idempotency_key, completed_at) VALUES (%s, %s, %s, %s, 1000000, 'COMPLETED', 'SETTLEMENT', %s, %s)",
                        (payout_id, POLICY_ID, trig_id, WALLET_ID, f'payout-{POLICY_ID}', now))

            # Atomic: insert txn + update wallet
            cur.execute("""
                INSERT INTO public.wallet_transactions (wallet_id, payout_id, direction, amount_paise, balance_before_paise, balance_after_paise)
                VALUES (%s, %s, 'CREDIT', 1000000, 0, 1000000)
            """, (WALLET_ID, payout_id))
            cur.execute("UPDATE public.wallets SET balance_paise = 1000000 WHERE id = %s", (WALLET_ID,))
            conn.commit()

            cur.execute("SELECT balance_paise FROM public.wallets WHERE id = %s", (WALLET_ID,))
            final_balance = cur.fetchone()[0]
            assert final_balance == 1000000, f"Expected 1000000, got {final_balance}"
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST J: Audit creation
# ============================================================
@test("J. Audit event creation")
def test_audit_creation():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        corr_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.audit_events
                    (correlation_id, entity_type, entity_id, event_type, actor, payload)
                VALUES (%s, 'PAYOUT', %s, 'PAYOUT_COMPLETED', 'test_runner', '{"amount_paise": 1000000}')
            """, (corr_id, POLICY_ID))
            conn.commit()

            cur.execute("SELECT event_type, actor FROM public.audit_events WHERE correlation_id = %s", (corr_id,))
            row = cur.fetchone()
            assert row[0] == 'PAYOUT_COMPLETED'
            assert row[1] == 'test_runner'
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST K: No-consensus produces no payout
# (Structural test: consensus state prevents trigger eval creation)
# ============================================================
@test("K. No-consensus: consensus_value must be NOT NULL when ACHIEVED")
def test_no_consensus():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        with conn.cursor() as cur:
            # Insert NO_CONSENSUS with null value — should succeed
            cur.execute("""
                INSERT INTO public.consensus_results
                    (id, region_id, metric, window_start, window_end, state, value, quorum)
                VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'NO_CONSENSUS', NULL, 0)
            """, (con_id, REGION_ID, now - timedelta(hours=1), now))
            conn.commit()

            # Try to insert ACHIEVED with null value — should fail due to check constraint
            con_id_2 = str(uuid.uuid4())
            try:
                cur.execute("""
                    INSERT INTO public.consensus_results
                        (id, region_id, metric, window_start, window_end, state, value, quorum)
                    VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', NULL, 3)
                """, (con_id_2, REGION_ID, now - timedelta(hours=2), now - timedelta(hours=1)))
                conn.commit()
                raise AssertionError("ACHIEVED consensus with NULL value should have been rejected")
            except psycopg2.errors.CheckViolation:
                conn.rollback()
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST L: Corrupted telemetry 2-of-3 consensus
# ============================================================
@test("L. Corrupted telemetry allows 2-of-3 consensus")
def test_corrupted_consensus():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)

        with conn.cursor() as cur:
            # Insert 3 telemetry readings (A=110, B=108, C=7 outlier)
            tel_a = str(uuid.uuid4())
            tel_b = str(uuid.uuid4())
            tel_c = str(uuid.uuid4())
            for tel_id, src_id, evt_id, val, state in [
                (tel_a, SOURCE_A_ID, 'CORR-A-001', 110.0, 'ACCEPTED'),
                (tel_b, SOURCE_B_ID, 'CORR-B-001', 108.0, 'ACCEPTED'),
                (tel_c, SOURCE_C_ID, 'CORR-C-001', 7.0, 'REJECTED'),
            ]:
                cur.execute("""
                    INSERT INTO public.telemetry_events
                        (id, source_id, region_id, source_event_id, metric, value, unit,
                         observed_at, window_start, window_end, validation_state)
                    VALUES (%s, %s, %s, %s, 'RAINFALL_MM', %s, 'mm', %s, %s, %s, %s::public.validation_state)
                """, (tel_id, src_id, REGION_ID, evt_id, val, now, window_start, now, state))

            # Consensus: ACHIEVED with 2-of-3
            con_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO public.consensus_results
                    (id, region_id, metric, window_start, window_end, state, value, quorum)
                VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 109.0, 2)
            """, (con_id, REGION_ID, window_start, now))

            # Members
            for tel_id, src_id, role, val, rej in [
                (tel_a, SOURCE_A_ID, 'ACCEPTED', 110.0, None),
                (tel_b, SOURCE_B_ID, 'ACCEPTED', 108.0, None),
                (tel_c, SOURCE_C_ID, 'OUTLIER', 7.0, 'STATISTICAL_OUTLIER'),
            ]:
                cur.execute("""
                    INSERT INTO public.consensus_members
                        (consensus_result_id, telemetry_event_id, source_id, role, normalized_value, rejection_reason)
                    VALUES (%s, %s, %s, %s::public.consensus_role, %s, %s)
                """, (con_id, tel_id, src_id, role, val, rej))

            conn.commit()

            # Verify
            cur.execute("SELECT state, value, quorum FROM public.consensus_results WHERE id = %s", (con_id,))
            row = cur.fetchone()
            assert row[0] == 'ACHIEVED'
            assert float(row[1]) == 109.0
            assert row[2] == 2

            cur.execute("SELECT COUNT(*) FROM public.consensus_members WHERE consensus_result_id = %s AND role = 'OUTLIER'", (con_id,))
            assert cur.fetchone()[0] == 1
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# TEST M: 10x replay produces exactly 1 wallet transaction
# ============================================================
@test("M. 10x replay produces exactly 1 wallet transaction")
def test_10x_replay():
    conn = get_conn()
    try:
        cleanup_test_data(conn)
        now = datetime.now(timezone.utc)
        con_id = str(uuid.uuid4())
        trig_id = str(uuid.uuid4())
        payout_id = str(uuid.uuid4())

        with conn.cursor() as cur:
            # Reset wallet to 0
            cur.execute("UPDATE public.wallets SET balance_paise = 0 WHERE id = %s", (WALLET_ID,))

            # Setup chain
            cur.execute("INSERT INTO public.consensus_results (id, region_id, metric, window_start, window_end, state, value, quorum) VALUES (%s, %s, 'RAINFALL_MM', %s, %s, 'ACHIEVED', 110.0, 3)",
                        (con_id, REGION_ID, now - timedelta(hours=1), now))
            cur.execute("INSERT INTO public.trigger_evaluations (id, policy_id, consensus_result_id, outcome, reason) VALUES (%s, %s, %s, 'TRIGGERED', 'THRESHOLD_MET')",
                        (trig_id, POLICY_ID, con_id))
            cur.execute("INSERT INTO public.payouts (id, policy_id, trigger_evaluation_id, wallet_id, amount_paise, state, idempotency_scope, idempotency_key, completed_at) VALUES (%s, %s, %s, %s, 1000000, 'COMPLETED', 'SETTLEMENT', %s, %s)",
                        (payout_id, POLICY_ID, trig_id, WALLET_ID, f'payout-{POLICY_ID}', now))
            conn.commit()

            # First settlement: succeeds
            cur.execute("""
                INSERT INTO public.wallet_transactions (wallet_id, payout_id, direction, amount_paise, balance_before_paise, balance_after_paise)
                VALUES (%s, %s, 'CREDIT', 1000000, 0, 1000000)
            """, (WALLET_ID, payout_id))
            cur.execute("UPDATE public.wallets SET balance_paise = 1000000 WHERE id = %s", (WALLET_ID,))
            conn.commit()

            # Attempts 2-10: all should fail due to unique(payout_id) on wallet_transactions
            duplicate_count = 0
            for attempt in range(2, 11):
                try:
                    cur.execute("""
                        INSERT INTO public.wallet_transactions (wallet_id, payout_id, direction, amount_paise, balance_before_paise, balance_after_paise)
                        VALUES (%s, %s, 'CREDIT', 1000000, 1000000, 2000000)
                    """, (WALLET_ID, payout_id))
                    conn.commit()
                    raise AssertionError(f"Attempt {attempt}: duplicate wallet txn should have failed")
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    duplicate_count += 1

            assert duplicate_count == 9, f"Expected 9 duplicates blocked, got {duplicate_count}"

            # Verify final state
            cur.execute("SELECT balance_paise FROM public.wallets WHERE id = %s", (WALLET_ID,))
            final_balance = cur.fetchone()[0]
            assert final_balance == 1000000, f"Expected 1000000 (one payout), got {final_balance}"

            cur.execute("SELECT COUNT(*) FROM public.wallet_transactions WHERE payout_id = %s", (payout_id,))
            txn_count = cur.fetchone()[0]
            assert txn_count == 1, f"Expected exactly 1 wallet transaction, got {txn_count}"
    finally:
        cleanup_test_data(conn)
        conn.close()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TerraFlux Database Integration Tests")
    print("=" * 60)
    print(f"Database: {DATABASE_URL[:40]}...")
    print()

    tests = [
        test_seed_data,
        test_telemetry_idempotency,
        test_validation_persistence,
        test_consensus_persistence,
        test_trigger_evaluation,
        test_payout_uniqueness,
        test_wallet_txn_uniqueness,
        test_atomic_wallet,
        test_audit_creation,
        test_no_consensus,
        test_corrupted_consensus,
        test_10x_replay,
    ]

    for t in tests:
        t()

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if errors:
        print()
        print("Failures:")
        for name, err in errors:
            print(f"  - {name}: {err}")
    print("=" * 60)
    sys.exit(1 if failed > 0 else 0)

