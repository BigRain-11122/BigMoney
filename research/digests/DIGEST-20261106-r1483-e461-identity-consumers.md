# DIGEST 2026-11-06 r1483 (bm-b) -- E461: does any consumer read the identity a face declares?

**Card.** E461-WHICH-CONSUMER-ACTUALLY-READS-THE-IDENTITY-A-FACE-DECLARES
**Producer.** `scripts/e461_identity_consumers.py` (run rc0 / verify problems=[] / check clean /
selftest 24/24)
**Faces.** `results/state_tilt/identityconsumers_latest.json`,
`results/state_tilt/IDENTITYCONSUMERS-2026-11-06.json`
**Methodology card.** `knowledge/METHODOLOGY_ASSETS.md` E461

## Why the question exists

E458 (r1482) graded 538 study faces and found 526 carry a machine-readable identity that resolves to
a file or a pool card. Resolving is not reading. If no consumer keys on the field, the declaration is
a label: a face could rename its identity field tomorrow and no reader would notice.

## Readings (526 graded faces, 8,209 .py sources)

| reading | count |
|---|---|
| faces named by a source that reads a declared field | **389** |
| ... of which named by a *face-specific* source (names ≤10 faces) | **4** |
| faces joined by a source that also carries the declared value as an exact literal | **12** |
| faces named only by their own producer | **130** |
| faces named by a consumer that reads none of their fields | **1** |
| faces named by nobody | **6** |
| identity field names never read by any source | **7 of 15** |
| read sites on identity-named fields | **110** |
| read sites on ambiguous names (`id`, `pin`, `pid`) | **1,242** |

The 7 never-read names are exactly the shape-named ones plus their siblings: `card_id`, `study_id`,
`prereg_path`, `prereg_note`, `pinned_note`, `source_card`, `source_cards`. Readers key on `study`
(53 read sites / 44 files) and `card` (6 / 6), i.e. on the *generic* vocabulary, never on the names
that carry the shape's precision.

## The three rules

1. **A file-level conjunction is not a link.** 385 of the 389 joins come from one source
   (`smoke_test.py`) that names more than ten faces -- a census reader, not a face-specific link.
   `joined_breadth` is published per row so the two shapes cannot be merged into one number.
2. **Exact literal is not substring.** `E452` occurs in `smoke_test.py` only inside leg labels,
   never as a compared constant; a substring test would report a join the code does not make. The
   value join is graded on exact string constants (12 faces), while the legs that do compare
   `_doc.get("study") == "E229"` are real exact-literal joins.
3. **Generic key names inflate the census.** `id` alone carries 1,125 read sites across 895 files
   (`Money0923/quant/arena.py` et al) unrelated to any study identity. Ambiguous names are counted
   apart; folding them in would let "every field is read" pass on `d["id"]`.

## Verdict

`some_faces_are_joined_to_their_study_by_a_consumer_keying_on_the_declared_field` -- with the split
published: the link exists, it is concentrated in one census reader, and only 4 faces have a
face-specific reader. The identity vocabulary promises 15 field names and the corpus reads 5.

## Bound

Static only. A computed key (`d[k]` with `k = "stu" + "dy"`) is invisible; a consumer comparing
against an imported constant counts as a field join and not a value join; a name composed from parts
is not matched (E458's bound). Read-vs-write is decided by the AST context of the key constant, not
by data flow.