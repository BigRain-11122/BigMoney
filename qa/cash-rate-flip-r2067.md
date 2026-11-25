# QA — cash-rate flip face (r2067, bm-c)

対象: `scripts/etf_book_cash_rate_flip.py` / `results/etf_book_cash_rate_flip.json` /
`research/ETF_BOOK_CASH_RATE_FLIP.md`

## What the face claims

| claim | value | where it is computed |
|---|---|---|
| the ADMIT flips at this cash rate | **0.917 %/yr** | `facts.flip_rate_c2_pct` (interpolated on the sweep, then re-derived on the engine at ±10 %) |
| today's vehicle | 1.7708 %/yr | `facts.rate_now_pct` (GC001 daily roll on the book's own calendar) |
| headroom | **85.4 bp of rate** | `facts.distance_bp` |
| which gate breaks | C2 (`cagr_gain_pp >= 0.30`) | `facts.binding_gate` |
| cost of a 5-day stale panel | 0.600 bp of annual return per 100 bp of rate error = 60 CNY/yr per million | `facts.gap_cost_bp_of_annual_return_by_100bp`, `gap_cost_cny_per_1m_by_rate_error_bp` |
| bars the published curve cannot price | 2 (2026-11-23, 2026-11-24), idle 15.74 %, **22.12 CNY per million unpaid** | `facts.tail_not_priced` |

## Evidence

| leg | result | file |
|---|---|---|
| offline selftest (pure helpers: crossing, gap cost) | **10/10 PASS** | `python scripts/etf_book_cash_rate_flip.py --selftest` |
| write run | rc0, `verdict=PASS`, 5 gates all true | `results/etf_book_cash_rate_flip.json` |
| re-derive and compare (`--check`) | rc0, face **and** rendered doc block | `--check` prints two CHECK OK lines |
| negative control | **7/7** — moved number → rc3, message says `CHECK FAILED`, message does **not** say `STALE`, restore is byte-identical, restored face is clean | `results/_r2067bmc_flip_negctl.py` |

Gates carried by the face itself:

- `C0_s1_reproduces_published_face` — at scale 1 the sweep must land on
  `etf_book_idle_cash.readings.cagr_gain_pp` to 0.01 pp (it does: gap 0.0000 pp).
- `C1_s0_control_is_the_engine_curve` — at scale 0 the composition must BE the engine curve
  (max relative error 2.2e-16).
- `C2_gain_is_monotone_in_the_rate` — the sweep is monotone, so the interpolation brackets
  a real crossing.
- `C3_flip_separates_the_verdicts` — behavioural: the real `verdict_of` is called at
  `flip*0.90` (0.825 %/yr → `REJECT`, gain 0.27 pp) and `flip*1.10` (1.009 %/yr → `ADMIT`,
  gain 0.33 pp). The crossing is not trusted from algebra.
- `C4_gap_cost_below_one_gate` — the 5-day gap is worth < 1 bp of annual return per 100 bp.

## Honest gaps (not claimed)

- No smoke leg and no S6 leg in this round: the tree is under `rc=3 CONTENTION` (another
  host live in the same checkout), and both of those are shared faces. Recorded as the next
  round's pointer instead.
- The flip rate is a property of this window's gates, not a forecast of the cash rate.
- The gap cost bounds what a rate error can move; it does not say what the missing days
  actually were — the panel cannot answer that, which is why the collector still has to run.
- Thresholds are imported from `etf_book_idle_cash.CRITERIA`, never restated here.
