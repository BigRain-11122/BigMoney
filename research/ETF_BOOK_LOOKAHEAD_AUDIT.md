# The card's headline trades one bar of the future

`2026-11-20T17:02:12+0800` · evidence cutoff **2026-11-20** · 1528 symbols · 5285 bars

## Verdict

**LOOKAHEAD_PRESENT** — the published engine ranks on `score.loc[d]` -- built from bar d's own close and amount -- and then earns open[d]->open[d+1]: the book buys at a price that was set before the information it ranks on. Delaying that information one bar costs 0.97 pp/yr, and the whole ladder is monotone in delay (-2:+15.34, -1:+12.25, +0:+9.16, +1:+8.19, +5:+7.67, +20:+4.86)

## The three arms

| arm | cagr | sharpe | maxdd | vol | bars |
|---|---|---|---|---|---|
| published (card) | 9.16% | 0.946 | -11.77% | 10.19% | 1667 |
| causal (score shifted +1 bar) | 8.19% | 0.849 | -16.56% | 10.28% | 1667 |
| ledger engine, no carry | 8.00% | 0.846 | -13.57% | 10.07% | 1668 |
| ledger engine, ladder3 carry | 8.59% | 0.902 | -13.26% | 10.07% | 1668 |

## The lag ladder — the same rule, moved in time

Negative lag = the score is given bars of the *future*; positive = the book is asked to trade on older information. Nothing else changes (same panel, ranking, cost, overlay).

| lag (bars) | cagr | sharpe | maxdd |
|---|---|---|---|
| -2 | 15.34% | 1.475 | -13.35% |
| -1 | 12.25% | 1.254 | -11.02% |
| +0 | 9.16% | 0.946 | -11.77% |
| +1 | 8.19% | 0.849 | -16.56% |
| +5 | 7.67% | 0.792 | -16.66% |
| +20 | 4.86% | 0.524 | -17.64% |

## Decomposition

- price of the one bar: **0.97 pp/yr**
- mark basis (open-to-open vs close-to-close): 0.19 pp/yr
- repo carry credited by the ledger, absent from the card: 0.59 pp/yr

the three components are priced on separate arms: the first is information ordering, the second is open-to-open vs close-to-close marking around an open fill, the third is the repo ladder the ledger credits and the card does not

Bar level — published vs causal: 1666 overlapping bars, max daily difference 0.0167 at 2025-08-25.

## What is affected

Scripts that price through this ordering (mechanical scan, 99 files):

- `scripts/candidate_year_gate_phases.py`
- `scripts/etf_book_2025_repro.py`
- `scripts/etf_book_admission_eta.py`
- `scripts/etf_book_bakeoff.py`
- `scripts/etf_book_band_ruler.py`
- `scripts/etf_book_bridge.py`
- `scripts/etf_book_buffer_adoption.py`
- `scripts/etf_book_cagr_reconcile.py`
- `scripts/etf_book_calendar_book.py`
- `scripts/etf_book_capacity_shortfall.py`
- `scripts/etf_book_cash_lock_gap.py`
- `scripts/etf_book_causal_rebuild.py`
- `scripts/etf_book_churn_hold.py`
- `scripts/etf_book_concentration.py`
- `scripts/etf_book_concentration_levers.py`
- `scripts/etf_book_corr_select.py`
- `scripts/etf_book_cost_tape.py`
- `scripts/etf_book_derisk_rule.py`
- `scripts/etf_book_do_or_wait.py`
- `scripts/etf_book_entry_gate.py`
- `scripts/etf_book_entry_lag.py`
- `scripts/etf_book_exit_liquidity.py`
- `scripts/etf_book_exit_tax.py`
- `scripts/etf_book_fill_venue.py`
- `scripts/etf_book_floor_memory.py`
- `scripts/etf_book_forced_hold.py`
- `scripts/etf_book_forward.py`
- `scripts/etf_book_gate_causal.py`
- `scripts/etf_book_gate_forward_content.py`
- `scripts/etf_book_gate_knobs.py`
- `scripts/etf_book_gate_raise_noise.py`
- `scripts/etf_book_gate_raise_price.py`
- `scripts/etf_book_hysteresis.py`
- `scripts/etf_book_idle_cash.py`
- `scripts/etf_book_late_sheet_price.py`
- `scripts/etf_book_liquidity_era.py`
- `scripts/etf_book_liquidity_select.py`
- `scripts/etf_book_live_size_provenance.py`
- `scripts/etf_book_lookahead_audit.py`
- `scripts/etf_book_lot_ladder.py`
- `scripts/etf_book_money_mde.py`
- `scripts/etf_book_nav_envelope.py`
- `scripts/etf_book_open_slicing.py`
- `scripts/etf_book_overnight_gap.py`
- `scripts/etf_book_pair.py`
- `scripts/etf_book_passive_mix.py`
- `scripts/etf_book_phase_atlas.py`
- `scripts/etf_book_pre2020_voltarget.py`
- `scripts/etf_book_pre2020_wf.py`
- `scripts/etf_book_production.py`
- `scripts/etf_book_punctuality.py`
- `scripts/etf_book_raise_arm_noise.py`
- `scripts/etf_book_rebal_adoption.py`
- `scripts/etf_book_ruler_forward.py`
- `scripts/etf_book_scale_floor.py`
- `scripts/etf_book_seat_hold.py`
- `scripts/etf_book_seat_mde.py`
- `scripts/etf_book_sleeve_cap.py`
- `scripts/etf_book_sleeve_cap_phases.py`
- `scripts/etf_book_sleeve_gate.py`
- `scripts/etf_book_sleeve_paths.py`
- `scripts/etf_book_spanning.py`
- `scripts/etf_book_spanning_pre2020.py`
- `scripts/etf_book_split_audit.py`
- `scripts/etf_book_stagger_publish.py`
- `scripts/etf_book_survivorship_hole.py`
- `scripts/etf_book_tearsheet.py`
- `scripts/etf_book_tilt_neutral.py`
- `scripts/etf_book_tsmom.py`
- `scripts/etf_book_underwater.py`
- `scripts/etf_book_universe_lock.py`
- `scripts/etf_book_vol_target_gate.py`
- `scripts/etf_book_vol_window_edge.py`
- `scripts/etf_book_vol_window_phase.py`
- `scripts/etf_book_volgate.py`
- `scripts/etf_book_voltarget_lag.py`
- `scripts/etf_book_vt_ladder.py`
- `scripts/etf_book_vt_phases.py`
- `scripts/etf_book_weight_scheme.py`
- `scripts/etf_book_width_cross.py`
- `scripts/etf_book_width_neighbors.py`
- `scripts/etf_book_width_null_production.py`
- `scripts/etf_book_width_positive_control.py`
- `scripts/etf_book_width_return.py`
- `scripts/etf_book_window_decomp.py`
- `scripts/etf_book_window_split.py`
- `scripts/etf_book_wrapper_year_gate.py`
- `scripts/etf_book_year_attribution.py`
- `scripts/etf_book_year_caliber.py`
- `scripts/etf_book_year_gate.py`
- `scripts/etf_book_year_gate_idlecarry.py`
- `scripts/etf_equity_alpha.py`
- `scripts/etf_nobond_vt.py`
- `scripts/etf_robust_pf.py`
- `scripts/etf_vol_calibration.py`
- `scripts/etf_vol_delivery_audit.py`
- `scripts/etf_vol_target_sweep.py`
- `scripts/futures_tsmom_probe.py`
- `scripts/idx_fut_carry_risk.py`

## Honest limits

- The causal arm is the same rule with its information delayed one bar. It is an upper bound on the defect, not a corrected production number: a causal redesign of the signal may recover part of the difference.
- The ledger arm marks to close around an open fill; the causal arm marks open-to-open. That basis gap is reported separately and is *not* part of the look-ahead number.
- One panel, one window, the survivor pool inherited from the card.
