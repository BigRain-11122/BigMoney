# DIGEST — overnight-gap leg-2 (held-position bridge), evidence_cutoff 2026-10-19

**One line:** the leg-1 overnight bleed does **not** wash out inside a hold — it
accrues at a constant ~-0.089 %/day for 5- and 20-day holds while the intraday
leg earns a constant ~+0.134 %/day. Holding longer does not fix an overnight
entry; it just multiplies the same split.

Source: `scripts/overnight_gap_hold_bridge.py` (selftest 9/9) →
`results/overnight_gap_census/HOLDBRIDGE-2026-10-19.json`
(+ `holdbridge_by_horizon.csv`, `holdbridge_latest.json`).
Panel: `data/astock_daily/per` (5,225 stocks, cutoff 2026-10-19).
Windows are **non-overlapping** (stride = H), enter close(i) / exit close(i+H).

| H | windows | Σovernight | Σintraday | hold (compounded) | on/day | in/day | win(hold) |
|---|--------:|-----------:|----------:|------------------:|-------:|-------:|----------:|
| 5 | 3,270,922 | −0.4490 % | +0.6763 % | +0.2372 % | **−0.0898 %** | **+0.1353 %** | 48.82 % |
| 20 | 782,015 | −1.7709 % | +2.6615 % | +0.8790 % | **−0.0885 %** | **+0.1331 %** | 48.79 % |

leg-1 one-day reference (r1074): overnight −0.0891 %/bar, intraday +0.1409 %/bar.

## What this settles

1. **Horizon invariance.** Per-day overnight rate moves −0.0891 → −0.0898 → −0.0885
   across H = 1/5/20. The bleed is linear in time, not a one-day microstructure
   artifact and not something that decays as the position ages.
2. **The intraday edge is equally stable** (+0.1409 / +0.1353 / +0.1331 %/day).
   The hold-level decay of the per-day rate is ~5 % from H=1 to H=20 — consistent
   with the single-day figure being measured on a wider (limit-board-inclusive)
   sample, not with a different mechanism.
3. **Consequence for judged cells:** any 5d/20d exit family (E14, E18-leg-2, E20
   appear here) must be read against the horizon-matched base rate, not against a
   1-day number multiplied by H. The compounded hold mean is **not** the linear
   sum of the two legs: at H=20 the cross-product term is worth ≈ +0.03 pp of the
   +0.88 % mean and is disclosed in the face, never folded in.

## Honest limits (frozen in the face's disclosures)

- qfq panel: ex-day cash adjustments land inside the overnight leg; sidecars are
  cash-only (r1067) so raw close cannot be reconstructed — not corrected.
- Windows containing a suspension transition, a one-price bar, a bad price or a
  |r| ≥ 75 % artifact are dropped whole, so the surviving set under-represents
  limit-board days (the same exclusion lineage as leg-1).
- No cost model, no position sizing, no long-short leg: this is a description,
  not a tradability claim. Zero prereg, zero judged face, zero pool write.

## Consumers

- E14 / E18-leg-2 / E20 open-entry legs → horizon-matched base rate.
- P4 DCA & grid marking timing → close-mark vs next-open-mark spread at hold length.
- Any future "hold N days to harvest the divergence" prereg → this bridge must be
  cited (it exists now, so absence is no longer an excuse).