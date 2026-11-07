# DIGEST-20261107-r1513-e488-writer-directory

**Round:** r1513 bm-b (dept=research+engineering) · **Study:** E488 · **Face:** `results/state_tilt/writerdir_latest.json`

## Question carried in

E487 (r1512) traced 67 of the 84 `*_latest.json` spellings that no source writes as a literal back
to a writing source, then split the traced ones by whether the writer path reached the directory the
reader resolves to: 1 same, **51 bare basename (directory untraced)**, 15 a stated but different
directory. A bare-basename class is an unfinished trace.

## What was measured

For each of the 51 rows, every tracing source's module AST was folded over its directory-shaped
constants (literal / assignment chain / `os.path.join` / `a + b` / `dirname(...abspath(__file__))`
with one up-step per `dirname` / one hop into a repository module imported under an alias) and the
folded paths were compared with the directory the reader resolves to.

## Headline

**50 of the 51 basename-only writers name the reader's directory (`results/state_tilt`) from their
own module constant.** 0 ancestors, 0 other directories, 1 unfoldable (`e365_face_population_pin`
folds `STORE_DIR = os.path.join(OUTDIR, "face_store")` where `OUTDIR` is a function parameter),
0 modules with no directory expression. Parent population reproduced 51/51.

So E487's "51 directories untraced" was **tracing depth**, not a wrongwriter population: at this
depth the number of basename-only writers that write somewhere else is zero.

## Two things that would have made this face lie

1. **A 4-hop budget printed 16 rows as "the module states no foldable directory"** while the real
   shape is an alias chain (`e453 -> e452 -> e447 -> e446 -> ...` re-exporting `OUTDIR`). Raising the
   budget to 12 hops folded 15 of those 16 immediately. A hop budget that is too small does not
   publish "the chain is long", it publishes "the module has no directory".
2. **A single-segment directory (`results`) carries no separator**, so a filter of "must contain `/`
   to be a path" dropped `RESULT_ROOT = os.path.join(ROOT, "results")` and pushed the ancestor arm
   into *unfoldable*. Correct rule: keep it when it contains a separator **or** it is a directory
   under the repository root, and publish that decision so `check` can recompute from the row.

## Verification

- `scripts/e488_writer_directory.py` — run rc0, `check` problems=[], `verify` problems=[], **selftest 23/23**.
- S6 leg `writer_directory` (rc0, 0.1 s).
- Smoke leg `E488 a basename-only writer is placed by its module's own directory constant (r1513 bm-b)`
  — standalone 1/1 green, doctored verdict 1/1 red, face re-derived and green after restore.
- Card E488 appended to `knowledge/METHODOLOGY_ASSETS.md` (18 inserted lines, 0 deleted: pure append).

## What this does not say

The module naming the reader's directory is not the same claim as the write happening there at run
time: E487 traced the write path only as far as a bare basename, so a runtime-composed suffix can
still differ. E489 takes the next step: does the traced write call actually join the very constant
that placed the row?