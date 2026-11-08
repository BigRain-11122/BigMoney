# DIGEST 2026-11-08 r1567 bm-b — E540: the published line is a statement anchor

**Card** E540 · **Study** `E540_line_pointer_distance` · **Face**
`results/state_tilt/LINEPOINTER-2026-11-08.json` (+ `linepointer_latest.json`) · **S6 leg**
`line_pointer` · **smoke leg** `# E540` · **selftest** 12 arms.

## Question

E398's census face publishes one row per read site and per write site of a bare `latest.json`, and
every row carries `file`, `line` and `expr`. E539 noticed in passing that the name inside the row's
evidence often does not sit on that line. This round asks the question directly: **what is that
line?** Is it the expression a consumer would land on, or a statement anchor above it?

## Method

1. Locate the published expression as an AST node of the file it names, comparing **node shape**
   (`ast.dump` without attributes), not text -- the row's line number and the file's line number
   are the two things that disagree, so a text match at the published line would beg the question.
2. Find the innermost `ast.stmt` holding it and the innermost function holding that statement, plus
   any loop header that encloses it.
3. Classify the published line against those spans (pure function, re-run by the gate on every row)
   and publish the signed distance.
4. Scan the corpus for sites that could consume a line pointer: reads of a `line` field (641),
   runtime source-position resolvers (488), and sites that name the census face (10).

## Readings

| anchor class | rows |
| --- | --- |
| the published line is part of the expression itself | 56 |
| the published line opens the statement that holds it | 1 |
| a continuation of that statement | 0 |
| a loop header above it | 0 |
| another statement in the same function | 206 |
| another statement in the file | 40 |
| expression not located | 1 |

Distance: median 12 lines, mean |distance| 13.34, range -68..+42; buckets 0:56 / 1-3:43 /
4-10:14 / 11-30:148 / 31+:42 (303 measured).

By tier the split is the answer to "what is this line for": `smoke_harness` 181 rows, **0** on the
expression line; `live_tooling` 45 rows, 13 on it; `scratch_or_estate` 11 rows, 10 on it. The audit
trail of a harness points at the open/read statement, not at the expression inside it.

228 of 304 published lines name **no** identifier from the expression at all (76 name at least one).
Example: `scripts/divlowvol_live_picks.py:301` publishes `prev = json.load(open(latest, ...))`
while the expression is on line 305.

No consumer reads these lines as values: 641 sites read a `line` field somewhere, 488 can resolve a
source position at run time, 10 name the census face -- but none ties a published line to a value
read. The pointer is a human-facing anchor.

## Two instrument lessons

1. **Shape matching beats text matching, but ambiguity must be published.** 48 rows publish an
   expression shape that occurs more than once in their file, so "nearest to the anchor" is an
   upper bound, not a resolution. Published as
   `rows_whose_expression_shape_appears_more_than_once_in_the_file`; its own follow-up card (E541)
   is to decide those rows by the rest of the row's evidence instead of by distance.
2. **"no span" is not "wrong anchor".** A row whose expression cannot be located is classed
   `no_node_for_the_published_expression_was_located` (or file-unreadable / line-outside) and is
   forbidden from carrying a distance -- the gate asserts it. Folding the unlocated row into
   "elsewhere" would have reported an instrument gap as a publication defect.

## How to apply

Before using any published location pointer, measure its distance distribution and publish what
statement the anchor opens. Before reading a published line as a value, ask what that line says.
