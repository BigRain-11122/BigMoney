# DIGEST 2026-11-04 r1429 bm-b — E410: two stale faces, two freshness forms, and a proof that fires

Card: `E410-GIVE-THE-STALE-FACE-A-BOUNDED-LAG-READER-INSTEAD-OF-NO-READER-AT-ALL`
Face: `results/state_tilt/FRESHNESSBOUND-2026-11-03.json` (+ `freshnessbound_latest.json`)
Prover: `scripts/run_e410_freshness_legs.py` (3/3 cases as expected)
Smoke legs: two module-level blocks appended to `smoke_test.py` (+ helper `_bar_lag_td`)
Chain leg: `freshness_bound` in `Tools/s6_chain_bmb.py` (rc 0, 0.6 s)

## The question

E409 (r1428) priced five reader sites over two faces written only from a session script and found
that **0** of them asks how old the face is. This card is the implementation step, not another
census: put the cheapest honest reader on each face and prove it fires.

## What was built

| face | bound | shape | red when | closes by |
|---|---|---|---|---|
| `results/t35_open_fill_verify.json` | 1 bar | bounded allowance — the same form `smoke_test.py:679-700` already uses for the ETF book page | lag > 1 bar, no `day`, or the face is ahead of the panel | rerun `scripts/t35_open_fill_verify.py` |
| `results/state_tilt/quantityname_latest.json` | 5 bars | one comparison of `evidence_cutoff` against the panel date; the lag is printed on every run | lag > 5 bars, no cutoff, or the cutoff is ahead | rerun `scripts/e321_*` |

Both bounds are counted in **trading days from `data/exchange_calendar.csv`**, never wall-clock
days, so a weekend or a holiday cannot red the suite.

Two forms become the faces answer different questions. The open-fill face verifies one session's
opens against that session's marks: one missed bar already means it describes a different day, and
a hard day gate is excluded by the E185 ruling recorded at `smoke_test.py:593-597` (a day equality
assumed a deployment layout and reddened a healthy non-writer host). The census counts a corpus of
sources, not a bar: its honest red is "the corpus it names is a different corpus", which one
re-derive closes, so a week is the outer bound of the re-derivation cadence.

## The proof

Three cases, each run in a scratch workspace (input faces copied in, never edited):

```
real            open-fill lag 0  -> green ; census lag 2  -> green
stale_openfill  open-fill lag 3  -> RED   ; census lag 2  -> green
stale_census    open-fill lag 0  -> green ; census lag 10 -> RED
input faces untouched (t35=631ba7ee…, quantityname=c104fe92…)
SUMMARY 3/3 cases as expected
```

Each leg is checked in isolation so one red cannot hide behind the other, and the two input faces'
sha256 are compared before and after the whole run — "untouched" is measured, not asserted.

## Three lessons, all measured this window

1. **A reader site written as a line number is a claim about layout, not about the code.** E409's
   `FACES` table held `smoke_test.py:9164/9257/9329`. Inserting 19 lines at the top for the helper
   moved all three; the E306 leg was then classified `dates_the_face_in_a_gate` from whatever sat at
   its old line (E305's `check(...)` call), and the published "0 of 5 readers price the age" became
   a false "1 of 5". Fixed by resolving every site from an **anchor string** and letting `verify()`
   refuse any site whose anchor does not resolve to exactly one line (`resolved_by` is published per
   reader). E409 was then re-derived: back to 0 of 5 — the fixture's verdict, not the one I hoped
   for, and that is the point.
2. **A card's deliverable name can collide with an existing face.** The card said
   `UNFLOORED-<cutoff>`; that is already E409's ledger on the same cutoff, and the first version of
   this runner overwrote it in place (restored from git after a clean `treasure_guard.py prescan`).
   The face is now named for what it measures, and the writer refuses to overwrite a face whose
   published `study` is not its own.
3. **A gate only ever seen green is not yet a gate.** A doctored copy costs a copy; a doctored
   original costs an incident. And run the two legs separately — a single "both pass" case cannot
   tell a live gate from a no-op.

## Dose note (reported, not hidden)

The suite's freshness classifier (`E409._suite_practice`) requires a date token and a comparison
operator **on the same line**. These gates split them (`_fv_lag = …` then `_fv_ok = … <= 1`), so the
new legs do not move `legs_pricing_the_age` (still 6 of 193). That is the detector's shape rather
than a defect, and the counter now undercounts the bounded form — recorded so the next reader of
that number knows.

## Not claimed

- The full smoke suite was launched detached at 10:47 (`results/_smoke_r1429.out`, pid 16344) and
  had not finished at close; the two new legs were exercised stand-alone by the prover and through
  the S6 leg, and those are the only green claims made here.
- The rest of the S6 chain (update_*, panels, scorecards, papers, dashboards) was not re-run this
  window and is not claimed.