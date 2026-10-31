# r1192 bm-a -- does the commodity sleeve need a gate of its own? (NO_GATE, and the placebo is why)

Round: r1192, machine bm-a, 2026-10-31. Face: `results/etf_book_sleeve_gate.json`
(`scripts/etf_book_sleeve_gate.py`, selftest 18/18, `--check` recomputes every verdict).

## The question

r1191's next pointer had two halves: put the "whose CAGR is this" reading on the CARD as well
(page + ticket were done), and answer whether the commodity sleeve deserves its own risk gate.
The second half is not rhetorical: the sleeve pays (deleting it costs 3.71pp of CAGR) and
cushions (deleting it takes the drawdown from -11.8% to -22.3%), and the book-level vol target
already de-levers the whole book. So the only open question is whether a *sleeve-level* state
carries extra information.

## What was priced

Three gates, each applied through the concentration face's own mechanism (commodity score ->
NaN on gated decision dates; the engine substitutes on its own grid):

| gate | sleeve off | CAGR vs card | max drawdown vs card | verdict |
|---|---|---|---|---|
| sleeve below its own 200d MA | 20/83 (24.1%) | -0.32pp | -2.77pp | NO_GATE |
| sleeve vol > its own trailing p80 | 25/83 (30.1%) | +0.02pp | **+0.86pp** | NO_GATE |
| sleeve 10% below trailing peak | 13/83 (15.7%) | -0.18pp | -1.27pp | NO_GATE |

Reference arm (whole sleeve deleted, for the cross-face leg): -3.71pp CAGR, reproducing the
concentration face's published `leave_class_out.delta_cagr_pp` to 0.0pp on the same cutoff.

## The leg that decides it

Each gate gets a **dose-matched placebo**: the same number of off-decisions, spread evenly over
the grid instead of timed by the gate. Two of three gates *lose* to their own placebo (trend
placebo 10.69%/yr vs trend gate 9.28%; drawdown placebo 7.42%/yr vs drawdown gate 9.42% but
-15.5% vs -13.0% — both worse in at least one dimension), i.e. the causal-looking state is no
better than switching the sleeve off arbitrarily.

The vol gate is the only arm not explained by holding less sleeve: +0.02pp of CAGR, +0.86pp of
drawdown, and +5.00pp of drawdown better than its own placebo. It fails the **pre-registered**
1.0pp drawdown bar by 0.14pp. Frozen criteria do not move after the result, so: NO_GATE, vol
gate named as the re-test candidate on new data.

## Answer

**NO_GATE.** The sleeve's risk is already carried by the book-level vol target, which only
de-levers; a sleeve gate on top of it was, in two of three shapes, worse than holding the sleeve
less often. The one shape that survived the placebo leg missed its bar and stays a candidate.

## Also in this round (single implementation)

The "whose CAGR" block moved down into `etf_book_concentration.reading()`; the card is now the
third consumer (ticket r1190, page r1191) and the page's `concentration_face` is a delegate, so
the three faces format one implementation instead of three copies of the same assembly (E289
family; CARD.md section "Whose CAGR is this?", top-3 22.1%, delete-top-3 -1.99pp, delete sleeve
-3.71pp with the drawdown 10.5pp deeper).

Methodology card: E312.