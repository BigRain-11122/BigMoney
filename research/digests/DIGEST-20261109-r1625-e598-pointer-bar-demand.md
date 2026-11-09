# DIGEST 2026-11-09 r1625 bm-b — E598: no pointer face is asked for a bar it does not carry

Card: `knowledge/METHODOLOGY_ASSETS.md` **E598**. Face: `results/state_tilt/POINTERBARDEMAND.json`.
Script: `scripts/e598_pointer_bar_demand.py` (selftest 36/36, check/verify `problems=[]`).

## Question

E595 priced an alias on **one** pointer face (`results/etf_book_order/latest.json`) and found that no
reader which actually addresses it asks it for a bar. E598 asks the repo-wide version: for every face
named `latest.json`, who names it, who opens it, which keys do they ask of it — and is any of those a
bar the face does not carry?

## Reading (cutoff 2026-11-06)

| quantity | value |
|---|---|
| faces named `latest.json` | **28** |
| (face, reader) pairs, attributed by directory | **1,058** |
| … spelling the full path | 50 |
| … spelling only the basename (unattributable) | 1,008 |
| pairs asking the face for a bar name | **4** |
| … carried by that face | 4 |
| … asked and **not** carried | **0** |
| faces carrying no bar name at all | 3 (`docs/live_book`, `results/e33_ladder_baseline`, `results/regime_matrix_p0`) |
| readers following a pointer redirect | 1 (`smoke_test`, `docs/live_book/latest.json` → its `json` target) |

Verdict: `every_bar_asked_of_a_pointer_face_is_carried_by_that_face`.

The three faces that carry no bar are pointer payloads by design. The single case that first looked
like a silent join — `smoke_test` asking `docs/live_book/latest.json` for `book_decided_at` /
`priced_bar` — asks the pointer **only** for its redirect key `json`; the bar is read one hop later
from the page the pointer points at. That hop is published as its own arm rather than counted as a
missing bar.

## Three defects found in my own census (all fixed in-window, all published)

1. **A dict that NAMES a face is not a payload binding.** `page = {"card": "results/etf_book_production/latest.json", ...}`
   made `page` a "reader" of the card, so `page.get("priced_bar")` was graded as a silent join.
   The binding predicate now accepts only a *path expression* (literal / folded join / f-string) or a
   *loader call* (`json.load/loads/read_text/open/_read_json/_load`).
2. **A derived object's keys are not the face's keys.** `info = _series_tail_delta(series)` followed by
   `info.get("asof")` produced a phantom `asof` demand on `results/paper_export/latest.json`. Loader-fed
   objects and builder results are no longer followed.
3. **A loader fed BY the payload is the redirect target, not the same face.** `_page = json.load(open(_ptr.get("json")))`
   is one hop away; that is where the `docs/live_book` "missing bar" came from.

A first version also collected key *values* as if they were payload names (`x = d.get("k")` adding `k`),
which put `asof` in a payload-name set.

## Pointers

- Attribution must be by **directory**, never by basename: E594 keyed targets by basename and
  attributed readers of other faces to the pointer (E366 family, third occurrence).
- E594's "silent readers" therefore have **no repair target** among pointer faces: the missing field is
  an empty slot nobody orders, not a writer omission. A repair would be unrequested.
- Next card: **E599** — for every pointer face that redirects, is the bar at the far end checked against
  the bar the pointer declares? (`results/state_tilt/REDIRECTBARMATCH.json`.)