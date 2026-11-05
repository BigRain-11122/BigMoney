# DIGEST 2026-11-06 r1468 bm-b -- E449: the prereg pointer is a comment with a name

Card: `E449-WHICH-DEAD-PREREG-POINTER-IS-A-DOCUMENT-NO-STUDY-CODE-EVER-READS`
Face: `results/state_tilt/deadprereg_latest.json` (`DEADPREREG-2026-11-06.json`)
Producer: `scripts/e449_dead_document_pointer.py` (selftest 26/26, `check problems=[]`, `verify problems=[]`, run 8 s)
Leg: `smoke_test.py` `# E449 (r1468 bm-b)` + `scripts/run_e449_smoke_leg.py` (1/1 green, 1/1 red doctored)
S6: `Tools/s6_chain_bmb.py` leg `dead_prereg_pointer` (`check`, rc 0, 0.05 s)

## Question

E448 graded 30 dropped compositions as opened nowhere in their own file and 25 of them name a path
that already exists. The largest family is a research-note pointer: a study script composes
`os.path.join(ROOT, "research", "<STUDY>-P1.md")` into a `PREREG` constant and never opens it. A
pointer to documentation is harmless; a pointer that stands in for reading the prereg is a claim
with nothing behind it. Which is it?

## Answer

30 dropped compositions -> **7** land on an existing `.md` under `research/` (**23** out of scope:
12 not a file, 10 outside research/docs, 1 target unresolvable). Verdict
`some_dropped_document_pointers_are_named_in_code_text_but_never_opened`.

| class | n |
|---|---|
| read_by_an_opener_elsewhere | **0** |
| cited_in_code_text_only | **7** |
| cited_in_prose_only | 0 |
| declared_and_unread_in_code | 0 |

The seven notes are `FUND-DIVLOWVOL-P1`, `FUND-QUALITY-P1`, `FUND-VALUE-P1`, `LOWAMP-DEEP-P1`,
`LOWAMP-P1`, `LOWAMP-P2`, `LOWAMP-P3`. All seven exist on disk. **No opener call anywhere in the
19,278 walked text files (12,197 `.py`) takes an argument that carries any of their basenames** --
neither directly nor through a same-file constant, including the second declaration at
`scripts/divlowvol_live_picks.py:52`.

The notes are nonetheless cited: **31 distinct `.py` files name one of these notes by filename**
(39 citation lines inside the graded rows; the face publishes five per note) and 18 prose files do
too. So the corpus *talks about* the prereg constantly and never *opens* it.

And the constant itself is dead weight: in all seven files `PREREG` is assigned and then **loaded
zero times** (`rows_whose_constant_is_never_read_again = 7`). A name that is never read again is not
a gate; it is documentation that survives a lint pass.

## The measurement that had to be tightened

The first build classified all seven as `cited_in_code_text_only` on a **stem** match
(`FUND-QUALITY-P1`), and the stem is the study id: it appears 1,985 times across closeout scripts,
handover notes and round reports that have nothing to do with the note. Citing the note means naming
`research/<STUDY>-P1.md` with its extension, so the classification now runs on the basename and the
1,985 stem-only mentions are published as `study_id_mentions_excluded_from_the_class` instead of
being silently promoted into evidence. Two rows would have changed class on the looser rule
(`LOWAMP-P2`: 0 basename citations, 177 stem-only prose mentions; `LOWAMP-P3`: 2 basename citations
against 52 stem mentions).

## Why it matters

A study's prereg is the one document that is supposed to constrain the study. Here the constraint is
carried by a constant nobody reads: the promise is in a string, and the string is never dereferenced.
That is not a defect in any single script -- it is what a "we froze a prereg" claim looks like when
the only machinery behind it is bookkeeping. The cheap repair, when a study needs it, is to hash the
note into the study's own output (a `prereg_sha16` field); a read that only exists to print a path is
worth less than the hash.

## Limits published on the face

* opener evidence is a same-file or literal-argument test: a path assembled in another module and
  imported here is not followed;
* a citation means the note's filename, counted once per file for prose, and the constant-use count
  reads `ast.Name` loads in the declaring file only;
* out-of-scope rows are published with their reasons rather than dropped.

## Files

* `scripts/e449_dead_document_pointer.py` (run / check / verify / selftest 26/26)
* `results/state_tilt/deadprereg_latest.json` + `DEADPREREG-2026-11-06.json`
* `scripts/run_e449_smoke_leg.py`, `smoke_test.py` leg, `Tools/s6_chain_bmb.py` leg
* card `knowledge/METHODOLOGY_ASSETS.md` E449