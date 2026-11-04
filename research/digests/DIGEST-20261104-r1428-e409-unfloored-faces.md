# DIGEST 2026-11-04 r1428 bm-b — E409: two faces nobody refreshes, five readers that never ask

Card: `E409-DO-THE-TWO-SESSION-ONLY-WRITERS-LEAVE-THEIR-READERS-UNFLOORED`
Face: `results/state_tilt/UNFLOORED-2026-11-03.json` (+ `unfloored_latest.json`)
Study: `scripts/e409_unfloored_faces.py` (run / verify / selftest 12/12)
Chain leg: `unfloored_faces` in `Tools/s6_chain_bmb.py`
Smoke leg: appended to `smoke_test.py`, executed verbatim by `scripts/run_e409_smoke_leg.py` (1/1)

## The question

E408 (r1426) classified the surface that runs each real writer: 12 of 14 run on the standing
round chain, 2 only from a session script — `scripts/t35_open_fill_verify.py` writes
`results/t35_open_fill_verify.json`, and the E321 study writes
`results/state_tilt/quantityname_latest.json`. Both are read by legs of `smoke_test.py`. So on a
round where no session happened to call them, the leg compares against a face nobody refreshed.

E409 asks it per face: how old is it, how many rounds since it changed, what does each reader do
when it is stale, and which fix is cheaper.

## The measurement

| face | age (days since commit) | stale vs panel 2026-11-03 | readers | readers that price the age |
|---|---|---|---|---|
| `results/t35_open_fill_verify.json` | 0.52 | no (`day=2026-11-03`) | 2 | 0 |
| `results/state_tilt/quantityname_latest.json` | 2.76 | **yes** (`evidence_cutoff=2026-10-31`) | 3 | 0 |

Reader tiers (5 sites, block = the leg's own `try:`/`except` span, not a fixed window):

- `smoke_test.py:589` — `prints_staleness_without_gating`. The leg computes the STALE condition,
  prints it, and passes.
- `smoke_test.py:619` — `compares_the_face_to_itself`. It reads `day` only to select rows, then
  validates the tier and the per-trader detail shape.
- `smoke_test.py:9164/9257/9329` — `no_freshness_test`. Three legs re-derive their own numbers and
  compare against the stored ones, so a stale face passes as long as it is internally consistent.

Tree-wide practice: **6 of 192** suite legs that open a face or a page price the age of it
(3.1%). The two faces here are not being held to a standard the file does not already meet
elsewhere — they are being held to one it meets once in thirty-two.

## Verdict (recomputed by the gate)

`a_stale_face_passes_every_reader_that_never_asks_how_old_it_is`

1 of 2 faces is behind the panel; 1 of those has no reader that asks how old it is; 0 of 5 reader
sites ask.

## The part that changes the fix

The card proposed two candidate fixes — a chain leg, or a reader that prices its own staleness.
For `t35_open_fill_verify.json` the reader-side fix is **not available**: `smoke_test.py:593-597`
records that a hard day gate was already litigated and removed, because requiring equality made a
healthy bm-b run red against a bm-a-written dashboard (E185 family: an assertion that assumes a
deployment layout). The same file, 60 lines later, does it correctly for another face — a bounded
**one-bar** lag allowance computed from the exchange calendar, red at two bars
(`smoke_test.py:679-700`). So the honest answer for that face is not "add a check"; it is "add the
bounded-lag form that is already in this file", or put the writer on the chain.

For `quantityname_latest.json` the reader-side fix is genuinely one comparison: the face carries
`evidence_cutoff`, the panel carries the last bar day, and no host-layout ambiguity is involved.

## Instrument lessons

1. A fixed ±N line window bled one leg's evidence into its neighbour's: the dashboard leg's own
   `STALE` print was attributed to the tier leg that begins 30 lines later, so the tier leg was
   classified as "prints staleness" when it never mentions the dashboard. Anchoring the block on
   the enclosing `try:`/`except` — the unit the suite already reports as one leg — fixed it, and
   the first build's tier table was wrong in exactly that one row.
2. `"results/"` as a literal is not "opens a face": `os.path.join("results", ...)` does not match
   it. The narrow rule said **42** legs open a face; the correct rule says **192**, and the share
   of legs that price the age changes from 1/42 to 6/192. Publishing both counts keeps the
   undercount visible instead of letting it become the headline (E409 r1418 family).
3. The study counts the suite it lives in, and this round added a leg to that suite — the practice
   census went 192 → 193 on its own second run. Self-inclusion is excluded by name and the excluded
   count is published (E180/E207/E319 family, third re-occurrence).
4. A guard written to stop the study writing its input was itself wrong: it banned `open(... "w")`
   outright while the study legitimately writes its own deliverable. A guard that cannot tell the
   deliverable from the input is a guard that will be deleted; scoping it to a window around each
   write-mode open made it both true and useful.

## Not claimed

- The full ~305-leg suite was not re-run this window. The E409 leg was appended to
  `smoke_test.py` and executed verbatim from that file by `scripts/run_e409_smoke_leg.py` (1/1),
  plus `selftest 12/12` and `verify problems=[]`.
- `Tools/s6_chain_bmb.py --list` was not used to confirm registration: it produced no output for
  five minutes and was cancelled, so registration is confirmed by reading the leg table
  (`"unfloored_faces"` present, file parses) and by running the leg's exact command, not by the
  runner's own listing.
- No fix was applied to either reader this window. That is the next card's work, and the shape of
  the fix differs between the two faces (see above).