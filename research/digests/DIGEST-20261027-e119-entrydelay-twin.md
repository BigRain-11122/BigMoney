# E119 — the entry-delay ladder under the split repair (the first DELEGATING twin)

Face: `results/e44_midmonth/ENTRYDELAYSCREEN-20261027.json`
Code: `scripts/e39_panel_census.py` → `run_entrydelayscreen` / `_entrydelay_arm_cells` /
`_lag_ladder_read` / `_delegation_attribution` (selftest 380 → 393/393).
Ticket: E119-ENTRYDELAY-SCREENED-TWIN. Arm: raw `e27.load_universe()` vs
`panel_screen.screen_universe(mode=neutralise_int)` — 67 names touched, 67 integer-like
events neutralised, 34 gapped kept, 1,317 names in / 1,317 out.

## What is new about this twin

`run_entrydelay` measures nothing itself: it calls `run_midsweep` and republishes that
face's `me_lagK` arms as `answers.delay_rows`. So the arm seam has to be threaded through
**both** layers (`run_entrydelay(raw=…)` → `run_midsweep(raw=…)`), and a delta on this
face has two possible owners. The join therefore harvests the copy layer (`delay/…`) and
the delegated layer (`gap/…`) separately and names which one moved, plus a copy-vs-source
invariant checked on each arm **before** any delta is read.

## Numbers

| | cells |
|---|---|
| compared | 93 |
| moved | 50 (12 copy, 13 source, 18 book, 7 answers, 0 other) |
| max abs delta | 15.0 bp — `gap/me_lag10/era/2021_2023` (−74.0 → −59.0) |
| same-arm control | 0 moved, max 0.0 |
| one-sided cells | 0 |
| nulls | 13 — all pre2017 (no bars at start 2020-01-01, empty in both arms) |
| copy == its own arm | **true on both arms** |
| attribution | both layers moved = the ladder itself changed |
| cutoff control (ENTRYDELAY-20261020, raw vs raw) | 39 moved, max **6.0** bp |

**The repair dominates the cutoff axis here** (15.0 vs 6.0 bp) — the reverse of E118,
where the cutoff control was an order of magnitude *larger* than the repair. Same family,
opposite conclusion, which is why each face carries its own controls instead of inheriting
a house rule.

## The reading: the ladder's shape is arm-dependent, its sign is not

Newest era (`2024_now`), gap in bp at 1 / 3 / 5 / 10 sessions:

| arm | rungs | shape | span |
|---|---|---|---|
| raw | −42, −74, −73, −90 | **monotone** | −48 |
| screened | −41, −70, −64, −85 | **non_monotone** | −44 |

Every rung stays negative and the span barely moves (−48 → −44), so *"lateness is priced
in the newest era"* survives the repair. *"Each extra session costs more"* does **not**:
the repair improves the lag-5 rung by 9 bp (2.3% of the −73 it replaces, and 1.8× the
5 bp it gives the lag-10 rung), so the ladder now dips and then deepens.

The mechanism is visible in the per-rung deltas — the repair moves all four rungs in the
same direction (cheaper lateness: +1 / +4 / +9 / +5 bp), but **not proportionally in k**.
A repair that is not monotone in k cannot preserve a monotone ladder, however small it is.

Full window is `non_monotone` on **both** arms (the lag-3 rung is a relief: −26 → −17 raw),
so the full-window ladder never had the shape the newest era has. Quoting "a cliff" from
the full-window column would have been wrong before the repair too.

## Where the cells move

- 10 of 50 moved cells are `book/*/era/*/ann_return_pct` — the delayed book's own annual
  return, i.e. the repair changes what a *late* book earns, not just its gap.
- The `2021_2023` era moves hardest (lag10 −74 → −59 = 15 bp) and that era's lag-3 gap is
  **positive on both arms** (+23 → +21): in 2021_2023 a three-session delay beat month-end.
  A ladder read only at the newest era would never surface that.

## Honest limits

- Four fixed lags (1/3/5/10), 2 bp shape tolerance — a description, not a fitted curve.
- The lag moves the decision session too, so a repair that changes *which name is picked*
  on a delayed date changes the ladder by construction; this cannot separate "same names,
  later" from "different names".
- `pre2017` is empty by construction at start 2020-01-01 (13 null cells, both arms).
- Descriptive census: no gate, no prereg, no trial count.

## Method card

`knowledge/METHODOLOGY_ASSETS.md` E157 — *a delegating runner's twin must split the copy
from the source and check the copy invariant on each arm*.