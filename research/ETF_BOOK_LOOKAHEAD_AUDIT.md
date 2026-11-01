# The card's headline trades one bar of the future

`2026-11-01T13:20:18+0800` · evidence cutoff **2026-10-30** · 1504 symbols · 5270 bars

## Verdict

**LOOKAHEAD_PRESENT** — the published engine ranks on `score.loc[d]` -- built from bar d's own close and amount -- and then earns open[d]->open[d+1]: the book buys at a price that was set before the information it ranks on. Delaying that information one bar costs 1.14 pp/yr, and the whole ladder is monotone in delay (-2:+15.98, -1:+12.46, +0:+9.60, +1:+8.46, +5:+7.39, +20:+5.09)

## The three arms

| arm | cagr | sharpe | maxdd | vol | bars |
|---|---|---|---|---|---|
| published (card) | 9.60% | 0.990 | -11.77% | 10.17% | 1652 |
| causal (score shifted +1 bar) | 8.46% | 0.874 | -16.56% | 10.28% | 1652 |
| ledger engine, no carry | 8.53% | 0.898 | -13.57% | 10.05% | 1653 |
| ledger engine, ladder3 carry | 9.12% | 0.955 | -13.26% | 10.05% | 1653 |

## The lag ladder — the same rule, moved in time

Negative lag = the score is given bars of the *future*; positive = the book is asked to trade on older information. Nothing else changes (same panel, ranking, cost, overlay).

| lag (bars) | cagr | sharpe | maxdd |
|---|---|---|---|
| -2 | 15.98% | 1.532 | -13.35% |
| -1 | 12.46% | 1.275 | -11.02% |
| +0 | 9.60% | 0.990 | -11.77% |
| +1 | 8.46% | 0.874 | -16.56% |
| +5 | 7.39% | 0.766 | -16.66% |
| +20 | 5.09% | 0.544 | -17.64% |

## Decomposition

- price of the one bar: **1.14 pp/yr**
- mark basis (open-to-open vs close-to-close): -0.07 pp/yr
- repo carry credited by the ledger, absent from the card: 0.59 pp/yr

the three components are priced on separate arms: the first is information ordering, the second is open-to-open vs close-to-close marking around an open fill, the third is the repo ladder the ledger credits and the card does not

Bar level — published vs causal: 1651 overlapping bars, max daily difference 0.0167 at 2025-08-25.

## What is affected

Scripts that price through this ordering (mechanical scan, 33 files):

- `scripts/etf_book_bakeoff.py`
- `scripts/etf_book_bridge.py`
- `scripts/etf_book_buffer_adoption.py`
- `scripts/etf_book_cagr_reconcile.py`
- `scripts/etf_book_concentration.py`
- `scripts/etf_book_cost_tape.py`
- `scripts/etf_book_forward.py`
- `scripts/etf_book_hysteresis.py`
- `scripts/etf_book_lookahead_audit.py`
- `scripts/etf_book_nav_envelope.py`
- `scripts/etf_book_pair.py`
- `scripts/etf_book_passive_mix.py`
- `scripts/etf_book_phase_atlas.py`
- `scripts/etf_book_pre2020_wf.py`
- `scripts/etf_book_production.py`
- `scripts/etf_book_sleeve_gate.py`
- `scripts/etf_book_sleeve_paths.py`
- `scripts/etf_book_spanning.py`
- `scripts/etf_book_spanning_pre2020.py`
- `scripts/etf_book_split_audit.py`
- `scripts/etf_book_stagger_publish.py`
- `scripts/etf_book_tsmom.py`
- `scripts/etf_book_vol_window_phase.py`
- `scripts/etf_book_voltarget_lag.py`
- `scripts/etf_book_width_cross.py`
- `scripts/etf_book_width_null_production.py`
- `scripts/etf_book_window_decomp.py`
- `scripts/etf_nobond_vt.py`
- `scripts/etf_robust_pf.py`
- `scripts/etf_vol_calibration.py`
- `scripts/etf_vol_delivery_audit.py`
- `scripts/etf_vol_target_sweep.py`
- `scripts/futures_tsmom_probe.py`

## Honest limits

- The causal arm is the same rule with its information delayed one bar. It is an upper bound on the defect, not a corrected production number: a causal redesign of the signal may recover part of the difference.
- The ledger arm marks to close around an open fill; the causal arm marks open-to-open. That basis gap is reported separately and is *not* part of the look-ahead number.
- One panel, one window, the survivor pool inherited from the card.
