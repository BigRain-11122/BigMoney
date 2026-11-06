# E462 — the dialect nobody speaks is nearly unwritten; the two faces that write it disagree with themselves (r1485 bm-b)

**Study:** `E462-WHICH-IDENTITY-DECLARATIONS-SIT-IN-A-DIALECT-NO-READER-SPEAKS`
**Face:** `results/state_tilt/identitydialect_latest.json` + `IDENTITYDIALECT-2026-11-06.json` (evidence_cutoff 2026-11-06)
**Producer:** `scripts/e462_identity_dialect.py` (run / verify problems=[] / check problems=[] / selftest 22/22)

## The question

E461 measured the vocabulary, not the pages: 110 identity-named read sites against 15 frozen identity
field names, 7 of which (`card_id`, `study_id`, `prereg_path`, `prereg_note`, `pinned_note`,
`source_card`, `source_cards`) are read by no source at all. A face that writes its identity only in
one of those names is self-describing to a human and silent to every gate. This card asks it per
face: which voices does each face actually use, do they agree, and what would dropping the spoken
name cost?

## Readings

Population = the 526 graded rows of E458's `faceidentity_latest.json` that declare a top-level
machine-readable identity (the same population E461 graded, machine-read from E461's own
`face_rows()` so the two studies cannot drift apart).

* **617 declared field instances over 526 faces**, of which **2 instances** sit in a name no source
  reads. The silent dialect is, in practice, almost unspoken.
* **524 faces speak only names a source reads**, **2 are redundant** (a never-read name beside a
  read one), **0 are silent** (never-read names only). Verdict
  `the_never_read_names_are_a_second_voice_on_faces_that_also_speak_a_read_name`.
* **Both redundant faces contradict themselves.** `results/state_tilt/SELFRES-2026-10-29.json` and
  its `selfres_latest.json` twin declare `source_study: "E252"` beside `study: "E253"` — a second
  voice naming a *different study*, unreadable by anything, so no gate has ever seen the
  disagreement.
* **Two more faces disagree in the spoken dialect.** `NAMERESOLVE-2026-11-04.json` and its
  `nameresolve_latest.json` twin declare `card: "E413"` and `study: "E421"`. Both names are read, so
  this contradiction is *visible*: a consumer keying on `card` joins the face to E413 and a consumer
  keying on `study` joins it to E421, and nothing says which is the study. 4 faces carry more than
  one identity value (2 pairs, each a face plus its `latest` twin); 89 of 526 faces declare both
  `card` and `study`, so the shape that can disagree is common while the disagreement is rare.
* **Only three distinct names are ever declared on a face at all**: `card`, `study`, `source_study`.
  Of the 16 names measured, 13 are never written by any face — the vocabulary E458 froze is much
  wider than the dialect faces actually speak.
* **Join exposure 389**: 389 faces are currently joined by a consumer that keys on a read name
  (carried from E461's rows, 0 faces absent from that face). All of them would become unreadable if
  the read names were dropped — the silent dialect is not a harmless extra.
* **Zero ambiguous-name exposure**: no face declares an identity using only `id` / `pin` / `pid`
  (E461's ambiguity caveat does not bite at this layer).

## Two rules this round measured rather than assumed

1. **A name outside the frozen vocabulary is not a never-read name until it is measured.** The first
   build counted `source_study` as never-read by construction (it is not one of E458's 15 names),
   which would have published "2 faces write in a dead dialect" off the strength of a lookup
   failure. The census was widened to `vocabulary ∪ declared names`, `source_study` was then
   measured (0 read sites — the claim survives), and the payload now carries
   `fields_outside_the_frozen_vocabulary` + a per-face count so the distinction is never silent.
   Same family as E207/E208: a classifier that accepts a name it never looked at.
2. **A scanner must exclude itself *and its predecessor*.** This family is the only thing in the
   repo that reads identity field names as field names; E461 already excluded itself, and E462
   excludes `e461_`/`e462_`/`run_e461`/`run_e462` and both faces. Carrying E461's published counts
   beside the re-derived ones (`field_census_per_e461`, `fields_whose_read_status_disagrees_with_e461`)
   publishes the disagreement instead of hiding it — it is empty this round.

## Wiring

* S6 leg `identity_dialect` (`python scripts/e462_identity_dialect.py check`, tallies re-derive from
  the published rows without re-walking the corpus).
* Smoke leg `e462 is a face's identity written in a dialect anyone reads (r1485 bm-b)` +
  `scripts/run_e462_smoke_leg.py` (verbatim extraction; red on a doctored copy that recasts a
  read-only face as redundant).
* Methodology card E462 in `knowledge/METHODOLOGY_ASSETS.md`.

## Bound published, not claimed

Static only: a name reached through a composed key (`d["card" + "_id"]`) is invisible and would be
counted never-read, which inflates the *silent* dialect, never the read one — and this round's
silent count is 0, so the bound costs nothing here. Contradiction compares declared values as
strings; two ids differing only in case/spacing would be reported as a contradiction.