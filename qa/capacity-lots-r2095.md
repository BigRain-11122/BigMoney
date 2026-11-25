# QA — idx_fut_carry_capacity_lots (r2095, bm-c)

Date: 2026-11-25T17:5x+08:00 · Machine: bm-c · Verdict: **MARKET_IS_NOT_THE_GATE**

## What the artefact is

`scripts/idx_fut_carry_capacity_lots.py` → `results/idx_fut_carry_capacity_lots.json` →
`research/IDX_FUT_CARRY_CAPACITY_LOTS.md`.

r2094 priced one lot in CNY and ended by naming the hole it left: "1 手以上按首档线性外推，
未验证深度（ETF 书已有容量面，carry 书没有）". The ETF book has answered this shape for a
long time (`etf_book_capacity_edge`, K1 = one day's own order ≤ 1% of the traded slot's ADV,
20-bar median, last 60 sessions). This face applies the same ruler to the carry book, using
the panels the repo already carries (`data/futures_contracts/<PROD><YYMM>.csv`: date, OHLC,
volume, hold), and adds the two readings the ETF book has no analog for: standing position vs
open interest, and the roll-day volume of the incoming contract.

| check | result | evidence |
|---|---|---|
| selftest | **15/15 PASS** | `python scripts\idx_fut_carry_capacity_lots.py --selftest` |
| run | rc0 | verdict `MARKET_IS_NOT_THE_GATE`, evidence cutoff 2026-11-23 |
| check (self-verify) | rc0 `CHECK_OK` | re-derives from the panels + two upstream faces; names what it did not recompute |
| negative control | **7/7 PASS** | `python results\_r2095bmc_capacity_negative.py` |
| N1 empty panel refuses | ok | `DATA_BLOCKED`, never extrapolates one lot |
| N2 halving volume halves lots | ok | adopted lots ratio exactly 0.500 on both products |
| N3 30x desk rung flips the verdict | ok | worst headroom 234x → **7.81x** (< 10 → capacity bites) |
| N4 edited number | ok | rc3 `CHECK FAILED`, and the word **STALE is absent** (r1850: the word is a contract) |
| N5 moved panel digest | ok | rc3 `STALE`, names the window delta |
| N6 the median leg is not the answer | ok | median-ADV leg overstates capacity **2.21x (IC) / 2.17x (IM)** |
| reuse, not rebuild | ok | per-lot carry + notional from `idx_fut_carry_always_on_price.json`, rungs from `idx_fut_carry_sizing_spec.json`, volumes from the contract panels |

## What it decides

| product | binding leg | lots at the 1% line | capital at capacity | desk's largest rung | headroom |
|---|---|---|---|---|---|
| IC | roll day (IC2612 @ 2026-09-14: 46,845 lots) | **468** | 529,145,134 CNY | 2 lots / 2,259,132 CNY | **234x** |
| IM | roll day (IM2612 @ 2026-09-14: 75,215 lots) | **752** | 871,861,442 CNY | 2 lots / 2,318,318 CNY | **376x** |

- Front-contract OI median 170,454 (IC) / 271,976 (IM); 20-bar median volume 103,615 / 163,010;
  turnover volume/OI ≈ 0.67 — a market that recycles two thirds of its standing interest daily.
- The binding leg is **not** ordinary-day trading (1,036 / 1,630 lots) and not standing interest
  (1,705 / 2,720 lots) but the day the front identity migrates. Spreading a roll over three
  sessions lifts the same ruler to 1,640 / 2,615 lots — roll rhythm is free capacity.
- Money at capacity, printed per carry ruler (never a single number): IC 54.5–54.6M CNY/yr on
  calendar/strictest, 15.6M on published; IM 98.9–102.9M vs 49.4M on published.

## What it does not decide (honest)

- **Impact cost.** Daily bars carry no depth; the face stops at "share of the thing you must
  trade" and never prices taking it.
- **The 1% line is a rule, not a measurement.** 0.5/1/2/5% ladder is in the JSON; anyone with a
  different line can read it proportionally.
- How much of OI is actually tradable (hedgers, market makers and speculators are mixed) is
  unknowable from this panel.
- Only IC/IM; IF/IH have thinner basis and different flow, untested.
- Capital is linear in lots (rung 2 = exactly 2× rung 1 in the published sizing face); portfolio
  margin netting is untested.
- Capacity being large says nothing about the rate being stable — r2094's ruler problem
  (5.9–6.9pp swing) still stands; this face must not be read as "the book pays X%".

## Not done in this window (contention)

`repo_write_contention --lookback-min 45` = rc3 CONTENTION (peer interactive host pid 93460,
started 15:54, still writing shared faces). Per r1907 only new-file surfaces landed: no S6
chain, no full smoke, and **state/heartbeat not written** this window (precedent = r2092 /
r2093 / r2094). The face has no chain leg and no smoke leg yet — wiring requires editing
`Tools/s6_chain_bmc.py` and `smoke_test.py`, both shared faces under contention.
