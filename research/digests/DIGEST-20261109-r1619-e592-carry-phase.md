# DIGEST 2026-11-09 r1619 bm-b — E592: the ledger's carry is reproducible, but the phase is a class, not a point

**Round**: 1619 (bm-b). **Card**: E592, closed. **Face**: `results/etf_book_forward/CARRYPHASE.json`.
**Script**: `scripts/e592_carry_phase.py` (selftest 38/38, check/verify `problems=[]`, standalone
smoke leg PASS and 1/1 red under `--doctor`). **S6 leg**: `carry_phase` (rc0, 0.59s).

## Question

E591 (r1618) replayed the shipped `ladder3` from a fresh contract phase over the ledger's eleven
published bars and reproduced only four of the eight bars past the repo panel. It named the cause
("the contract phase is state, and neither face publishes it") but never measured whether *some*
phase reproduces the published carry — nor how much of the phase the published bars actually pin.

## Reading

| arm | reproduced at the printed precision | at 0.5% | max abs gap |
|---|---|---|---|
| replay from the reconstructed origin **2020-01-02** | **11 / 11** | 11 / 11 | **0.000755%** |
| fresh phase at the ledger's first published bar (E591's arm) | **0 / 11** | 6 / 11 | 416.2% |
| printed precision of the `carry` field itself (`round(...,10)`) | — | — | **0.001302%** |
| phases tested (41³ three-rung offsets) | — | — | **68,921** |
| phases reproducing every bar at 0.001% | — | — | **52,111 (75.6%)** |
| bars no phase in the window explains | — | — | **0** |

Per-rung marginal sweep (offset 0..250 bars from the origin, the other two rungs at the origin):

| rung | offsets reproducing every bar | reading |
|---|---|---|
| GC007 | **251 / 251** | offset-invariant on this window |
| GC014 | **251 / 251** | offset-invariant on this window |
| GC028 | **168 / 251** | the only rung whose phase the bars constrain |

## Where E591's 4/8 came from

`etf_book_forward.build_carry(dates)` is called with `date_grid(px, rebal)` — the writer's **whole**
grid, 2020-01-02 → 2026-11-06, 1,658 bars — not with the eleven bars the ledger publishes. So the
contract phase is anchored 1,647 bars before the first published bar, and a replay that starts at
the first published bar is starting a *different* ladder. Restricted to the eight bars past the
panel, that fresh-phase arm reproduces exactly **4 of 8** at 0.5% — E591's number, recomputed here.

## What the reader needs, and what the face gives

The state a reader needs is the **replay origin** — the bar at which every rung's first contract is
entered. The face does not print it, but it is recoverable: `seed.bar` (2026-10-23) minus
`seed.grid_index` (1647) lands on the grid's first bar. That reconstruction is checked against the
live calendar in `published_phase`, and it is the difference between 0/11 and 11/11.

It is also **not necessary** to have that exact origin: 75.6% of the sampled phases reproduce every
published bar, because two of the three rungs are offset-invariant on a panel whose tail is
forward-filled and all of the discrimination sits on the 28-day rung's open-contract entry quote
(2026-10-21 at 1.365%; a phase that opens on 2026-10-14 at 1.39% is 1.8% high on every bar).

## Traps this study had to disarm

- **Tolerance is part of the claim.** At 0.5% the origin arm reproduces 11/11 and so do 75.6% of all
  phases; at 0.001% the origin arm still reproduces 11/11 but the fresh-phase arm reproduces 0/11.
  Publishing one tolerance would have read as "phase doesn't matter" or "phase is everything".
- **A residual has to be priced against the field's own precision.** 0.000755% sounds like an
  unexplained remainder until you notice the carry is printed to 1e-10, i.e. 0.001302% of a 1.1e-5
  figure. The residual is the rounding, not unknown carry.
- **Failing phases fail on every bar at once.** All 16,810 failing combos miss the same bars, so a
  per-bar table cannot localise the phase — the bar counts are identical across bars by
  construction, not by coincidence. Measured as `every_failing_phase_misses_the_same_bars`.
- **Reproducible ≠ identifiable.** The card asked for "the best-fitting phase per rung"; the honest
  answer is an equivalence class (two rungs unconstrained, one constrained to 168 of 251 offsets),
  published as ranges rather than as a single winning offset.

## Evidence

`scripts/e592_carry_phase.py` · `results/etf_book_forward/CARRYPHASE.json` ·
`scripts/run_e592_smoke_leg.py` (PASS / doctor RED) · `smoke_test.py` leg `E592` ·
`Tools/s6_chain_bmb.py` leg `carry_phase` · card `E592` in `knowledge/METHODOLOGY_ASSETS.md` ·
pool: E592 done, E593 seeded (does the ticket's advertised cash yield survive its own 252-bar
convention).