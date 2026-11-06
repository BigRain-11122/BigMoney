# DIGEST 2026-11-07 r1502 bm-b — E473: who writes the families nothing reads

Card: `knowledge/METHODOLOGY_ASSETS.md` E473.
Producer: `scripts/e473_producer_spill.py` (run / check / verify / selftest).
Faces: `results/state_tilt/producerspill_latest.json`, `PRODUCERSPILL-2026-11-07.json`.

## Reading

Population: E472's 97 unread vintage families (571 files, 28.5 MB, 0 with a study consumer).

| writer class | sites |
|---|---|
| publishes a studied face **and** an unread family (spillover) | 240 |
| resolves faces, none of them studied | 94 |
| names a family but resolves no face of its own | 40 |
| **total writers with write-call evidence** | **374** |

Resolved faces: 2,226 — 1,848 opened by a study, 85 only by a one-off `_r` round script, 12 only by
a smoke leg, 281 by nothing in the corpus.

Bytes: distinct unread emission 7,235,450 per cutoff (E472's 28.5 MB over each family's vintage
count); summed over writers 16,624,043 per cutoff, because several writers emit the same family.
Top unread emitters: `scripts/e97_routing.py` (7 families, 1.9 MB/cutoff, mixed),
`scripts/e109_repairsweep.py` (6 families, 1.3 MB/cutoff, unresolved), `scripts/e417_shadow_face.py`
and `scripts/e426_dynamic_face_names.py` (446 KB/cutoff each, mixed).

Verdict: `some_unread_family_writers_also_publish_studied_faces_and_some_publish_only_unread`.

## Why it matters

E472 priced 28.5 MB of output that no study opens but could not say whether that output is an
accident of a script that also does useful work. Half the answer is now yes: 240 of 374 writers emit
one family a study reads and one nothing reads, so the unread half is a one-line prune at the source.
The other half is a policy question, and 40 sites are not even answerable that way — their own
evidence names a family but resolves no file, because the path is composed at runtime.

The most consequential number is the residue: **47 of E472's 97 families have no write-evidence
writer at all**. "Prune the spillover" is executable for 50 families by name and meaningless for 47.

## Pits

1. **A write call in a site that merely mentions the token is not a producer.** E472's `writes` flag
   yields 5,481 producers — `smoke_test.py` is credited with 54 families because the suite writes
   *something*. Evidence taken from the write call's own argument list (plus one hop through assigned
   names) yields 374. A 15x over-count disappears the moment the definition names the channel.
2. **Attribution multiplies bytes.** Summing unread bytes over writers gives 2.3x the distinct family
   total because families are shared. Both numbers are published; only the distinct one is a volume.
3. **A vacuous class is a lie in a table.** The first build classed every writer with no resolved
   face as "only unread" — 40 rows where the truth is "its faces cannot be resolved". The face now
   carries a third class; the class vocabulary is in `verdict_vocab`'s sibling `CLASSES` and the row
   guard refuses a row whose class disagrees with its own face list.
4. **A family-token match is not ownership.** `shared_families` lists the families where more than one
   writer names the token, so a reader cannot mistake the row for a claim that this script authored
   the whole family.

## Cost

The one-pass corpus scan (reader literals + write evidence in the same AST walk) is ~10 minutes on
this tree: 10,992 sources parsed, 296,665 opener literals. `check` re-derives in 0.1 s and never
rebuilds; `verify` rebuilds and is the expensive leg.