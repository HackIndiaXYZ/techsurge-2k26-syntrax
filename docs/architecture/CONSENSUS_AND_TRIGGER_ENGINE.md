# Consensus and Deterministic Trigger Engine

## Consensus rule - team design decision

The system uses exactly three enabled demo sources. Events are compared only when their `region_id`, `metric`, and `[window_start, window_end]` are identical. A reading must be accepted by basic validation before it may participate. The largest mutually agreeing group has absolute value difference of at most 5 mm. A group of two is quorum. The consensus value is the median of the group; any valid reading outside the group is retained as `SOURCE_DISAGREEMENT`.

## Approaches considered

| Approach | Fit for this MVP | Reason |
| --- | --- | --- |
| Majority vote | Useful for categorical accept/reject decisions | Does not itself give a rainfall value |
| Median | Selected for numeric rainfall | A single extreme reading cannot move the middle of a three-source group |
| Quorum | Selected at 2 of 3 | Allows one unavailable or rejected source while retaining an explicit no-consensus state |
| Weighted consensus | Not selected | Needs independently justified reliability weights; arbitrary weights would hide assumptions |
| Trimmed mean | Not selected | More useful with a larger source set; with three sources, median is easier to explain |
| Source reliability learning | Future optional analysis | Needs enough labelled historical data and governance; cannot silently override rules |

The Byzantine-fault concept is a useful lens for conflicting information, not an MVP certification. The classic problem concerns agreement among potentially faulty participants under specified communication assumptions; this prototype only demonstrates transparent tolerance of one discrepant input and makes no formal BFT claim. See the [original research record](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/).

| State | Meaning | Trigger consequence |
| --- | --- | --- |
| `PENDING` | Fewer than two valid distinct sources available | Do not evaluate as eligible |
| `ACHIEVED` | At least two sources agree | Evaluate matching policies |
| `NO_CONSENSUS` | Two or more readings exist but no group of two agrees | Record no-consensus evaluation; never pay |
| `EXPIRED` | Window is past allowed processing horizon | Never pay |

Range validation rejects a rainfall reading below 0 or above 400 mm in a 60-minute demo window as `IMPOSSIBLE_VALUE`; stale data is older than 10 minutes from `received_at`; a future observed time more than 2 minutes ahead is rejected. These are team thresholds chosen for simulation, not a weather-science guarantee.

## Trigger rule

The one recommended primary demo policy is rainfall: `consensus_value_mm >= 100` over the pre-agreed 60-minute window, for the policy’s region, during an active policy interval. The payout is INR 10,000 in a synthetic wallet. Other plausible parameters are temperature, drought and wind, but they add event-window and communication complexity without improving the required MVP proof.

```text
if policy.status != ACTIVE:            NOT_ELIGIBLE
elif policy.region != consensus.region: NOT_ELIGIBLE
elif policy.metric != consensus.metric: NOT_ELIGIBLE
elif policy already has payout:         ALREADY_TRIGGERED
elif consensus.state != ACHIEVED:       NO_CONSENSUS
elif now outside policy dates:          EXPIRED
elif consensus.value >= threshold:      TRIGGERED
else:                                   NOT_MET
```

The calculation must be a pure, versioned function of persisted policy and consensus records. An LLM must not alter window selection, data membership, threshold comparison, or payout decision.
