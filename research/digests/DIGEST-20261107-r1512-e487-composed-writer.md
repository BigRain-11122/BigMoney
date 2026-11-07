# DIGEST 2026-11-07 r1512 bm-b — E487: who writes the latest spellings nobody writes literally

Card: `knowledge/METHODOLOGY_ASSETS.md` E487.
Producer: `scripts/e487_composed_writer.py` (run / check / verify / selftest).
Faces: `results/state_tilt/composedwriter_latest.json`, `COMPOSEDWRITER-2026-11-07.json`.

## Reading

Population: E482's 84 spellings that resolve to a file on disk but that no source in the corpus
writes as a literal (E479's 36 twins excluded, this census's own writer and runner excluded). The
parent's population tally is reproduced exactly (84/84), so the rows are the same population and
not a re-count.

| class | spellings |
|---|---|
| a python source that writes also names the stem (traced) | 67 |
| a source that never writes names the stem (untraced residue) | 11 |
| only its readers name the stem | 3 |
| only a non-python source names it | 0 |
| excluded by this census (smoke / one-off round scripts) | 3 |
| no source names the stem | 0 |

The 67 traced rows split by route: **20** reach the stem through a literal that is written where it
is named, **5** only through a write helper's argument, **42** only through a loop over a set of
name constants. Verdict: `most_unwritten_spellings_have_a_writing_source_whose_path_traces_back_to_the_stem`.

So E482's "no source writes it" bucket is mostly a scanner limitation, not a wild face: 67 of 84 have
a writer inside the tree whose name is composed at run time. What survives is 11 spellings that are
named by sources which never write anything, plus 3 that only this census's excluded scripts name.

## The residue moved to the directory layer

Tracing the stem says a writer exists; it does not say the writer writes where the reader looks.
Second question, same 67 rows:

| directory class | spellings |
|---|---|
| the writer path reaches the directory the reader resolves to | 1 |
| the writer path reaches only a bare basename (directory untraced) | 51 |
| the writer path reaches a stated directory that is not the reader's | 15 |

Only one of 67 composed writers can be shown to write into the directory its own reader resolves
to; the interesting number is the 51 where the trace stops at a basename — an unfinished trace, not
a finding, and the next card (E488) is exactly that hop.

## Two defects caught in this window

1. **The ancestor walk is not a descent.** `os.path.dirname` returns its own argument for `../..`,
   `/`, `C:/` and `.`, so a "walk up until empty" loop over such a literal never terminates. The
   stranded run from the previous window hung here silently for more than five minutes; a
   `faulthandler.dump_traceback_later` guard pinned it to `_directory_class`. With a
   `parent == candidate` break the same tree builds in 31.8 s.
2. **A class must re-derive from the rows it publishes.** The directory class was computed from the
   full literal set while only the first 12 literals were published, so `check` — which recomputes
   from the published row — failed on `unresolved_latest.json`. Computing the class from the
   published subset makes it green (E444 family: a conclusion may not rest on rows the face drops).

Both are published in the card as reusable rules rather than described as noise.

## Verification

- `run` rc0, `check` problems=[], `verify` re-derives from the live tree with problems=[].
- `selftest` **28/28**: three path routes, three directory classes, eight class branches, parent
  tally reproduction, and three doctored faces that must go red.
- S6 leg `composed_writer` rc0 0.10 s (`Tools/s6_chain_bmb.py 1512 --only composed_writer`).
- smoke leg `E487 an unwritten latest spelling is attributed to the source that composes its stem
  (r1512 bm-b)` proved 1/1 standalone via `scripts/run_smoke_legs_by_name.py`.

The face on disk before this window was the product of an earlier definition of the module (it
claimed 84/84 traced) and its own `check` failed against the module that shipped with it; it was
re-derived, not patched by hand.