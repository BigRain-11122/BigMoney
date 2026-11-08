# DIGEST 2026-11-08 r1568 bm-b — E541: can a row's own evidence pick among shape-identical nodes?

**Card** E541 · **Study** `E541_branch_ambiguity` · **Face**
`results/state_tilt/BRANCHAMBIGUITY-2026-11-08.json` (+ `branchambiguity_latest.json`) · **S6 leg**
`branch_ambiguity` · **smoke leg** `# E541` · **selftest** 26 arms.

## Question

E540 located the expression a census row publishes by AST node shape and, when the shape occurred
more than once in the file (48 of 303 located rows), took the nearest to the published line. That
pick is an upper bound on resolution, not a resolution. This round asks the census row to choose:
**do the fields the row already carries name the occurrence, and does E540's rule land on the node
the evidence names?**

## Method

The 48 ambiguous sites are rejoined to the census row that published the same file+line+kind (48/48
rejoin uniquely, no disagreement on function or constant). For every site the same-shape nodes are
recomputed from the file at its own cutoff and addressed as `(lineno, col_offset)`. Four constraints
the row already carries are then applied conjunctively, in order:

1. **TEXT** — the candidate's source segment equals the published expression text (whitespace
   normalised; node text cut from a per-file byte line cache, never `ast.get_source_segment` per
   node, which re-splits the whole file on every call).
2. **TEXT_RENDERED** — the same comparison with whitespace and quote style dropped.
3. **FUNCTION** — the candidate sits in the function the census row names.
4. **CONSTANT** — the candidate's segment carries the constant the census row names.

An arm that would reject **every** surviving candidate is refused for that row and published as
refused: that is evidence the arm is miscalibrated for the row (the census line can sit in another
function, as E540 measured), not evidence about the node. Then E540's rule is recomputed verbatim
(innermost function of the published line first, then `min by (|lineno − published|, lineno)`) and
compared with the node the evidence kept.

`family_dir` and `class` are not arms: `family_dir` is a normalised directory no site spells, and
`class` says how the family was attributed, not which node was read.

## Readings

| | rows |
| --- | --- |
| ambiguous sites (population) | 48 |
| candidate nodes | 118 → 89 after the arms |
| decided by the evidence | 16 (all by FUNCTION) |
| left ambiguous (2 survivors: 23, 3 survivors: 9) | 32 |
| E540's nearest rule lands on the decided node | 16 of 16 |
| ambiguous rows where the nearest node is inside the surviving set | 32 of 32 |

Per arm: TEXT applied on 2 rows and was **refused on 46**; TEXT_RENDERED applied on all 48 and
narrowed **none**; FUNCTION applied on all 48 and narrowed 16; CONSTANT applied on 5 and narrowed 0.

By tier the ambiguity is not evenly spread: of the 15 `live_tooling` rows 13 decide (the tier that
decides what a live face reads), while of the 25 `smoke_harness` rows **24 stay ambiguous** — the
same fixture path is spelled identically in several test bodies, so "nearest to the anchor" there is
an arbitrary pick among copies of the same string.

## Two instrument lessons

1. **A published expression is not the source text.** The census renders `expr` through a
   re-serializer: string literals come back single-quoted while the sources use double quotes, so
   the strict text arm matched no candidate at all on 46 of 48 rows. Read alone that looks like
   "the row carries no text evidence"; the truth is that the text was re-rendered. Both arms are
   published separately so the refusal is never read as absence — and the rendered arm's answer is
   itself the finding: where shapes are identical, text narrows **nothing** (0 of 48).
2. **A rule can be admissible without being resolvent.** E540's nearest pick agreed with the
   evidence on every row the evidence could decide (16/16) and never landed outside the surviving
   set (32/32), yet it also never resolved the 32 rows the evidence could not: 73 extra candidates
   remain, and on the harness tier the "nearest" node is one of several identical copies. Agreement
   with the evidence is a soundness reading, not a resolution count, and the two must be published
   apart.

## How

Before treating a location field as a pointer, ask what could distinguish the candidates and price
each signal's *narrowing* rate, not just whether it applies: here text applies 48 times and narrows
0, the function applies 48 and narrows 16. And when a field is compared against source, first check
that the field is source text at all — a re-serialized expression will fail a strict comparison on
nearly every row and silently look like a missing signal.

Correct body = `scripts/e541_branch_ambiguity.py` (run/check/verify/selftest 26 arms) + face
`results/state_tilt/BRANCHAMBIGUITY-2026-11-08.json` + `branchambiguity_latest.json`; S6 leg
`branch_ambiguity`; smoke leg `# E541`; card `knowledge/METHODOLOGY_ASSETS.md` E541.