# E188 — the label duty: the two readings are one number plus the fee, and only the audit face says which

Date: 2026-10-28 | round r1222 | machine: bm-b | dept: research
Face: `results/e79/LABELDUTY-2026-10-27.json`
Tool: `scripts/e97_routing.py` mode `labelduty` (selftest 40 -> 48)
Upstream: E185 (`results/e79/LEVELWEDGE-20261027.json`), E176 (`TILT3SIGNBOOKSPLIT`), E177 (`TILT3SIGNDECOMOFFSET`)

## What was asked

E185 located the E180 wedge as the turnover fee, which turns a bug hunt into a labelling
duty: if `decomposition_engine_bp` is published gross of the fee by one face and net of it
by another, every face that quotes a level or an offset off that cell is quoting either a
gross or a net number without saying which. Sweep the family, classify each face, then
re-state one decided verdict under the other stance so "the label changes nothing" is
measured rather than assumed.

## What the measurement says

10 cells publish this number in both stances (5 eras x raw/screened).

- gross minus net equals the published rebalance fee to **0.0050 bp** worst case — the two
  faces are one number plus a fee, not two calculations.
- The label alone moves the level by **1.129% .. 12.187%** of its own value. The wide end is
  2024_now (31.2982 gross vs 27.8998 net), where a 3.40bp fee sits on a 28bp level.
- **No cell changes sign** with the stance (0/10). So the label changes sizes, never
  directions — which is exactly why a sign-only reading never noticed it.
- **10/10 published offsets are the same construct with the fee between them**: E176's
  `decomposition_level_offset_bp` and E177's `level_offset_bp` differ by the fee on every
  cell (2.97 / 3.58 / 3.59 / 3.48 / 3.38 bp on pre2017 / 2017_2020 / 2021_2023 / 2024_now
  / full, raw arm).
- **4 cells quote an offset no wider than their own fee** (inside the wedge):
  2021_2023 raw −1.1442 net / −4.77 gross (fee 3.6208), screened −2.0866 / −5.67 (fee
  3.5823), full raw 6.1325 net / 2.78 gross (fee 3.357), full screened 5.2868 / 1.95 (fee
  3.3327). A verdict that says "the decomposition sits ~2bp under the published level" is
  quoting a number the label can double.
- Deltas are **not** exempt, they are merely smaller: a delta built from the two readings
  shifts by `fee_raw − fee_screened` = 0.0 / 0.0 / 0.0385 / 0.0754 / 0.0243 bp. Deltas
  built from published levels are fee-free by construction.

## The defect this finds

The family sweep over `results/e43_tilt_4member` + `results/e79`:

| face | publishes | its own text says |
|---|---|---|
| TILT3SIGNBOOKSPLIT | gross (10 cells) | nothing |
| TILT3SIGNDECOMOFFSET | net (10 cells) | nothing |
| TILT3SIGNDROPSWEEP | gross (10 cells) | nothing |
| LEVELWEDGE (the E185 audit) | both, by design | both |

The label exists — but on a different file from the numbers. A reader who copies the JSON
that publishes the cell never sees it; the only page that says which stance it is happens
to be the audit that discovered the wedge. That is the finding: not "an unlabelled number",
but "the label lives away from the object".

## Transferable rules

1. **A label duty is a sweep, not a fix.** Once one face is found publishing a gross number,
   every sibling that consumes the same cell is a candidate — and the sweep is cheap because
   the two stances differ by a published term you can join.
2. **Classify a face by what it publishes against what it declares, in four states** —
   labelled, unlabelled, mixed (one label, two objects), mislabeled (declares one, publishes
   the other). Takes a value-match against the stance ladders plus a token scan of the face's
   own text, and the slug is excluded: a face called `..._gross_...` is an identifier, not a
   claim.
3. **Report the margin in fees, not in bp.** "Offset 2.10bp, fee 3.58bp" is a decision a
   reader can act on; "offset 2.10bp" beside an unlabelled gross/net pair is not, because the
   same cell has another legitimate value 170% away.
4. **A sign test is not the safety test.** Zero flips out of ten cells looks like immunity and
   is actually the mechanism by which this error survives review: the stance never reverses a
   verdict, it only changes the number the verdict quotes.