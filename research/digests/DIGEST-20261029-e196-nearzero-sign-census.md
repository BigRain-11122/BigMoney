# E196 — the printed sign is a rounding fact wherever the level is a hair against its gap

Date: 2026-10-29 | round r1228 (bm-b) | dept: research | card: E201 → `knowledge/METHODOLOGY_ASSETS.md`
Face: `results/e79/NEARZEROSIGN-2026-10-27.json` (producer: `scripts/e97_routing.py nearzerosign --publish`)

## 1. The question, stated before the sweep

E195 read the full-era `sh510050` drop as a *reversal*: an additive level of **+0.07bp**
against a compounded gap of **-38.20bp**. That is not a small direction — it is no
direction. The sign of the additive reading is decided by rounding scale.

So the question is not "how big is the level", it is **"for every published pair of an
additive level and a compounded gap in this family, is the printed sign big enough next
to the gap it is told apart from to be quoted?"**

Two floors were declared *before* any cell was read (they are constants in the source):

| floor | value | meaning |
|---|---|---|
| `NEARZERO_RATIO_FLOOR` | 5% | `|level| < 0.05 x |gap|` -> **sign_is_hair**: the printed sign must not be quoted |
| `NEARZERO_GAP_FLOOR_BP` | 1bp | `|gap| < 1bp` -> **level_agrees**: no gap to speak of, no sign question |

Third class, by elimination: **sign_quotable**.

## 2. The sweep

Schema-driven, not face-listed: walk every `results/**/*.json`, take every dict that
prints **both** an additive level (`arith_bp`) and a compounded gap (`comp_bp`). The
sweep therefore covers the family plus anything else that prints both numbers, and it
cannot silently miss a face added later.

**164 cells across 3 faces** (LADDERDROPCURVE 132, LADDERDROPRULE 28, LADDERDROPCROSS 4).

| class | cells |
|---|---|
| sign_quotable | 157 |
| **sign_is_hair** | **6** |
| level_agrees | 1 |

`|level|/|gap|`: median **1.153**, min **0.001946**, max **53.5**.
Of the **51** cells where the two readings point opposite ways, **44** carry a level big
enough to be quoted and **6** do not.

## 3. The six hairs, verbatim

| face | path | level_bp | gap_bp | lambda |
|---|---|---|---|---|
| LADDERDROPRULE | `/full/drops/0/base` | 0.074333 | -38.198705 | 0.001946 |
| LADDERDROPCURVE | `/full/drops/0/base` | 0.074333 | -38.198705 | 0.001946 |
| LADDERDROPCURVE | `/full/drops/0/curves/first/steps/0` | 0.074795 | -38.435733 | 0.001946 |
| LADDERDROPCURVE | `/full/drops/0/curves/first/steps/1` | 0.075262 | -38.675666 | 0.001946 |
| LADDERDROPCURVE | `/full/drops/0/curves/first/steps/2` | 0.075736 | -38.913351 | 0.001946 |
| LADDERDROPCURVE | `/pre2017/drops/1/curves/last/steps/5` | 1.408800 | -51.432962 | 0.027391 |

The lambda of the first five is **identical to six digits**: level and gap scale
together along the curve, so "the sign is a hair" is a property of the *pair*, not of a
particular step. The face also publishes
`gap_needed_for_quotable_bp = |level| / 0.05` — for the full-era pair that is
**1.49bp**: the gap would have to shrink by a factor of 25 before the +0.07bp level
could be read as a direction against it.

## 4. The hair can be on either side

The single **level_agrees** cell is `LADDERDROPCURVE /full/drops/0/curves/last/steps/4`:
level **27.99bp**, gap **-0.523bp**. Its signs disagree, and here it is the *gap* that
is the rounding artefact — 0.52bp of compounded difference is not a quantity anyone
should quote. So the floor is symmetric: `hair_side` is published per cell (`level` /
`gap` / null), and the face reports `cells_where_the_gap_is_the_hair = 1`.

A sweep that only asked "is the level small?" would have called this cell a clean
reversal and been wrong in the other direction.

## 5. What a reader should take away

1. **Do not quote the printed sign of the full-era `sh510050` drop.** It is +0.07bp
   against a -38.20bp gap; the direction is rounding. E195's "survives edge trimming"
   reading of this pair survives as a statement about *which months are removed*, not as
   a statement of direction.
2. **157 of 164 cells are quotable** — the family is not poisoned, it is locally
   defective at four distinct pairs (six rows, two of them the same pair printed twice).
3. **The defect costs zero bp and a whole sign.** Nothing in the arithmetic changes;
   what changes is what a reader is allowed to say.

## 6. Honest limits

- The floors are declared constants, not fitted; a reader who prefers 10% gets a
  different list, and `level_over_gap` is published per cell so they can rebuild it.
- Two of the six rows are the *same pair* published by two faces (RULE and CURVE); the
  identical lambda is the tell.
- Cells that print a level and no gap (or a gap and no level) are outside the sweep's
  reach by construction; they answer no sign question and are not counted as clean.
- This is a reader-facing audit: zero engine change, zero judgment change, no face was
  rewritten. It publishes what the family prints and what may be quoted from it.

## 7. Pits captured this round

`evidence_cutoff` is not a date field everywhere — a status face carries
`"panel 2026-10-14 (bars 10-15 due 15:30)"`, and a lexicographic max over that text
beats every real date, so the first publish wrote
`NEARZEROSIGN-panel 2026-10-14 (bars 10-15 due 15:30).json`. The cutoff is now derived
only from contributing faces **and** validated against `^\d{4}-\d{2}-\d{2}$`; leg L58
pins it. Second pit: the new face made L37 red by appearing as a quoting face with no
producer — a new published face must be added to `LEVELQUOTE_EXCLUDE_STUDIES` in the
same edit that creates it.