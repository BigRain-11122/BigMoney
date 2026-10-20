# DIGEST 2026-10-20 · E21 leg-3 — who pays the overnight toll (conditioned decomposition)

**Artifact** `results/overnight_gap_census/LEG3-2026-10-19.json` (+ `leg3_by_liquidity.csv`,
`leg3_by_volatility.csv`, `leg3_by_gap.csv`, `leg3_liq_x_gap.csv`), generated 2026-10-20 16:32
by `scripts/overnight_gap_conditioned.py` (selftest 16/16). Evidence cutoff 2026-10-19.
Zero prereg, zero judged face, zero pool write, zero cost model — descriptive face only.

## Question

Leg-1 established the unconditional split: overnight −0.0891%/bar vs intraday +0.1409%/bar
(A-share returns are earned intraday; overnight is structural bleed), and leg-2 showed the
bleed is linear in hold length. Leg-3 asks **who pays it**: does the toll concentrate in a
particular liquidity / volatility / gap regime, or is it uniform?

## Method (frozen in the script header)

Panel = T-87 qfq forward panel `data/astock_daily/per/<code>.csv`; same exclusion lineage as
leg-1 (bad px / suspension-resume transition / one-price bar / |r|≥75% artifact drop the
observation, not the file). Conditioning features are read at the decision bar i and returns
are measured at i+1 (strict causality):

- `liq_pct` — today's `amount` percentile inside the stock's own trailing 250 bars
- `vol_pct` — today's 20-bar return std percentile inside the same 250-bar window
- `gap` — today's open/prev-close − 1, bucketed by fixed cross-sectional edges
  (−2%, −0.5%, +0.5%, +2%)

Self-relative percentiles are used deliberately: the panel is 16.7M bars, per-date
cross-sections are not materialised, and the applied question ("unusually liquid / noisy
*for itself* right now") is the same one an entry rule asks.

## Coverage

5,199 stock files, 16,714,559 bars, **15,110,598 observations**. Dropped and counted:
suspension-resume 160,515; one-price 87,070; warm-up (<250-bar history) 1,343,943; artifact
|r|≥75% 29; bad px 6; short files 26. Weighted mean over any face = overnight −0.0833%/bar,
intraday +0.1393%/bar (leg-1 all-bars reference −0.0891% / +0.1409% — the small gap is the
warm-up window, not a contradiction).

## Findings

**1. The toll is not uniform — it scales with the name's own liquidity state.**

| self-relative liquidity | overnight mean | intraday mean | net | n |
|---|---|---|---|---|
| q1 (quietest) | −0.0193% | +0.0402% | +0.0187% | 3,397,940 |
| q2 | −0.0402% | +0.0948% | +0.0526% | 2,644,894 |
| q3 | −0.0578% | +0.1346% | +0.0746% | 2,626,699 |
| q4 | −0.0827% | +0.1761% | +0.0903% | 2,816,849 |
| q5 (loudest) | **−0.1936%** | +0.2396% | +0.0400% | 3,624,216 |

q5/q1 overnight ratio = **10.0×** (t = −211 vs −37). The intraday leg also grows with
liquidity, but not enough to restore the net: net return peaks at q4 and *falls* at q5.

**2. Volatility is the same axis in another coat.** overnight by `vol_pct` quintile:
−0.0253% / −0.0442% / −0.0670% / −0.0920% / **−0.1845%** (q5/q1 ≈ 7.3×). Liquidity and
volatility are correlated here; the liq × gap cross-tab below keeps the reading honest —
no claim that they are separate mechanisms is made in this face.

**3. Deep gap-down days carry the worst next-day overnight leg.**

| today's gap | overnight next day | intraday next day | net |
|---|---|---|---|
| < −2% | **−0.4465%** | +0.3783% | −0.0827% |
| −2% … −0.5% | −0.1373% | +0.2055% | +0.0651% |
| −0.5% … +0.5% | −0.0509% | +0.0886% | +0.0359% |
| +0.5% … +2% | −0.0424% | +0.1377% | +0.0923% |
| > +2% | −0.0490% | +0.3266% | +0.2600% |

Panic gaps (below −2%) are the only gap bucket whose next-day *net* is negative, and the
overnight share of it is large (−45bp vs +38bp intraday).

**4. The two axes multiply.** Worst cell of the liq × gap cross-tab: **q5 × gap < −2% =
−0.6674% overnight** (n = 278,212); best cell: q1 × gap > +2% = **+0.0600%** overnight
(n = 33,515). Full cross-tab in `leg3_liq_x_gap.csv` (25 cells, every cell n > 33k).

## What this changes for named consumers

- **E14 (limit-up premium) / E18-leg-2 (dividend harvest) / E20 (suspension resumption)**
  open-entry legs: these events *are* liquidity episodes and they frequently follow gaps.
  Their overnight legs must now be read against the conditioned base rate (q5 / gap<−2
  rows), not the panel mean — the panel mean understates the toll such entries pay by up
  to an order of magnitude. This is a base-rate correction, not an edge claim.
- **P4 DCA / grid paper marking timing**: marking at the close vs the next open costs a
  name-state-dependent amount; for a loud name it is ~20bp/bar, for a quiet one ~2bp/bar.
- **Any future "capture the overnight leg" prereg**: this face is the required control.
  A claim that survives only in the q5 bucket is a liquidity-episode proxy claim, and D6
  adjacency must be checked against the volume-episode families already burned (W16
  turnover_surge, W20 turnover_regime) before drafting.

## Honest limits

- Descriptive only: no transaction costs, no executability claim, no judged verdict.
- Self-relative percentiles mean "loud for this name", not "loud in the cross-section";
  the top quintile of a low-turnover name is not the same absolute liquidity as a megacap.
- Warm-up drops the first 250 bars of every stock (1.34M observations), so the panel is
  slightly younger than leg-1; weighted totals differ by ~6bp of the overnight mean.
- Board interaction is emitted (`by_liq_board` in the JSON) but not digested here — one
  question per leg.