# Digest r1411 -- E394: the 218 reads that open a face without their key, classified

Face: `results/state_tilt/PHANTOMWHY-2026-11-03.json` (+ `phantomwhy_latest.json`).
Card: `knowledge/METHODOLOGY_ASSETS.md` E394. Study: `scripts/e394_phantom_why.py`.

## What was asked

E393 priced the 1 MB read cap and found the cap had been hiding faces that almost all *do* store the
key (3,241 of 3,271). That turns the other direction into the remaining unexplained class: reads E392
resolved to a real face which does not store their key -- 188 under E392's cap plus 30 that only
appeared once the cap was lifted. A "face lacks the key" line is not yet a defect, so this round
classifies all of them instead of counting them.

## What it measured

| class | reads | keys | reading |
|---|---|---|---|
| `producer_names_the_key_but_the_face_lacks_it` | 131 | | the face's own producer writes the key structurally (dict literal / store / `setdefault`), so it can be written conditionally |
| `key_lives_in_another_face` | 69 | | another read in the same scan opened a face and found the key there |
| `a_face_stores_it_but_no_read_names_which` | 16 | | the population counts a carrying file; no read witnesses which face |
| `face_unparsed_so_presence_unknown` | 2 | | above the cap or unparseable: unknown, never dead |
| `key_present_at_another_depth` | 0 | | -- |
| **`no_face_in_the_tree_stores_this_key`** | **0** | | **the only broken-reader class** |

Residual population: **218 reads / 54 keys / 37 faces**, of which **30 reads** were the slice only
the uncapped reader could see. Broken readers: **0**.

## The thing this round refuses to flatter

The first pass asked whether a source that names the face also *contains* the literal key, and it put
all 218 reads in the producer class. That is co-occurrence, not authorship: `arm` matched six
unrelated closeout scripts and `bytes` matched `smoke_test.py`. Requiring a structural write moved 87
reads into "another face" and "unwitnessed" without changing any read's face. Since the class name
has to name the measurement, it is now `producer_names_the_key_but_the_face_lacks_it` **with** the
write form and line in the evidence column.

Two more splits that would have been flattering in either direction: an unwitnessed key is not a dead
key (the population's `files` field is a count, not a list, so "which face carries it" cannot be read
off it), and an unparsed face is not a dead face.

## Verdict

`no_residual_read_is_a_broken_reader_it_is_depth_producer_or_moved_name`

No published ratio moves: the share is storing-reads over name-matched reads, and this is the
complement of both terms, so `moves_a_published_number = False` is published with the arithmetic
(E382's republish rule applies to splits that move a headline).

Wiring: `scripts/e394_phantom_why.py` (run / verify problems=[] / selftest 21/21); smoke leg E394
(1/1, exec'd verbatim by `scripts/run_e394_smoke_leg.py`); S6 leg `phantom_why` (rc 0, 0.07 s).
Successor: E384/E385 in the pool ask the opposite question of the same census (which keys no site
could open, and whether splitting a merged key moves a published count); the 131 producer-class keys
are the natural population for asking whether a producer's conditional write is documented anywhere.