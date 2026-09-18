# PS-F03 User Journeys

**Settlement journey:** The dashboard shows an active policy. Sources submit readings. Each event is validated and grouped into a 60-minute bucket. A consensus result appears with its source members. The trigger engine records the threshold comparison. If eligible, a payout is initiated once, the synthetic wallet balance changes, and the audit timeline shows every causal step.

**Failure journey:** The operator selects “corrupted source.” The dashboard labels the outlier rather than hiding it. Selecting “retry payout” replays the same instruction key, shows an idempotent result, and leaves the wallet balance unchanged after the original credit.
