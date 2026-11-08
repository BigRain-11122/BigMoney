# DIGEST 2026-11-08 r1567 bm-b — E539: a class label priced against its own evidence row

**Study**: `scripts/e539_label_vs_evidence.py` (selftest 17/17) · **Face**:
`results/state_tilt/LABELVSEVIDENCE-2026-11-08.json` (+ `labelvsevidence_latest.json`) ·
**Card**: E539 · **Pool**: E539 done, E540 seeded.

## Question

E398 publishes a census of every read and write site of a bare `latest.json`. Each row carries a
`class` naming where the family directory came from **and** an `evidence` object naming the exact
expression / constant / binding. E538 priced four rows as `family_stated_at_the_site` while their
family came from an imported constant resolved three functions away. Does that happen in 4 rows or
in a class?

## Reading (population = all 304 rows: 237 read sites + 67 write sites)

| leg | result |
|---|---|
| rows whose label agrees with their own evidence | **275 / 304** |
| rows whose label contradicts their own evidence | **29** |
| — of which `family_stated_at_the_site` whose family is a *name*, not a literal at the site | **29** (4 imported constant + 20 module constant + 5 local binding) |
| — of which any other bucket (not supplied / carried / no evidence / off vocabulary) | **0** |
| stated rows whose how is a literal at the site | 195 (185 "literals build the directory" + 10 "a literal component names it") |
| signature rows published without a default (`default_expr == "None"`) | 27 (a measurement, not a charge) |
| source leg: name on the exact published line / within ±3 / elsewhere in the enclosing function / elsewhere in the file only / nowhere in the file | 53 / 47 / 158 / 36 / **0** |
| readers of a class label in `.py` outside `results/` | 9 sites in 4 files, of which **1 branches on it** (`scripts/e403_family_arg.py:535`) |

The 29 rows sit in **24 files**, **17 of them in the `live_tooling` tier** — the tier that decides
what the live pipeline reads. `Money02/live_pull.py:12`, `live_view.py:16`,
`preflight_data.py:58` and `:59` are the four E538 priced; the rest are the same shape at lower
reach.

## Two instrument lessons

1. **A published absence is not a published value.** E398 writes `default_expr` on every signature
   row; rows whose parameter has no default carry the four letters `None` there. Reading key
   presence, or truthiness of the string, invented a 27-row class ("signature rows with no default
   published") that was entirely my own defect — the label `family_required_by_the_signature` is
   *consistent* with having no default. The gate now names the sentinel (`present()` returns False
   for `None`, `"None"`, `""`, `"null"`, `"na"`, quote-pairs) and the 27 rows are published as a
   measured count instead of a charge.
2. **A published `line` is a statement anchor, not the expression line.** The source leg first
   charged 194 of 294 rows with "the line does not carry the name". Reading the source shows the
   pointer lands 4–30 lines from the expression — for `Money02/preflight_data.py:58` the expression
   is on line 59, for `scripts/e235_charge_granularity.py:683` it is on 681. Under a four-rung
   ladder (exact → ±3 → enclosing function → file) the charge falls to **zero**: the name is always
   somewhere in the file. So the honest reading is not "the labels are wrong about the source" but
   "the pointer granularity is unmeasured" — that residue is E540.

## Verdict (gate-recomputed)

```
at_least_one_published_label_disagrees_with_its_own_evidence_row_or_with_the_line_it_points_at
```

## Method limits

- the source leg looks for the last dotted component of the name the evidence row carries; a line
  that spells the same name differently (`getattr`, a loop variable) reads as a coarse pointer;
- a literal-hows row is checked by its last family component, not the whole path;
- the reader leg counts class literals and calls a line a branch when it carries a comparison or
  conditional token; it does not type-check which value is compared;
- the face is read as published on disk at its own cutoff; nothing upstream is rebuilt.