# DIGEST 2026-10-30 r1163 bm-a — three atlas arms judged on the atlas's own ruler

Face: `results/etf_book_phase_atlas_arms.json` | prose: `research/ETF_BOOK_PHASE_ATLAS_ARMS.md` |
card: `knowledge/METHODOLOGY_ASSETS.md#E259` | runner: `scripts/etf_book_phase_atlas_arms.py`
Arm faces: `results/etf_book_phase_atlas_buffer_k05.json`, `..._cost05.json`, `..._cost20.json`

## The question

r1350 (bm-c) priced the production cell grid on every decision origin of its own cycle and found the
between-cell spread (5.22pp) sitting inside the median cell band (6.68pp). It left three follow-ups
in the runnable pool, unclaimed: re-price the buffer arm and bracket the toll.

That matters because **r1325 rejected buffer k=0.05 on a −0.145pp median taken from five books on a
single decision calendar**. If the ruler for a cell is a 2.2–12.6pp band, a 0.145pp effect was never
a measurement — the REJECT may have been right for the wrong reason, or wrong outright.

## What was run

Three arms of `scripts/etf_book_phase_atlas.py`, claimed from the pool (bm-a r1163), 280 engine runs
each, 8 ProcessPool workers, all three rc0 on cutoff 2026-10-29:

| arm | args | wall |
|---|---|---|
| buffer k=0.05 | `--k=0.05` | 92.4s |
| 5bp/side | `--cost=0.0005` | 87.2s |
| 20bp/side | `--cost=0.0020` | 80.7s |

`scripts/etf_book_phase_atlas_arms.py` reads the four published faces and applies one frozen rule
(echoed into the payload); 19 selftest legs, including a baseline-reproduction leg (N5/R20 median
must equal the published 9.13pp — it does, 9.130) and hand-made arms that must read ADOPT / REJECT /
NOT-SEPARABLE / NOT-ASSESSED.

## Reading

**1. The buffer REJECT survives, but as a direction, not a size.** 12/12 cells judged; not-worse
share 0.667 (floor 0.80); median per-cell delta **−0.030pp**; **0/12 cells resolve** — no cell's
delta exceeds its own band (smallest band 2.19pp, largest 12.57pp). So the honest sentence is
"the buffer does not pay", not "the buffer costs 0.145pp": at this design the effect is two orders
of magnitude under the ruler, and both a −0.30pp and a +0.40pp reading are available on the same arm
depending on which cell you look at.

**2. The cadence conclusion is not a cost artefact.** Band by cadence stays put across the toll:

| face | R10 band | R20 band | R40 band | R40/R10 | median band |
|---|---|---|---|---|---|
| baseline 10bp | 3.407 | 6.711 | 8.980 | 2.64 | 6.68 |
| 5bp | 3.465 | 6.772 | 9.000 | 2.60 | 6.91 (+0.9%) |
| 20bp | 3.293 | 6.600 | 8.948 | 2.72 | 6.77 (−1.7%) |

Doubling the toll moves the median band by −1.7%; halving it moves it by +0.9%. **The band is a
property of the decision count, not of the toll.** That converts r1350's cadence reading from "true
at 10bp" to "true independent of the toll we charge", which is what a path-dependence claim needs.

**3. What the toll arms are not.** At 5bp every cell earns more (+0.712pp median, share 1.000) and at
20bp every cell earns less (−1.410pp, share 0.000) — but **0/12 cells resolve at either level**. The
cost saving is mechanically certain and smaller than the phase noise, so it cannot license a config
change; it only says the incumbent cell is not being rescued by a cheap-toll assumption.

## Bugs found on the way

`--out` accepted a repo-relative path and then died in `Path.relative_to(ROOT)` **after** the full
280-cell run (a whole arm's compute thrown away, exit 1, no face written). Fixed in
`scripts/etf_book_phase_atlas.py` by resolving a relative `--out` against ROOT. Disclosed gap: the
fix carries no selftest leg of its own yet (the face's 12 legs do not exercise the write path), so a
future edit could reintroduce it silently.

## Honest limits

- Descriptive only: no judgment line was moved, no cost model changed, no ledger booking.
- The arms inherit the production panel's survivorship and its eligibility burn-in; nothing here
  re-validates the panel.
- The 12 cells share one 2020+ window, so "band" is measured inside one regime, not across regimes.
- Not wired into the S6 chain: the arms face is a point-in-time reading of three published faces
  (0.04s to rebuild), not a daily product.

## Cost

3 × 280 cells ≈ 4.3 min wall on 8 workers, BelowNormal priority; the analysis itself is 0.04s and
zero network.