# DIGEST 2026-11-07 r1519 bm-b — E493: whose bytes are behind E492's two single-write harnesses

**Card** E493 — **Face** `results/state_tilt/LATESTCOPYOWNER-2026-11-07.json` (+ `latestcopyowner_latest.json`)
**Script** `scripts/e493_latest_copy_owner.py` (run / check / verify / selftest 27/27)
**Pool row** E493 (seeded r1518, burned r1519)

## Question

E492 published two latest names whose only visible harness "writes once with no restore":
`deadprereg_latest.json` and `dirfield_latest.json`. A label about writing is not an answer
to who wrote the copy that is on disk. Three harness shapes collapse into that one label:

- it opens the face only to read it and mutates the document in memory;
- it writes the face and writes the original back;
- it writes the face and leaves whatever it wrote.

## Reading (2026-11-07)

| quantity | value |
|---|---|
| faces selected by E492's `harness_single_write_composers` | 2 |
| harness opens the face only for reading | **1** (`deadprereg`) |
| harness writes then writes the backup back | **1** (`dirfield`, restore at `run_e423_smoke_leg.py:74`, inside a `finally`) |
| harness writes and leaves | **0** |
| harnesses that author a payload of their own | **0** |
| live doctor runs | 2 |
| live runs that left the face byte-identical | **2** |
| faces repaired by this build | **0** |
| producer builds re-derived | 2 |
| disk matches a fresh producer build byte-for-byte (clock removed) | 0 |
| disk is a stale vintage of its own producer (shape + verdict agree) | **2** |
| disk matches a harness mutant | **0** |

Verdict: `the_copy_on_disk_is_the_producers_in_every_case`.

## The label is wrong in both directions

`deadprereg_latest.json` — `scripts/run_e449_smoke_leg.py` opens the face twice, both `rb`,
never writes. E492 still carries "writes the name once with no restore" on it: the label
claims a write that does not exist, so the number it contributed to `faces_with_a_single_write_harness`
was never about a write at all.

`dirfield_latest.json` — `scripts/run_e423_smoke_leg.py` captures the whole file at line 55
(`io.open(FACE, "rb").read()`), runs a deliberately poisoned leg, and puts it back at line 74
in a `finally`. The doctor prints `face restored byte-identical: True` and returns 0; the sha
before and after agree. The static matcher saw the write sites and not the write of the
backup, so "no restore in the same source" is a false negative — the restore is
`io.open(FACE, "wb").write(backup)`, a shape the matcher does not recognise.

## Ownership vs freshness are two numbers

Neither disk copy matches a fresh build byte-for-byte. Read alone, that would say "the harness
left something behind". Both differ only because the tree grew: `dirfield`'s population moved
from 13,080 to 13,092 faces while the key set and the verdict stayed identical. Publishing
`disk_shape_matches_a_fresh_producer_build` and `disk_is_a_stale_vintage_of_its_own_producer`
separately keeps a stale vintage from being read as a mutant.

## Three rules

1. **A label about writing has to survive both directions.** Zero write sites wearing
   "writes once" is the label inventing a fact; a second write of the backup variable wearing
   "no restore" is the matcher missing a form. Publish write sites, backup name, restore lines
   and whether the restore sits in a `finally`, and the label becomes re-checkable.
2. **Authorship and freshness are different readings.** Shape plus verdict decide who wrote
   it; byte identity decides whether it is today's vintage. Merging them turns a normal stale
   face into a defect.
3. **Pointing a module's output directory at a temp dir can break its read side.** A first
   draft redirected `ST` so the producer would write into a temp dir; `e449.build()` reads the
   sibling face `droppedpath_latest.json` from that same directory and died with
   FileNotFoundError, publishing "could not be measured" — the instrument's wound, reported as
   the subject's. Only call the pure `build()`; leave writing to the producer's own entry point.

## Verification

- `scripts/e493_latest_copy_owner.py` run rc0 / check problems=[] / **selftest 27/27**
  (read-only, backup name, restore line, `finally`, restore-without-payload, payload authoring,
  three persistence classes, clock stripping, five ownership verdicts, stale vintage still the
  producer's, reshaped payload → untold, six doctored faces refused).
- `smoke_test.py` leg E493 — standalone 1/1 green, `--doctor` 1/1 red with the face sha restored.
- `Tools/s6_chain_bmb.py --only latest_copy_owner` rc0 0.06s.
- Nothing published was changed by the live arm (0 repaired), nothing deleted, no GPU, no cloud.

## Limits

Two faces at one moment. The live arm sees before and after, not during, so a write and
restore inside the same second is indistinguishable from no write. The producer arm requires a
pure `build()`; a builder with side effects needs its own arm. This card does not extend to
E492's other 49 faces.