# DIGEST 2026-11-01 r1344 (bm-b) -- E324: where the six "unpublished" keys actually live

Study: `scripts/e324_unpublished_key_causes.py` (selftest 28/28, verify 0 problems)
Face: `results/state_tilt/UNPUBLISHEDKEY-2026-10-31.json` (+ `unpublishedkey_latest.json`)
Upstream: `results/state_tilt/REACHWIDE-2026-10-31.json`, class `producer_found_but_publishes_no_such_key` (6 rows)
Card: `knowledge/METHODOLOGY_ASSETS.md` E324. Pool: E324 done, E325 seeded.

## The question

E321 classified the 196 unresolved gates by reading their producers. Six came back as "a producer is
found, but it publishes no key of that name". E323's wider needle moved 25 rows and left these six
untouched: they were never a needle problem. The pool card asked the only question left -- is the key
written under another name, copied in from a sub-face, or genuinely absent from the writer?

## The answer

| cause | rows | evidence |
|---|---|---|
| copied wholesale from a sub-face writer | 4 | `etf_book_spanning_pre2020.py:123` `"tolerance_pp": TOL_PP` against `results/etf_book_spanning_pre2020.json`; `etf_book_window_decomp.py:194` `"tolerance_pp": CONTROL_TOL_PP` against `results/etf_book_window_decomp.json`; both faces copied into `PRODUCTION-2026-10-27/28.json` by `"control": doc.get("control")` / `"controls": doc.get("controls")` |
| the key is a data value | 1 | `e299_rounded_vs_tolerance_census.py:646` `by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1`, published at `:663`; no literal `epsilon` key exists |
| no source mentions the key at all | 1 | `summary.by_verdict.tolerance_silently_defaulted` in `PRECISIONCENSUS-2026-10-30.json`, while no `.py` under scripts/Tools/live/monitor/firm contains the string |

Verdict: `five_of_the_six_keys_are_published_by_a_writer_and_the_sixth_is_a_face_no_committed_writer_can_reproduce`.

## Identity, not assertion

* Sub-face copies: the face value equals the sub-face value at the same path (0.5 == 0.5, four checks).
* Data key: `by_kind["epsilon"] = 39` re-counts to the 39 rows of `PRECISIONCENSUS-2026-10-29.json` whose `kind` is `epsilon`.
* The population is not hand-typed: it is `REACHWIDE`'s own `class_after`, and the smoke leg refuses a population that differs from upstream.

## Blind spot

16 of the 196 census rows sit inside a block their face writer copies from another face (signature:
`"<component>": <expr>.get("<component>")` on a component of the gate's own path). The composition
blind spot is therefore ~8 pct of the population, not a one-off.

## What was wrong in the tools (both permissive)

1. `e321.writes_the_face` accepted any line carrying `open`, so a module that READS a sub-face
   (`with open(DEC, "r") as fh: json.load(fh)`) was credited as its writer. First run of this study
   therefore attributed the window-decomposition key to `etf_book_pre2020_wf.py` (a composer), not to
   `etf_book_window_decomp.py` (the writer). Fixed with `owns_face`: the name assigned the face path
   must be opened in a write mode.
2. A string on a line carrying `=` is not a key. `kind = "epsilon"` uses the same text as a value.
   E321's detector would accept it; `shape_of` accepts only a mapping key (`"k": v`) or an item
   assignment (`d["k"] = v`). Both directions are fixture legs.

## Orphan face -- the finding worth following

`results/state_tilt/PRECISIONCENSUS-2026-10-30.json` was generated `2026-10-31T13:45:22` and
committed at r1324 (`9f8f42076`, 14:24). Its summary block carries keys (`by_verdict`, and
`by_tolerance_source`, `comparisons_with_a_printed_copy`, ...) that the committed `e299` does not
produce: `git log -S "by_verdict" -- scripts/e299_rounded_vs_tolerance_census.py` is empty, and the
current script writes the *10-29* schema (`legs_in_smoke_test`, `n_numeric_face_sites`, ...). So the
committed artifact was written by a session-local variant of the script that was never committed.
A published face is evidence only if the tree can reproduce it; this one cannot.

Seeded as E325: count, over the whole 196-gate population, how many gate keys no source mentions at
all -- an orphan face is a face-level defect, not a naming defect.

## Not run this round

Full smoke suite not re-run (~30 min); the new leg (330th) was extracted and executed standalone:
PASS. S6 leg `unpublished_key_causes` rc=0 in 6.1s. GPU untouched (parked, C-20261014-01). Cloud
untouched. Nothing deleted, no quarantine action.