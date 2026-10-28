# DIGEST 2026-10-29 — E206: the producer half of a silent face (leaf-name growth gate)

Round: r1234 (bm-b). Watermark: RED at open (`pool-batch-runnable-idle-low-cpu`, py 1.7%,
pool ready 1 — the E205 card). Mission: burn the ready card.

## What E205 actually asked for, and what r1233 shipped instead

The E205 card in `results/runnable_pool.json` is the **leaf-set** growth gate: record every
face's delta numbers, diff against the previous window, fail when a new number lands in a face
whose text is still silent. r1233 shipped the **reader-map** ratchet (`SIGNGROWTH`) — a good
leg, but the other half of the question, and it left E205 `ready`. This round closes E205 by
building the card as written: mode `signleafgrowth`.

## Result

`results/e79/SIGNLEAF-2026-10-27.json` (seeded baseline `results/e79/SIGNLEAF-BASELINE.json`).

- 14 faces, 14 silent (E201's population, unchanged).
- **319** delta names recorded (list indices elided, so an extra era row is the same name).
- 0 grown, 0 shrunk, 0 born, 0 retired; verdict `no_delta_name_grew_inside_a_silent_face`, rc 0.

The gate fails (rc 3) on exactly two events: a silent face gaining a delta name the baseline
lacks, and a face born silent while already publishing deltas. Shrinkage is reported, never
failed — a face that retires a number is moving the right way.

## The blind spot, measured rather than admitted

The gate is a token test on the key name (`delta`/`diff`/`difference`), so it can only see deltas
spelled that way. The product publishes its own coverage:

- **629** numeric leaves carry a unit/sign token (`_bp`, `gap`, `wedge`, `spread`, `edge`) but no
  delta token;
- **140** of those are arm pairs (`engine_bp_raw` + `engine_bp_screened` = one level quoted
  twice), leaving **489** residue;
- residue by class: **208 anchored** (level quotes), **71 offset** (a gap under a constant — the
  only residue class that can plausibly carry a sign), **210 unclassified**.

So the token test is a **floor** on coverage, not a claim of completeness: at least 71 published
numbers could be differences the gate cannot name. That is the next card, not a defect in this one.

## The defect this round produced twice, and the live leg that caught it

Publishing the residue as `{"anchored": 208, "offset": 71}` put a **count** under a key the
family's own level-quote audit classifies **by name**: `level_quotes()` duly reported my face as
quoting an offset cell worth 71 "bp", and the live smoke leg L37 ("every quoting face has a
producer") went red because a face with three-digit count leaves has no bp producer.

Restructured to a list of records (`residue_by_class: [{"class": ..., "names": ...}]`) — and the
**same family of false quote appeared a second time** one edit later, when a count field was named
`of_which_arm_paired_levels`: the token `level` alone was enough for the classifier to read it as
one more anchored level cell. Now `unit_names_in_arm_pairs`, and L94 pins "no class-named numeric
key survives in this product".

## Verification

- `scripts/e97_routing.py selftest` **97/97** (legs L85–L94 added: leaf identity, index elision,
  clean/shrunk/born/seed cases, recall-gap accounting, no class-named numeric key).
- `python -m smoke_test` **124/124 PASS** (L37 live leg green again after the restructure).
- Gate run live twice: seeded then clean, rc 0 both times.

## Next

E207-COUNT-AS-QUOTE-AUDIT: scan every published face in `results/` for numeric leaves whose name
matches a measurement token but whose value is small-integer/count-shaped, i.e. quotes the
family's name-based classifier would fabricate — the class of defect this round walked into twice.