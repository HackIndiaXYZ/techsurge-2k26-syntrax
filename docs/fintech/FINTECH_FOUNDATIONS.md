# Parametric Insurance Foundations

**Insurance** transfers specified financial risk from a policyholder to an insurer in exchange for a premium. A **policy** defines who is covered, for what period, what condition matters, and what payment may be due. A **claim** in traditional indemnity insurance requests payment after a loss; an assessor commonly verifies the loss and amount.

**Parametric insurance** instead pre-agrees an observable parameter, such as rainfall in a window. If the trusted measurement satisfies the trigger, the stated payout is due without estimating each person’s loss. It can settle faster, but it introduces **basis risk**: the parameter can be crossed without the individual suffering loss (false trigger), or a real loss can occur without the parameter crossing (missed trigger).

In PS-F03, a **policyholder** owns a synthetic policy. The **coverage** is the predefined rainfall condition, not a promise to cover all flood damage. The **premium** is not modeled because the prototype begins with an active synthetic policy; no underwriting or real insurance sale occurs. **Settlement** is the simulated completion of a triggered payout. **Zero-touch** means no manual claim or adjuster is needed after the predefined, deterministic rule is met.
