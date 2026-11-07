# DIGEST 2026-11-07 r1516 bm-b -- E491 latest-copier

Card: E491 in `knowledge/METHODOLOGY_ASSETS.md`.

## Question
E489's single `dir_only` row is `bandthreshguard`: the traced write call opens
`BANDTHRESHGUARD-2026-10-29.json` while the reader opens `bandthreshguard_latest.json`, and the
row was published as "the write call composes the reader directory with another basename -- the
`_latest` copy is composed elsewhere". That is an inference from a tracer that reads only the
**first** argument of a call. A copy call (`shutil.copyfile(src, dst)`) carries its destination
**second**, so a copier is invisible to it. Who actually composes the latest name, and does it go
through the same directory constant?

## Reading (2026-11-07, 176 `_latest` names, 287 sources mentioning one)
- written directly: **123**
- **copy inside the source directory: 2**
- copy out of the source directory: 0
- several static composers: 51
- no static composer found: 0
- copy sources that are a dated sibling of the name: 2

The card's own name gets a determinate answer:

```
scripts/e273_guard_from_threshold.py
  path   = os.path.join(OUTDIR, FACE)      # BANDTHRESHGUARD-2026-10-29.json
  latest = os.path.join(OUTDIR, LATEST)    # bandthreshguard_latest.json
  shutil.copyfile(path, latest)            # line 385, same OUTDIR, same function
```

So E489's row is **one writer's second write in the same function**, not a second writer with its
own directory. The other copy row, `foo_latest.json`, is a selftest fixture inside
`scripts/e332_invisible_tail_recovery.py` (`results/x/foo_latest.json`); it exists on no disk, so
only one of the two copy rows is a real published face
(`faces_whose_destination_exists_on_disk` is published beside the tally).

## Three reusable rules
1. **Argument position is the probe's semantics.** Copiers put the destination second, direct
   writes put it first. A tracer that reads only first arguments does not miss a copier; the
   copier is not in its channel at all. Whether a name "has a writer" depends on how many write
   shapes the tracer understands, not on whether a writer exists.
2. **"Copy in the same directory" and "written directly" must be counted apart.** 123 of 176 are
   direct writes and only 2 are copies; treating a copy as "another writer", or merging the two,
   turns a 1-in-50 exception into a structural claim.
3. **A static census will pick up other scripts' fixtures.** A destination that never exists on
   disk must be published as a field, otherwise template code inside a selftest is counted as a
   real face.

## Wiring
- `scripts/e491_latest_copier.py` -- run rc0, check `problems=[]`, verify `problems=[]`,
  **selftest 25/25**; six doctored faces refused
- face `results/state_tilt/LATESTCOPIER-2026-11-07.json` + `latestcopier_latest.json` (176 rows)
- S6 leg `latest_copier` rc0 0.07s
- smoke leg `E491 a latest copy is composed by a copy call the write-call census cannot see`
  standalone 1/1 green, doctored 1/1 red with the face sha restored