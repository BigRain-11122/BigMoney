# The ETF book's cash leg: what the tenor is actually worth

`scripts/etf_book_cash_ladder.py` → `results/etf_book_cash_ladder.json` +
`results/etf_book_cash_ladder/CASH-TICKET-2026-10-19.json`
(r1258, exploratory — no preregistration, no verdict, no ledger booking)

## The two assumptions this removes

r1255 replaced the flat "2% cash" guess with the observed GC001 panel and got **2.088%/yr**.
That number carried two holes:

1. **no commission.** Exchange repo charges per contract; rolling overnight 252-365 times a
   year is not free. With the fee schedule in `FEE_BP` the same 1-day leg pays 2.023% gross
   and **1.777% net** — a 0.246pp/yr drag, i.e. r1255's cash leg was about 12% too rich.
2. **one tenor only.** Overnight is the cheapest tenor to model, not the best one to hold.

`repo_daily/` has all 11 tenors on disk (SH GC001..GC182, SZ R-001/003/007). This note prices
six policies over 2020-07-16 .. 2026-10-19 (1,516 bars against the book's 2026-10-23 cutoff:
the repo panel is **4 bars stale**, refreshed by the bm-a lane — disclosed, never ffilled).

## Mechanics that are not negotiable (all selftested, 12/12)

* a contract is **never exited early** — a 60% one-day rate printing inside a 28-day contract
  changes nothing (leg 3);
* the rate is the quote at the **close of the entry bar** (leg 5: rewriting the future moves
  no earlier contract);
* interest = rate/100 x **calendar** days / 365, so Friday's 1-day contract earns three days
  (leg 2) — this is where a 252-day model of a 365-day market goes wrong by ~30bp;
* a missing quote accrues nothing and is counted (leg 9);
* the 1-day leg reproduces r1255's `repo_daily_cash` accrual **exactly** (leg 11, diff 0.0),
  so the comparison against the previous answer is pinned, not asserted.

## The curve is nearly flat, and the fee is a rent

| tenor | mean quote | rolls/yr | commission bp/yr |
|---|---|---|---|
| GC001 | 1.977% | 365.0 | 36.5 |
| GC003 | 1.980% | 121.7 | 36.5 |
| GC004 | 2.005% | 91.2 | 36.5 |
| GC007 | 2.077% | 52.1 | 26.1 |
| GC014 | 2.081% | 26.1 | 26.1 |
| GC028 | 2.085% | 13.0 | 26.1 |

28 days of term buys **11bp** of quote, and the commission is roughly proportional to the
holding period, so every tenor pays ~26-37bp/yr of rent. That is why the ladder's value is
fee efficiency, not yield: 1-4 day tenors cost 36.5bp/yr of commission, 7-28 day tenors
26.1bp. GC028 is the highest-yielding capped tenor on 44.5% of bars, GC014 on 19.7%,
GC007 on 18.7%, GC001 on 13.3%.

## Six policies, net of commission

| policy | net %/yr | gross %/yr | contracts | max lock | longest gap without a maturity |
|---|---|---|---|---|---|
| gc001 (the r1255 leg) | 1.777 | 2.023 | 1,515 | 11d | 11d |
| short_pick (best of 1/3/4/7) | 1.851 | 2.108 | 400 | 15d | 15d |
| ladder4 (1/7/14/28) | 1.851 | 2.107 | 2,069 | 34d | 11d |
| capped28 (best of ≤28d) | 1.863 | 2.125 | 133 | 38d | 38d |
| **ladder3 (7/14/28)** | **1.875** | 2.135 | 554 | 34d | 15d |
| best_gc (best of 1..182) | 1.987 | 2.119 | 41 | **182d** | 182d |
| best_dual (GC+R) | 1.988 | 2.119 | 41 | 182d | 182d |

Three reads:

1. **ladder3 is the best policy a monthly-rebalanced book can use**: +0.098pp/yr over the
   1-day roll, positive in **7 of 7 years** (2.475/2.256/1.890/2.244/1.850/1.481/1.255 vs
   2.335/2.143/1.825/2.182/1.733/1.420/1.076), with a maturity every ≤15 days and 34 days
   of worst-case lock.
2. **the 182-day lock buys +0.11pp more and is not worth it** for a sleeve that is supposed
   to be the book's dry powder; the whole cash leg is a ~1.8-2.0% instrument, so the
   difference between the best and worst policy is 21bp/yr.
3. **the Shenzhen leg adds exactly nothing** — `best_dual` and `best_gc` are identical, in
   whose company, mixed tenor ranks and counts. R-001/003/007 never win a roll. Retire them
   from any future selector work.

## What it is worth on the book

At beta 0.20 the r1255 grid holds a mean k of 0.541, so 45.9% of NAV sits in the cash leg.
Multiplied out: ladder3 = **+0.045pp/yr on the whole book**, the 182-day lock +0.097pp. Both
are honest and both are small — the cash leg is a 2% instrument and no tenor choice turns it
into a 3% one.

## Quarter-end spikes are real but not reachable without giving up the ladder

Mean quote on the last three trading days of a quarter vs other days: GC001 3.032% vs 1.920%
(peak 7.83% on 2023-03-31), GC007 2.725 vs 2.041, GC014 2.378 vs 2.065, GC028 2.166 vs 2.081.
The spike decays with tenor almost exactly as fast as the lock costs, so a "park in overnight
over quarter-end" overlay is a future note, not a free lunch already in hand.

## Today's instruction (as of the panel's last bar)

`CASH-TICKET-2026-10-23.json` (refreshed r1259): four rungs of 11.5% of NAV each
(GC001 1.015% / GC007 1.33% / GC014 1.35% / GC028 1.35% → roll at each maturity), blended
quote ≈1.261%, next roll per rung at the first bar at/after each maturity. The repo panel
(owner `update_repo.py`, T-88) is now level with the equity book at 2026-10-23; when it
falls behind again, refresh it with `--takeover` only if the owner heartbeat is genuinely
stale (see the section below).

## Limits

* commission schedule is an assumption (exchange table, not re-verified against a broker page
  in this window); rerun with `--fee=0` for the gross read;
* lot granularity, T+1 settlement and the ticket's 0.1%-of-NAV residue are ignored;
* interest is spread evenly inside a contract (contract totals exact, intra-contract shape
  smooth);
* no intraday execution model: entry uses the entry bar's close;
* survivorship does not apply here (repo tenors are index-like), but the equity book's
  survivorship caveat still covers everything the cash leg finances.

## r1259 refresh: the lane came back, the numbers did not move

The panel behind every number above was 4 bars behind the equity book (last repo bar
2026-10-19 vs equity 2026-10-23) because `update_repo.py` had no way to act when its owner
went silent — the r1101 silent-rot class, one lane over. That gap is closed: the script now
carries a declared stale-takeover leg (explicit `--takeover` AND owner heartbeat >= 120 min
stale, the decision imported from `update_etf_daily`, never re-implemented). bm-b's
heartbeat was 68.9 h old, so the leg fired, pulled 11/11 tenors (+4 rows each, zero failures,
zero overlap mismatches, cutoff 2026-10-19 -> 2026-10-23), and the whole ladder was
re-derived on the extended panel.

The re-derivation is the useful part, because it is a reproducibility ruler rather than a
new result:

| model | net 2026-10-19 | net 2026-10-23 | delta |
|---|---|---|---|
| gc001 | 1.777% | 1.775% | -0.002 |
| short_pick | 1.851% | 1.849% | -0.002 |
| ladder3 | 1.875% | 1.873% | -0.003 |
| capped28 | 1.863% | 1.863% | -0.001 |
| best_gc / best_dual | 1.988 / 1.987% | 1.986 / 1.987% | -0.001 |

Four real bars move every policy by at most 0.3 bp, the ranking is unchanged, and the book
uplift stays +0.034 / +0.040 / +0.045 / +0.097pp exactly as rounded before. The staleness
flag `repo_panel_stale.behind_book_bars` went 4 -> 0, so the cash leg is no longer a stale
quote riding under a fresh equity book.

What the new bars do say is about the level, not the policy: overnight softened while the
term end held. October 2026 GC001 averages 1.235% (12 bars, min 0.890 on 10-22) against
1.325% in September, and the last four bars average 1.167% vs 1.181% for the four before,
while GC007/014/028 gave up only 1.0-1.9 bp over the same window. Read forward, that widens
the ladder's current edge: at October's realised quotes ladder3 nets 1.118%/yr against
0.989% for the overnight roll (+13 bp, versus +9.8 bp on the full-sample average), i.e.
0.513pp vs 0.454pp on NAV at the 45.9% cash share. The ladder's value is not a fixed 10 bp —
it is whatever the overnight curve gives up, and right now it is giving up a little more.

Refresh procedure (repeatable, no clock fields in the verdict): `python scripts/update_repo.py
--takeover` then `python scripts/etf_book_cash_ladder.py`; the ticket file name follows the
panel's last bar, so a refresh never overwrites a past ticket.