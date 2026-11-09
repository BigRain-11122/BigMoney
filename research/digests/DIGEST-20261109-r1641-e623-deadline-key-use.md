# r1641 bm-b — E623: a dead line is not an unread key

**Face**: `results/state_tilt/DEADLINEKEYUSE-2026-11-09.json` (+ `deadlinekeyuse_latest.json`)
**Runner**: `scripts/e623_deadline_key_use.py` (selftest 22/22; run/check/verify `problems=[]`)
**Smoke leg**: `smoke_test.py` leg E623 + `scripts/run_e623_smoke_leg.py` (1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically)
**S6 leg**: `Tools/s6_chain_bmb.py` → `deadline_key_use` (`verify`, rc=0, 0.05 s)
**Card**: `knowledge/METHODOLOGY_ASSETS.md` E623

## The question

E619 counted locals assigned from a face key and never read again (27 modules / 36 face-key lines).
E622 then showed 34 of those lines sit in a function that is reachable from module level, so they are
real defects rather than inert residue. Neither asked the local question: **is that same key read
anywhere else in the same function?** E619's rule is "no load after the assignment", which cannot
distinguish a duplicated read from a loop-carried read from a genuinely dropped value.

## The reading

Population: `scripts/*.py` (AST) via `e619.population`, face publishers only, 1,095 modules, 14
skipped, this study and E622's self-exclusion set removed.  34 live dead face-key lines in 29 holder
functions across 26 modules:

| class | lines |
|---|---|
| `superseded_duplicate_read` (the key is read again **after** the dead line) | 6 |
| `key_read_only_before_the_dead_line` (read only on **earlier** lines) | 7 |
| `only_other_reads_are_dead_too` | 0 |
| `only_read_of_that_key_in_the_function` | 21 |

So "has a duplicate read" is 13 lines, but only 6 of those duplicates are live reads *after* the dead
line. 21 lines are the only read of their key in the function — those are the values taken and
dropped. 23 of the 34 keys are also read in another function of the same module, which is a different
statement again: the key is used, just not here.

Cross-check against E622: the population is imported, not re-implemented; the re-derived holder count
(29) and line count (34) match the published face holder-by-holder with 0 differing line counts.

## Instrument notes (in-window)

1. **Inherited estate with a newer script than face.** The killed round wrote the face at 19:34:41 and
   touched the script at 19:35:59. Rebuilding changed the published verdict from
   `13_of_34...` to `6_of_34...` — the inherited face was built by an earlier revision. Nothing from
   the inherited face was trusted; every gate was re-run.
2. **Position, not existence.** The first useful design decision is that a read of the same key has
   three fates inside a function (after the dead line, before it, only once). A boolean "is the key
   read elsewhere" collapses them and reports 13 where the defensible count is 6.
3. **Key identity is literal-only.** A key held in a variable is the same blind spot E619 has;
   and `m["k"]` on a *different* dict in the same function satisfies the duplicate test — published
   as a limit and seeded as E624, because it can only shrink the superseded class.