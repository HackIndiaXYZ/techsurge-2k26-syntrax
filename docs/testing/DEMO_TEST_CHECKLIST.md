# Demo Test Checklist

- Reset to the known synthetic policy and wallet balance.
- Verify three sources, threshold, window, and `SYNTHETIC` labels are visible.
- Run corrupt-source preview; show rejection reason and audit evidence.
- Run clean trigger; verify 101/102/103, consensus 102, trigger and one wallet credit.
- Run payout retry; verify same payout/transaction and unchanged post-payout balance.
- Show T0/T1/T2 metric and trial count, not invented target numbers.
- Show basis-risk limitation and no-real-money statement.
- Keep a local seeded fallback ready if deployment is unavailable.
