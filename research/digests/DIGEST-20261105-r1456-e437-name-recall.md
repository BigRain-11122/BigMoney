# DIGEST 2026-11-05 r1456 bm-b -- E437: how much of the temp-directory population does the fixture name test see

Card: `E437-WHICH-TEMP-DIRECTORY-WRITE-SITE-THE-NAME-HEURISTIC-MISSES`
Face: `results/state_tilt/NAMERECALL-2026-11-04.json` (+ `namerecall_latest.json`)
Instrument: `scripts/e437_name_recall.py` (selftest 25/25, verify problems=0)

## Question

E428 counts "fixture-shaped" parameter-directory write sites by a word test on the callee name.
E434 counted 30 of 310 sites with the same test and published it as a population statement. A name
test has recall; nobody had measured it against an independently labelled population.

## Answer

| cell | rows |
|---|---|
| temp directory **and** a fixture word in the callee name | 91 |
| temp directory **but** no fixture word (the recall gap) | **112** |
| fixture word **but** no temp directory | 69 |
| neither | 27,437 |
| **directory-parameter call rows** | **27,709** |

Over the 203 call rows that supply a temp directory the name test recalls 91 (**44.8%**); over the
160 rows it names, 91 are temp-supplying (**56.9%** precision). Of the 112 missed rows, 88 come
from a selftest/smoke caller, 16 from a `verify`/`reprice`/`reading`/`rerun` harness inside a
production module, and **8 from callers with no test or verify hint at all**.

Verdict (recomputed from the rows by the gate):
`some_temp_supplying_call_row_the_name_heuristic_misses_is_made_from_a_product_caller`.

Top missed callees: `build` 50, `write` 16, `save` 8, `_write_csv` 8, `_syn_file` 8.

## Two instruments that had to be replaced

1. **Site-level aggregation.** The first build marked a *site* temp when any caller supplied a
   temp directory. Generic writers (`dump`, `save`, `write_json`) have many callers, so a single
   `tmp_path` call made the helper temp-shaped and 108 of 112 "missed sites" read as
   production-reached -- they were ordinary repository writes a test happened to call. The unit
   must be the call row.
2. **Expanded arguments that are payloads.** The argument text is expanded through the caller's
   constants; when the parameter position does not line up the expansion returns a whole payload.
   44 call rows carried a `tempfile` marker inside a payload. The marker test now only counts a
   single-line expression of at most 220 chars, and the rejected rows are published
   (`temp_texts_rejected_as_payload=44`).

## Marker-list blind spot (published, not folded in)

`tmp_path` / `tmp_path_factory` are not in E432's `TEMP_MARKERS`, so a call passing pytest's
fixture is invisible to the temp label itself: **0** call rows in this corpus pass one of those
names, which means the blind spot is not measurable here rather than absent.

## Files

- `scripts/e437_name_recall.py` -- run / verify / selftest
- `results/state_tilt/NAMERECALL-2026-11-04.json` + `namerecall_latest.json`
- `scripts/run_e437_smoke_leg.py` -- 1/1 green, 1/1 red on a doctored verdict, face restored
  byte-identical `f0860814109e4c08`
- `smoke_test.py` leg `# E437 (r1456 bm-b)`
- `Tools/s6_chain_bmb.py` leg `name_recall` (verify ~6 min; chain run cut by the CLI 5-minute
  no-output window, the same verify completed standalone rc=0)
- `knowledge/METHODOLOGY_ASSETS.md` card E437