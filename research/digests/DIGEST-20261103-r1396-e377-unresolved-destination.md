# DIGEST 2026-11-03 r1396 — E377: the destinations a name-keyed census cannot see

**Card**: E377-WHICH-PUBLISHED-PATHS-A-CENSUS-CANNOT-KEY (ready, priority 3, entered r1393)
**Source**: E376 SETTLED a member's bill with "zero fields is not writes-nothing" — the two store
members write `"results/_r%sbmb_s6_chain.json" % rnd`. The card asks how large that blind spot is
across the whole corpus.
**Face**: `results/state_tilt/UNRESOLVEDDEST-2026-11-03.json` (+ `unresolveddest_latest.json`)
**Script**: `scripts/e377_unresolved_destination.py` (selftest 10/10)
**Lane**: cpu-only, zero network, nothing from the corpus executed (only `ast` + `json.load`)

## Answer in one line

542 of 2,121 `json.dump` calls (25.6%) write to a path the instrument cannot name, and the faces they
reach include 36 published faces that **no resolved sink in the corpus keys** — so "no writer" is two
different sentences: *no named writer* and *a writer this instrument cannot name*.

## The population

| quantity | value |
|---|---|
| corpus sources | 2,411 (2,393 parsed) |
| `json.dump` calls | 2,121 |
| resolved to a literal/constant path | 1,579 |
| unresolved | **542**, in **285** sources |
| faces named by an unnameable writer | 62 |
| faces keyed by some resolved sink (the census surface) | 856 |
| faces reached by an unnameable writer and absent from that surface | **36** |

Why the 542 cannot be keyed (histogram, top): `argument_supplied` 94 (the destination is the caller's
argument), `local_expression` 84, `joined_computed` 70 (path built at run time), `other` 26,
`returned_from_helper` 6, `attribute_supplied` 3, `formatted` 2.

## The load-bearing consequence

E350 publishes 40 of its 131 "unwritten guard" rows. Exactly **one** of those 40
(`results/token_usage.json:generated`, 2 guards) is named by an unnameable writer — so on the *published*
subset the blind spot moves 1 row, while the other 91 untested rows are simply unknown. The honest
sentence is therefore not "the census is 25% blind to writers in general" but "for each claim the
instrument makes about a specific face, ask whether that face is keyed at all".

Sample of the 36 unkeyed published faces: `docs/daily_report/REPORT-2026-10-07.json`,
`docs/live_usage/LIVE-2026-10-07.json`, `docs/live_usage/LIVE-latest.json`,
`results/_r668bmc_ca_union_receipt.json`.

## Reusable findings

1. **"No writer" must be split before it is published.** A census that keys literal/constant
   destinations answers "did a *keyable* source write this"; an unnameable writer produces the same
   silence as no writer. Publish the unnameable set and its reach beside the negative claim, or the
   negative claim silently absorbs a blind spot (E376's rule 2, priced corpus-wide).
2. **A writer's name reach is a lower bound.** The reach test is a NAME test over one source's
   literals: it shows a face the writer *could* write, never that it writes it. A writer whose
   destination is supplied by its caller names no face at all, so reach is under-counted, not
   over-counted — the 36 is a floor.
3. **Reach is not consumption.** A face reached by an unnameable writer and keyed by nobody is a face
   nothing in the corpus is bound to; whether a human or an out-of-corpus tool reads it is a different
   question (successor card).

## Bound

Name test over one source's literals (could-write, not does-write); callers that supply the destination
contribute no name, so reach under-counts; `keyed` is the union of resolved sinks over the same corpus
E350 walks, so a face keyed only by another unnameable writer still counts as unkeyed; the E350 face is
read as published and not rebuilt here.

## Cost

One corpus scan (2,411 sources) plus one static walk; no replay, no engine, no network.