# DIGEST 2026-11-07 r1501 bm-b — E469 arm-1: which channels tie a published face to its writer

Card: `knowledge/METHODOLOGY_ASSETS.md` E469.
Producer: `scripts/e469_face_producer_edge.py` (run / check / verify / selftest).
Faces: `results/state_tilt/facetrace_latest.json`, `FACETRACE-2026-11-07.json`.

## Reading

13,740 payload faces under `results/` + `docs/` (md/html excluded and published as
`documents_excluded`=520 because they belong to E449's population).

| channel | faces |
|---|---|
| named by a registry or digest | 5,545 |
| a quoted literal equals the face path | 2,935 |
| the payload names its own stem | 1,045 |
| a pointer to another face | 344 |
| a card id the asset file resolves | 271 |
| a card id the asset file does **not** carry | 20 |

8,257 traceable (60.1%), 5,483 (39.9%) with no channel at all.

Owner ambiguity: exactly one literal owner 1,505; more than one 1,430; none 10,805.

Verdict: `some_published_faces_are_named_by_no_source_and_carry_no_card`.

## Why it matters

The instrument can name a single writer for only 11% of published faces. Where two sources carry
the same path literal, nothing on disk decides which one wrote the face that is on disk, so a
consumer that resolves "the producer" from a literal is guessing. This is the reverse of E466: it is
not that readers ignore pointers, it is that for most faces there is no unambiguous pointer to
ignore.

## Pits

1. A substring in a source file is not an owner. `basename in text` counted comments and longer
   paths and over-counted owners by ~1,370 faces (4,305 -> 2,935). The published rule is quoted
   literals only and `literal_method` says so.
2. 13,740 faces x 2 MB of digests = 27 GB of scanning: first build 310 s, after one-pass token sets
   and literal dicts 69 s. Measure the unit of the scan before optimising the loop (E442 family).

## Continuation (arm-2, deliberately not claimed)

Join these rows with the E466/E470 reader map: which study opens each face, and does that reader walk
the same channel that names it. The pool entry for E469 carries this pointer.