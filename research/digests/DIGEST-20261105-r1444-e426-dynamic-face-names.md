# DIGEST 2026-11-05 r1444 bm-b -- E426: a literal census describes what is read, not what is written

**Card.** E426-WHICH-READER-BUILDS-A-FACE-NAME-FROM-A-VARIABLE-SO-NO-LITERAL-NAMES-IT (pool,
cpu-only, ready 2026-11-04)
**Product.** `scripts/e426_dynamic_face_names.py` + `results/state_tilt/DYNAMICNAME-2026-11-05.json`
(+ `dynamicname_latest.json`), smoke leg `# E426 (r1444 bm-b)`, S6 leg `dynamic_face_names`,
methodology card E426.

## What was asked

Every name census in this tree (E402 basenames, E404 resolved directories, E422 bare names, E417
bare literals) declares the same limit in prose: *a reader that builds the name from a variable is
invisible to it*. E417 wrote that sentence last round and moved on. E426 prices it on three
machine-read sources: the python corpus parsed with `ast` (every expression that produces a
`*.json` name from a non-constant part is a template), the published faces under `results/`, and
the faces E411 priced (the ones a reader in this tree actually opens).

## What was found

| reading | value |
| --- | --- |
| published faces (basenames not starting with `_`) | 10,034 |
| named by a literal somewhere in the corpus | 3,054 (all of them also have a template) |
| reachable **only** through a variable-built name | 6,716 (67%) |
| no mask at all (no literal, no matching template) | 264 |
| templates found / kept as specific enough to name a face | 5,551 / 5,333 |
| ...sitting in a function that opens a file | 2,818 |
| faces a reader opens (E411: 189 files, 5 directories, 14 templated) | 189 files |
| ...of those, reachable only dynamically | **0** |
| ...named by a literal | 188 (the 1 remainder is `results/etf_book_production/CARD.md`) |

**Verdict:**
`every_file_face_a_reader_opens_is_named_by_a_literal_while_the_producers_spell_only_a_template_so_a_literal_census_describes_what_is_read_not_what_is_written`.

Two directory clusters carry most of the blind spot: `results/p2cal_ext` (3,946 non-literal faces,
2,635 dynamic-only) and `results/wild_route` (1,572 / 1,569) -- each a producer that writes one file
per symbol from a `"%s.json" % key` template. Every one of those 3,946 and 1,572 sits in an opener,
so this is not dead text: it is the shape of every sweep lane in the tree.

## Five rules worth keeping

1. **A wildcard that names a directory is not a name.** The first pass treated every template as a
   mask and reported essentially every face as dynamically reachable -- true and useless. A
   template is now *specific* only if some fragment keeps a non-empty stem after the last `/` and
   the `.json` suffix are removed: `SIG-*.json` names a face, `results/<dir>/*.json` and
   `stem + ".json"` name a place. 218 of 5,551 templates were discarded, and the discard list is
   published so the filter itself is auditable.
2. **A scanner that publishes changes the population it counts.** The first build counted its own
   `DYNAMICNAME-*.json` and `dynamicname_latest.json`, so the next build saw 12,997 faces instead
   of 12,995 and verify went red on `verdict_reason` twice in a row. Round receipts
   (`results/_r1444bmb_s6_chain.json`) have the same effect every round. Both are excluded by name
   pattern (E180/E207 family), and the exclusion is stated in `method_limits`.
3. **A population row is three kinds, not one.** E411's population is "names the suite opens" and
   carries directories (`results/state_tilt`) and templated names (`TSMOM-%s.md`) beside files. On
   the first build those seven rows read as "faces with no mask at all" -- a finding manufactured
   from a category error. Labelling every row `file`/`directory`/`templated` left exactly one real
   unmasked face.
4. **Publishing every row is not publishing the finding.** The all-rows face was 13.3 MB for 12,997
   rows. The face now publishes a deterministic 60-row sample plus a per-directory tally, and the
   gate reads the tally: 243 KB, and the equality comparisons stay meaningful.
5. **A two-way verdict would have been wrong in the direction that flatters the instrument.** With 0
   dynamically-named faces among the ones readers open, "census adequate" was available -- while
   67% of the corpus the census claims to describe is invisible to it. The verdict is four-way, and
   the readers/writers split is its own sentence.

## Why it matters

The censuses are not broken -- they describe the read side correctly, and that is what a gate needs.
What they cannot do is answer "how many faces exist": a producer that writes `"%s.json" % key` never
spells a name, so any population built from literals undercounts by two thirds. That number now has
a face: 6,716 of 10,034.

**Delivered.** `scripts/e426_dynamic_face_names.py` (run / verify problems=[] twice / selftest
27/27); `results/state_tilt/DYNAMICNAME-2026-11-05.json` + `dynamicname_latest.json`; smoke leg
`# E426 (r1444 bm-b)` (1/1, proved red on a doctored `faces_literal_named` then restored
byte-identically); `scripts/run_e426_smoke_leg.py`; S6 leg `dynamic_face_names` (rc=0, 72 s);
methodology card E426; read-only -- no face, census or reader edited.