# E96 — the churn LEVEL faces do not say which screen arm produced them

- **When**: 2026-10-27T04:2x (+08:00), bm-b r1163
- **Face**: `results/e44_midmonth/LEVEL-LABELS-20261027.json`
- **Tool**: `python scripts/e96_level_label_audit.py run` (selftest 22/22)
- **Promise audited**: r1158 round report — "every published churn LEVEL says which screen arm produced it"

## What was measured

The audit scans `results/e44_midmonth/*.json` and separates two shapes:

- **LEVEL faces** — top-level `eras` mapping era → `{me, mid, gap_*}` blocks (the published churn levels);
- **arm siblings** — top-level `eras` mapping *arm* → era → block (`MIDSCREEN`, `SCREENGAPERA`, …).

Every LEVEL face is then classified three ways: **declared** (its own `spec` names its arm),
**inferred** (its cells are bit-identical to a named arm of a sibling face), or **inferred_nearest**
(not identical, but one arm dominates the runner-up by ≥10× on max abs difference at full coverage,
with the residual published as `drift_bp`). Anything else stays **unlabelled**.

## The answer

Only two faces on disk carry published churn LEVEL cells, and **neither declares its arm**:

| face | state | arm | evidence |
| --- | --- | --- | --- |
| `MID-20261020.json` | `inferred_nearest` | `unscreened` | drift **8.3bp**, runner-up (`drop`) **195.2bp** → margin **23.5×** |
| `MID-20261020-s20180101.json` | `unlabelled` | — | best coverage only **0.854**; nearest (`unscreened`) 69.0bp, runner-up 195.2bp |

So the r1158 promise is **not met on disk**: 0 of 2 declared, 1 inferable with a caveat, 1 not
inferable at all.

Two findings the bare promise would have hidden:

1. **The nearest-arm match is not an identity.** The base face reads like `unscreened`, but it was
   burned on the 2026-10-20 cutoff and the labelled sibling re-derived it on 2026-10-21, so the same
   arm differs by **8.3bp** across the two burns. That is small beside the arm gaps (195–241bp) and
   therefore enough to name the arm, but it is not zero and must not be quoted as "identical".
   Publishing only "arm = unscreened" would have made a reburn look like a label.
2. **A different window start cannot borrow a label.** `MID-20261020-s20180101.json` populates the
   `2017_2020` era that the 2020-start sibling never burned, so its coverage against every arm is
   0.854 and no inference is possible. The honest state is *unlabelled*, not "probably unscreened
   too" — a wider window is a different experiment, and none of the four arms covers it.

## Why the fix is an index, not a rewrite

Published faces are frozen evidence: rewriting `MID-20261020.json`'s `spec` would change the record
that r1158 and E57/E80 quotes rest on. The repair instrument is therefore this audit face — a
machine-readable label index that a consumer can join against, plus the rule that a *new* level face
must carry its arm in `spec` at burn time.

## Next

- `E97-READSET-TRIAGE-ROUTING` (routing table for the 25 charged modes) and `E98-ENDCHOICE-ALLERAS`
  remain ready.
- New `E99-LEVEL-LABEL-START2018`: burn the start-2018 LEVEL twin against declared arms so the second
  published level stops being unlabelled — the only way to label it is to re-derive it with the arm
  recorded.