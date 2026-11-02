# DIGEST 2026-11-02 r1378 -- E356: seven red legs, one question, and only one finding

## What was observed

The r1378 suite ends `271/278 PASS, 7 FAIL`. Seven assertions, one sentence between them:

```
[FAIL] ... every published control block is censused by which panel it re-derived on | summary does not re-derive
[FAIL] ... a leg that compares a face value finer than the field is printed | the summary does not re-derive
[FAIL] ... widening the producer needle relocates the unowned gates | the summary does not re-derive
[FAIL] ... a gate whose face no source can produce | the reason does not re-derive; a rung's counts do not re-derive
[FAIL] ... every reader that reaches a face only through a pointer | summary.pairs does not re-derive
[FAIL] ... the repaired corpus reading lands beside the shipped one | ValueError('too many values to unpack (expected 2)')
[FAIL] ... the repaired corpus reading lands beside the shipped one | the re-derivation does not reproduce every published candidate
```

They are not seven defects, and "re-derive" is doing work it cannot do. Every one of these legs
compares a *published* face against `build()` run on today's disk. The corpus those censuses
describe gains a script and two faces every round (r1378 alone added `e356_census_red_triage.py`
and two faces), so a published count is a statement about a population that no longer exists.

## What was measured

`scripts/e356_census_red_triage.py` rebuilds each face through the module's own loader and compares
leaf by leaf, addressing rows by identity and treating stamps (timestamps, cutoffs, file names) and
embedded line coordinates as coordinates rather than findings.

| leg | class | what moved |
|---|---|---|
| E298 replay control census | substantive | counts 138->142 faces; `self_face_cutoff_present` True->False |
| E299 finer-than-printed | population_moved | 759 rows appeared, 740 left; the 122 "changed" leaves are line numbers |
| E323 wider needle | substantive | corpus 2341->2350 files, mentions 6020->6035, reason line restates both |
| E325 orphan gate faces | substantive | orphan rows 24->3, largest family 22->1, share 12.24->1.53 |
| E331 pointer-only readers | in_sync | nothing -- build() equals the published face to the byte, and the leg is still red |
| E335 sibling entry point | population_moved | rows moved; the study's own verdict reproduces |

The two counts that carry the lesson:

* **1658 changed leaves by position vs 148 by identity.** Every one of the 1,510 extra leaves was a
  shifted index: a leg that diffs lists by position reports the whole tail of a list as changed
  when one row is inserted at the top.
* **7 of the 148 were still fake**: rows named `<unnamed leg at line 1128>`. Inserting a line above
  them renames them. Only the literal `line <n>` spelling is folded -- a template that blanks every
  digit would also blank a real value (12.24 -> 1.53).

## The two things that are real

1. **E325 is a finding that moved.** Orphan rows fell 24 -> 3 and the largest orphan family 22 -> 1
   because E332's recovered corpus changed which sources can name a face. A face that was
   "reproducible by a source that names it" is now "no source in the corpus names the face". That
   is the only row in this table that deserves a phone call, and it took a triage to see it inside
   six identical complaints.
2. **One leg was broken independently of its face.** `optin_allowlist()` returns
   `(consumers, verdict, why)`; the E335 leg unpacked two values and raised
   `ValueError: too many values to unpack`. Fixed in `smoke_test.py` this round. A leg written
   against a signature rots with the signature -- and it was invisible while the leg was "red for
   the same reason as the others".

## How to apply

When a guard says "does not re-derive", ask *what* moved: stamp, coordinate, population, or value.
Only the last is a defect. Do not republish to make the leg green -- re-deriving a census on a
bigger corpus cannot equal its old self, so the leg is red by construction, forever. Assert what
must hold (partition sums, closed vocabulary, commission, row-for-row identity) and publish the
triage. The E356 smoke leg is deliberately structural for exactly this reason: it grades the
triage's own accounting, so it cannot go red the moment a study publishes.