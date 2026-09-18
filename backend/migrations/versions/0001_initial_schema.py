"""Initial PS-F03 schema

Creates all tables for the PS-F03 Autonomous Parametric Climate Insurance backend.

Revision ID: 0001
Revises: (none)
Create Date: 2026-09-18

COORDINATION NOTE:
  Ramraj generated this migration.
  Akshaya must review and apply to shared PostgreSQL/Supabase instance.
  Do NOT run 'alembic upgrade head' against the shared DB without Akshaya's coordination.

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── micro_regions ─────────────────────────────────────────────────────────
    op.create_table(
        "micro_regions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── weather_sources ───────────────────────────────────────────────────────
    op.create_table(
        "weather_sources",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("region_id", sa.String(64), sa.ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_weather_sources_region_id", "region_id"),
    )

    # ── policies ──────────────────────────────────────────────────────────────
    op.create_table(
        "policies",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("region_id", sa.String(64), sa.ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("payout_amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── trigger_rules ─────────────────────────────────────────────────────────
    op.create_table(
        "trigger_rules",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("metric", sa.String(64), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=False),
        sa.Column("threshold_operator", sa.String(4), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("observation_window_minutes", sa.Integer(), nullable=False),
        sa.Column("consensus_quorum", sa.Integer(), nullable=False),
        sa.Column("consensus_tolerance", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── telemetry_events ──────────────────────────────────────────────────────
    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("event_id", sa.String(128), nullable=False, unique=True),
        sa.Column("source_id", sa.String(64), sa.ForeignKey("weather_sources.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("region_id", sa.String(64), sa.ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("metric", sa.String(64), nullable=False),
        sa.Column("value_mm", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("rejection_reason", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_telemetry_events_event_id", "event_id"),
        sa.Index("ix_telemetry_events_source_id", "source_id"),
        sa.Index("ix_telemetry_events_region_id", "region_id"),
    )

    # ── consensus_results ─────────────────────────────────────────────────────
    op.create_table(
        "consensus_results",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("region_id", sa.String(64), sa.ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("median_all_sources_mm", sa.Float(), nullable=True),
        sa.Column("consensus_value_mm", sa.Float(), nullable=True),
        sa.Column("source_count_total", sa.Integer(), nullable=False),
        sa.Column("source_count_accepted", sa.Integer(), nullable=False),
        sa.Column("source_count_outliers", sa.Integer(), nullable=False),
        sa.Column("accepted_source_ids", sa.JSON(), nullable=True),
        sa.Column("outlier_source_ids", sa.JSON(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_consensus_results_policy_id", "policy_id"),
    )

    # ── trigger_evaluations ───────────────────────────────────────────────────
    op.create_table(
        "trigger_evaluations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consensus_result_id", sa.String(26), sa.ForeignKey("consensus_results.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("trigger_status", sa.String(40), nullable=False),
        sa.Column("consensus_value_mm", sa.Float(), nullable=True),
        sa.Column("threshold_mm", sa.Float(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_trigger_evaluations_policy_id", "policy_id"),
        sa.Index("ix_trigger_evaluations_trigger_status", "trigger_status"),
    )

    # ── payouts ───────────────────────────────────────────────────────────────
    op.create_table(
        "payouts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("trigger_evaluation_id", sa.String(26), sa.ForeignKey("trigger_evaluations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=False, unique=True),
        sa.Column("failure_reason", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        # THE CRITICAL IDEMPOTENCY CONSTRAINT
        sa.UniqueConstraint("policy_id", "trigger_evaluation_id", name="uq_payout_policy_trigger"),
        sa.Index("ix_payouts_policy_id", "policy_id"),
    )

    # ── wallets ───────────────────────────────────────────────────────────────
    op.create_table(
        "wallets",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("balance_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── wallet_transactions ───────────────────────────────────────────────────
    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("wallet_id", sa.String(64), sa.ForeignKey("wallets.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("payout_id", sa.String(26), sa.ForeignKey("payouts.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("balance_before_paise", sa.BigInteger(), nullable=False),
        sa.Column("balance_after_paise", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_wallet_transactions_wallet_id", "wallet_id"),
    )

    # ── audit_events ──────────────────────────────────────────────────────────
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("policy_id", sa.String(64), sa.ForeignKey("policies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("correlation_id", sa.String(26), nullable=True),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Index("ix_audit_events_event_type", "event_type"),
        sa.Index("ix_audit_events_entity_id", "entity_id"),
        sa.Index("ix_audit_events_policy_id", "policy_id"),
        sa.Index("ix_audit_events_correlation_id", "correlation_id"),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("audit_events")
    op.drop_table("wallet_transactions")
    op.drop_table("wallets")
    op.drop_table("payouts")
    op.drop_table("trigger_evaluations")
    op.drop_table("consensus_results")
    op.drop_table("telemetry_events")
    op.drop_table("trigger_rules")
    op.drop_table("policies")
    op.drop_table("weather_sources")
    op.drop_table("micro_regions")

