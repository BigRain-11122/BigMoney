## E336 -- a repository-wide price is not a decision: price one consumer at a time, twice, and refuse to name the cheapest when the two yardsticks disagree

E334 priced the helper repair for the whole repository (6 faces / 37 numbers). A reader cannot act on that
number: the question anyone actually has is "may I move ONE study onto the landed tokenizer reading, and what
does it cost me". This study ranks the six E334 consumers by that price and ranks them **twice**, because there
are two different quantities a consumer could be charged for:

- **reading A (delta)** -- shipped build vs tokenized build: how much of the consumer's own answer *is* the
  helper's defect. Counts: E331 8/30, E329 8/17, E328 6/13, E327 4/23, E326 3/18, **E330 0/21**.
- **reading B (publish)** -- the consumer's *published* face vs the tokenized build: what a reader has to re-read
  today if the consumer opts in. Counts: E328 9/13, E331 9/30, E329 8/17, E326 6/18, E327 4/23, **E330 1/21**.

E334's published delta re-derives **6 of 6 rows**, so both readings are measurements of the same corpus, not two
different datasets. Totals agree with E334 (29 numbers move under the delta; 37 published numbers would need
re-reading across 6 faces).

**The answer this study is allowed to give.** Both readings put `E330_unpinned_choice` first (0 delta numbers, 1
published number, verdict intact) -- but they swap `E328` and `E329` at positions 3/4, so the full orders are not
the same and the verdict **refuses to name a candidate**: the cheapest name here is a property of the yardstick,
not of a consumer. Four of six positions are stable; the head is one of them, so the face publishes the head as a
**floor** (E330 and E326 are the two cheapest on any reading) while refusing to hand out a ranking. `E327` is last
on both readings for the only reason that outranks a count: **its published verdict does not survive the switch**.

Two reusable rules came out of writing it. (1) **A per-consumer price needs two readings, not one.** The delta
says how wrong the study is; the publish reading says how much of its published answer stops being true. They are
not monotone in each other (E326 has 3 delta numbers but 6 published, E328 6 but 9) and a ranking built on either
alone silently answers a question nobody asked. (2) **Order stability is a property of the whole order.** A head
that agrees on both readings hides swaps beneath it; checking only "is the cheapest the same?" would have named
E330 as a *ranking* when only its *floor* is stable. Both flags (`orders_agree`, `cheapest_agrees`) are published
beside the orders so a reader can see which one failed.

Evidence: scripts/e336_consumer_optin_ranking.py (selftest 20/20, verify 0 problems) -> results/state_tilt/OPTINRANK-2026-11-01.json -> research/digests/DIGEST-20261101-r1356-e336-consumer-optin-ranking.md -> Tools/s6_chain_bmb.py leg consumer_optin_ranking -> smoke_test.py leg E336