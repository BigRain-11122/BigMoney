# E350 (r1371) -- the field, not the file, is what a hand edit touches

E346 counted 17 status fields that its own writer's next run branches on. E347 counted zero
operational gates reading a dated face. Both censuses counted *files*. This one counts *fields*.

Result face: `results/state_tilt/FIELDBRANCH-2026-11-01.json` (+ `fieldbranch_latest.json`),
producer `scripts/e350_field_branch_census.py`, selftest 20/20, verify re-derives 2289 fields /
5398 reads with 0 problems.

## What was measured

2343 in-repo `.py` sources (self source excluded). Two directions are followed so the census is
symmetric:

* **readers** -- 1632 variables bound by a load whose path folds to a `*.json` face;
* **writers** -- 876 variables that are built from scratch and handed to `json.dump(var, ...)`.

Every string-key `d["k"]` / `d.get("k")` on a face binding is a field read; its nearest
`if` / `while` / `assert` ancestor classifies the branch by its own body shape:

| class | rule | reads |
|---|---|---|
| `assert_guard` | the branch is an assert | 849 |
| `exit_guard` | the `if` body only raises / returns / continues / breaks | 60 |
| `choice` | the body works and/or the branch has an `else` | 1130 |
| `unbranched` | the value never reaches a branch | 3359 |

## Headline

* 2289 distinct (face, field) pairs, 5398 reads.
* 230 fields are read by a guard; **131 of them have no write anywhere in the corpus** -- a guard
  on a field nothing writes can only fire on a missing value.
* 728 fields reach a choice, 1130 choice sites. Largest *resolved* blast radius: 14 choice sites
  across 34 files on `results/gate_attrition.json :: entries`. The live state watermarks carry the
  same shape at smaller radius: `state-bm-c.json :: last_orders_sha` has 45 guards and 11 choices
  over 41 files, `last_decisions_sha` 43 and 11 over 40.
* 803 fields sit on a basename-only face key (their path would not fold past the file name). They
  are published as a bound, not ranked, because `meta.json` (66 files) and `attr.json` are not one
  face -- the first draft credited `attr.json :: entries` with 21 choice sites by merging a dozen
  unrelated files.

## Defects found and fixed in-window

1. **Basename keys merged distinct faces.** Fixed by keeping the path from the first known root;
   a selftest leg pins that `results/x/meta.json` and `data/y/meta.json` are two faces.
2. **Following only load bindings called 2018 of 2212 fields "never written"** because producers
   build the dict themselves. Adding the dump sink moved it to 1698 of 2289 and the unwritten-guard
   headline from 180 to 131 -- the census was measuring its own filter in the opposite direction.
3. **`parents_of` keys nodes, not `id(node)`.** The first `_nearest_branch` looked up `id()` and
   classified every read as unbranched; three selftest legs failed and named it.
4. **Self-inclusion one level up.** The smoke runner is itself a new `.py` source, so the face has
   to be rebuilt after the runner lands; verify then re-derives the same 2343.

## Bound

A load call whose path this resolver cannot fold (a handle opened outside a `with`, a
`Path.read_text()` chain) contributes no field rows: 3235 such bindings are counted beside the
1632 that resolve. Branch class is read from the body shape, so an `if/elif` chain that sets a
`blocked` flag and falls through is published as a choice, not a guard.

## Why it is a product, not bookkeeping

The face names the fields a single hand edit moves, per field, with the guard/choice split and the
counterfactual (`written` false = the guard can only fire on absence). That is a review checklist
for any status or watermark edit, regenerated deterministically from the tree.