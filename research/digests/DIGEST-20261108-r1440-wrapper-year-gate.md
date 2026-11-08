# DIGEST 2026-11-08 r1440 (bm-c) — the gate judges a book nobody holds

**Question r1438 left open, and this round closes:** does the execution wrapper
(beta-0.20 overlay + GC001 cash leg) change the calendar verdict — and is the thing
the desk actually accrues even the thing that was wrapped?

**Tool:** `scripts/etf_book_wrapper_year_gate.py` (selftest 8/8, `--check` 15/15,
run 49s rc0). Prices nothing new: reuses `R.open_to_open_equity`, `E.run_next_open`,
`BT.k_schedule`, `BT.apply_overlay`, `BW.repo_daily_cash`, and adjudicates through
`candidate_year_gate.admission_block` (all imported).

## Reading (window 2020-07-17 .. 2026-11-06, 7 calendar years, 2026 partial)

| arm | verdict | top-2 year share | annual sum | median yr | worst yr |
|---|---|---|---|---|---|
| plain book `n5_r20_vt08` (what the calendar judges) | CONDITIONAL | 75.74% | 76.07% | 5.47% | 0.62% |
| judged book + wrapper | CONDITIONAL | 75.88% | 75.93% | 5.47% | 0.48% |
| **ticket construction** (untargeted book + overlay + repo) | **ADMIT** | **67.52%** | 44.32% | 3.49% | 2.10% |

1. **The wrapper is inert on the object the gate judges.** The 8% vol target already
   holds the book's beta at ≈ 0.20, so `k = 0.20 / beta` clips to **1.0 in every year
   from 2021 on** (2020 partial: 0.944). Yearly returns are identical bar for bar
   except 2020; top-2 share moves 75.74% → 75.88%, i.e. *worse*. Putting the judged
   book through the wrapper answers the r1438 question with "no change".
2. **The arm the ticket accrues is a different book, and it ADMITs.** `etf_book_order`
   wraps the *untargeted* book (`F.run_next_open`), whose beta ≈ 0.43, so the same
   "beta 0.20" instruction lands at k = 0.23 (2020) → 0.46 (now, ticket `k_now`
   0.460253, reproduced here to 0.0038). That curve passes Y4 at 67.52%.
3. **That pass is 2.5pp wide and it leans on a partial year.** Excluding the partial
   2020 the same arm reads 77.57% — a fail. The gate's `top2_share` includes partial
   years; the ticket arm passes only because the partial year dilutes the sum.
4. **What the pass costs.** The executable arm earns 44.3% of summed yearly returns
   against the judged book's 76.1%, with median year 3.49% vs 5.47%. It buys the
   concentration line with exposure, not with selection.

## Why this is a defect and not a fix

The desk has two objects and one ruler. The calendar refuses `nobond_vt08_adopted`
(CONDITIONAL, `years_for_half` 2 vs line 3) 40+ rounds running, while the money is in
a *different* construction that has never been judged — and when it is judged here, it
passes on a technicality about partial years. Either the gate should judge the object
that runs, or the ticket should run the object the gate judges. Today neither holds.

## Method lessons (card E445)

- **A wrapper that cannot move `k` is not a wrapper.** Before judging a "wrapper", print
  the distribution of the knob it turns. Here k = 1.0 for six of seven years — the
  wrapper only ever had a job on 2020 and never had one since.
- **"Same instruction, different series" is a construction bug that hides as agreement.**
  Both routes honestly say "beta 0.20"; one of them means owning 100% of a vol-targeted
  book, the other 46% of an untargeted one. The identity proof has to be the *series*
  (k reproduced to 0.0038), not the parameter name.
- **Pure scaling cannot fix a concentration verdict** (selftest L3a: halving every year
  leaves `top2_share` bit-identical); only a flat carry moves it, and it moves it by the
  arithmetic of the four years. Any claim that de-risking "fixed" Y4 must name which of
  the two happened.

## Not verified / not wired

- Not wired into S6: 49s runtime would land on every 10-minute round. Receipt is
  `results/etf_book_year_gate/WRAPPER-GATE.json`; `--check` (0.1s) is available for a
  future chain leg once the runtime question is answered.
- Not verified: what the 2026-11-11 rebalance will actually hold; whether the
  `crossborder` class in the ticket maps to any class the calendar understands.