# E77 — screened wide-book re-derivation (r1148 bm-b)

Evidence cutoff 2026-10-21. Face: `results/e44_midmonth/SCREENWIDE-20261021.json`.
Runner: `python scripts/e39_panel_census.py screenwide` (32 backtest runs, 57 s, CPU-only).
Loader: `scripts/panel_screen.py` via `e27.run(raw=...)` — opt-in, no published face rewritten.

## Question

E76 re-derived the *era spread* on the repaired universe and the newest era moved
103bp → 303bp (integer-only screen) → 479bp (all adjacent prints). E77 asks whether
the wide-book headline columns themselves move, and whether the correction
survives the cost multiplier and both start windows.

## Answer — the wide book, not just the spread

| face | column | unscreened | neutralise (int) | neutralise (all) | drop |
|---|---|---|---|---|---|
| wide@2020 x1 | wide_ann_pct | 0.85 | 1.82 | 2.90 | 1.10 |
| wide@2020 x3 | wide_ann_pct | 0.70 | 1.66 | 2.74 | 0.95 |
| wide@2018 x1 | wide_ann_pct | 7.44 | 8.23 | 9.24 | 7.71 |
| wide@2018 x3 | wide_ann_pct | 7.28 | 8.07 | 9.07 | 7.55 |

The 2020-start wide book more than *doubles* (0.85 → 1.82 / 2.90 %/yr) once the
adjacent-impossibility prints are neutralised — the cheapest headline the chain
quotes is the one most contaminated, because it sits in the era where the 2024
splits print.

Era columns (spread vs ladder5, bp/yr):

| era | unscreened | neutralise (int) | neutralise (all) | drop |
|---|---|---|---|---|
| pre2017 | 236 | 236 | 236 | 219 |
| 2017_2020 | 419 | 419 | 446 | 443 |
| 2021_2023 | 243 | 289 | 379 | 314 |
| 2024_now | 103 | 303 | 479 | 78 |

`pre2017` is untouched by the screen (its splits gap behind suspension bars and
are never repaired — see E75), so the correction is **not** a uniform rescale:
it is concentrated where unadjusted prints actually sit.

Worst single correction: `era:2024_now@x1 spread_ann_bp` +376bp (all-adjacent),
+200bp integer-only. Worst wide column: `wide@2020 x1 vs_ladder_bp_annualised`
139.3 → 373.2 (+233.9).

## Does it survive costs and both windows?

Yes, and costs are irrelevant to the correction. The x1→x3 shift is −0.15…−0.17pp
in *every* mode (unscreened, both neutralise columns, drop) at both starts: the
screen moves the return path, not the traded turnover (turnover delta ≤0.003/yr,
cost_per_year delta ≤0.2bp).

Zero eras change the sign of their spread under any mode — the ladder-over-wide
ordering is robust; only the *magnitude* in 2021_2023 and 2024_now is an artefact.

66 of 80 delta cells are non-zero; the ladder column moves 0.0 (its five members'
corporate actions are gapped, consistent with E75/E76).

## Honest limits

- The screen repairs arithmetic impossibility only. A flagged ETF print may be
  genuine; `neutralise` is a sensitivity face, not truth. Integer-only is stricter.
- `drop` mixes the correction with a composition change (−disc 16 names), which is
  why `drop` reads *lower* in 2024_now (78bp) while both neutralise columns read
  higher: dropping the split names removes the distorting prints but also removes
  the names, and the surviving book is no longer the same book.
- Anything quoting the wide-book 2020-start or the 2024_now spread from
  `e27.load_universe()` unscreened is quoting a contaminated number by 0.8–3.8pp/yr.

## Pointer

Next: no new pool entry raised from this leg — the chain's published faces are the
consumer, and E76's opt-in loader is now measured at both headline levels. Reopening
condition: a screened ladder face (expected flat, would contradict E75's gapped-print
reading).