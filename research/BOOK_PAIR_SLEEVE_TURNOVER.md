# BOOK_PAIR_SLEEVE_TURNOVER

Q: How much of the sleeve's own premium reading is which 20 bonds the rule happens to hold, rather than how expensive they are?

Verdict: **THE_SWAP_ALONE_CAN_CHANGE_THE_BUCKET**

## Mechanism

The sleeve ruler is a median over 20 bonds. A re-pick holds on to roughly 
%s of them and swaps the rest, so the ruler's next reading is taken over a 
partly different basket. This face prices that basket change on one date: 
the same 20 before the swap and the same 20 after, both read on the swap 
date. Anything the market did cancels out, so what is left is membership.


## Numbers

- median |churn| **2.30 pp**, p90 **5.98 pp**, max **13.63 pp**
- ordinary (non-swap) day: median **0.78 pp**, p90 **2.71 pp**
- ratio churn/ordinary **2.94**; biggest swap is **5.04x** an ordinary p90 day
- month ends within 10 bars of a swap: **52**, of which a bucket changed: **16**
- today: reading **11.420%**, nearest edge **2.17 pp** away, swap p90 **5.98 pp** → inside the swap step: **yes**

## How to use it

Two sentences a reader can act on. First: when a label is decided within a 
couple of weeks of a re-pick, the reading it is decided on carries a step 
that no market event produced — the table above says how big that step is 
in the units the reader already knows (pp of premium). Second: if the reading 
sits closer to an edge than that step, the label could have gone the other 
way for reasons that are not about expensiveness at all.


## What is not measured

- membership is rebuilt from the parent's pick formula because neither parent publishes its holdings; the 1e-9 reconciliation only proves the two implementations agree, not that either equals the traded book
- the counterfactual reading drops bonds that delisted since the swap, so a swap that saved a defaulted name flatters the pre-swap side in those months
- a tertile label is a coarse ruler: a reading that moves 3pp inside the mid bucket is invisible to this face even though it is the same 3pp the desk sees
- churn_pp is a median-of-medians: two sets of 20 with the same median can differ in every bond, so this is a lower bound on membership noise
