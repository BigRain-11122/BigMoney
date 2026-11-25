# QA — the ladder's year arithmetic (r2107, bm-c)

Round: r2107 | host: bm-c | window: **CONTENTION** (`results/_repo_write_contention.bm-c.json`, rc3)
Product: `scripts/idx_fut_carry_ladder_years.py` → `results/idx_fut_carry_ladder_years.json`
Page: `research/IDX_FUT_CARRY_LADDER_YEARS.md`

## What the round adds

The carry ladder's faces so far priced the whole 1052-bar sample as one block (vol, Sharpe,
drawdown, worst month, underwater run). None of them said **which years produced the money**, so a
book that earns everything in one year and a book that earns it evenly printed the same headline.
This face splits every rung's series by calendar year, prints the realised compound of each year,
the best year's share of the compounded growth, the same book with the best year removed, and a
per-year attribution of the return into equity-sleeve / IC-leg / IM-leg pieces.

## Verification (all run this window)

| check | command | result |
|---|---|---|
| selftest | `python scripts\idx_fut_carry_ladder_years.py --selftest` | **OK 25/25** |
| face self-consistency | `... check` | **CHECK_OK** (16 rungs, 5 years; every year table compounds to its own full-period CAGR) |
| negative control | `python results\_r2107bmc_ladder_years_negative.py` | **ALL_CONTROLS_PASS 10/10** |
| word discipline | in the control | tampering ⇒ `CHECK FAILED` **without** the word `STALE`; upstream drift ⇒ `STALE` |
| cross-face | face `cross_face` block | rung 1/1 rebuilt here **26.67 %/yr** vs published 22.34 %/yr — the 4.33 pp is the sibling face's `k²` sleeve weight, recorded not repaired (shared face, contention window) |

## Controls, one by one

1. untampered face passes;
2. a published year return moved by 1 pp ⇒ CHECK FAILED;
3. a year row deleted ⇒ CHECK FAILED (bar count and compound both break);
4. judgment token flipped ⇒ CHECK FAILED;
5. money column moved 5,000 CNY ⇒ CHECK FAILED (tolerance is the face's own publishing precision, 5.02 CNY = half an ulp of 3-dp percent);
6. stored loss-year list contradicting the year table ⇒ CHECK FAILED;
7. upstream lattice digest moved ⇒ STALE;
8. ex-best cost positive and ex-best CAGR below full (the reading is not vacuous);
9. the cross-face gap is disclosed, not silently reproduced.

## Findings the reader gets

* instructed rung 1/1: **26.67 %/yr**, best year 2025 (+52.55 %), which supplies **41.4 %** of the
  compounded growth; without its bars the same book earns **19.73 %/yr** ⇒
  `SOME_YEARS_CARRY_MORE_THAN_OTHERS` (26.0 % of the CAGR).
* **no calendar year in the sample lost money** on any rung; the instructed rung's worst year is
  2023 at **+10.65 %**.
* per unit of risk the in-band rung's worst year is better (return/vol 0.905 vs 0.758) — the raw pp
  comparison would have said the opposite, because the two rungs are differently sized books.
* 2025's 42.98 pp summed = sleeve 15.90 pp + IC 12.36 pp + IM 14.71 pp: the sleeve is the piece
  every rung shares, the lot count is what varies.

## Not done (honest)

* `Tools/s6_chain_bmc.py` and `smoke_test.py` wiring — both are shared faces held dirty by the
  other host this window (r1907 same-tree multi-host rule). The face is check-only and autonomous.
* the r2105 `k²` repair, and regenerating the three 11-23 carry faces — shared face writes, same
  reason.
* full suite not run (570+ legs, contention window).
* `state-bm-c.json` / heartbeat untouched: multi-host co-written faces.

## Round-internal self-catches

1. worst-year comparison first written on **raw pp**, which called a better-per-unit-of-risk book
   "not better" — the rungs are differently sized, so the comparison is now return/vol with a
   stated tolerance.
2. `check` first used a 1-CNY money tolerance against a 3-dp percent column and red-ed its own
   correct face; the tolerance is now derived from the published precision and says so.
3. the selftest printed a hard-coded `12/12` while running 25 legs — the count is now counted.
