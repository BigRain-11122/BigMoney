# DIGEST r1202 / E168 — pre-2017 tilt split into its two legs, and the leave-one-month-out sweep

Face: `results/e43_tilt_4member/TILT3LEGS-20261027.json` (cutoff 2026-10-27)
Code: `scripts/e39_panel_census.py` — `run_tilt3legs`, `_leg_monthly`, `_lomo_sweep`, mode `tilt3legs`
Method card: E168. Selftest 504 -> 521.

## The question

E126 made 2013-04..2016-12 measurable for the first time and published **+1186.4bp/yr** of tilt
beside a size-neutral leg of only **+134.4bp**. That says most of the era's headline is the size
leg. It does not say what the size leg is made of, and it does not say whether 44 months is 44
months of evidence — the three-member skin's small leg is **one name** (`sh510500`).

## What the face now publishes, per era

Each era carries its two legs' annualised returns on their own, the arithmetic identity
(`tilt == small - large`, residual checked and published), and a leave-one-month-out sweep of the
era mean with two different scalings of dependence.

| era | months | large leg (2 broad-cap) | small leg (510500) | tilt | LOMO span | months to half |
|---|---|---|---|---|---|---|
| pre2017 | 44 | +683.5bp | **+1869.9bp** | +1186.4 | **1353.8** | **2** |
| 2017_2020 | 48 | +1288.2 | +364.3 | -923.9 | 440.5 | 14 |
| 2021_2023 | 36 | -1258.2 | -648.2 | +609.9 | 845.7 | 1 |
| 2024_now | 34 | +792.7 | +1045.5 | +252.8 | 907.7 | 1 |
| full | 162 | +454.1 | +691.2 | +237.1 | 361.6 | 1 |

Identity residual on every era: **0.0bp** (the published tilt *is* the leg difference; no second
fit was introduced).

## Three readings that were not available before

**(a) The pre-2017 headline is 44 months wide and 2 months deep.** Dropping a single month moves
the era mean anywhere in **643.7 .. 1997.5bp** (span 1353.8 on a 1186.4 reading), and the largest
single-month shift is **2014-12** (+811.1bp when removed — that month reads -2807.7bp of tilt,
-64.5% of the whole sum). Two months carry more than half of the era's contribution. So
"+1186bp/yr for pre-2017" is a true statement about a mean whose sign is stable (no single drop
flips it) but whose *level* is not quotable to the nearest hundred bp.

**(b) Both legs were positive in that era; the small leg was 2.7x the large one.** +683.5 vs
+1869.9 is not "small caps carried it against broad caps" — it is one mid-cap ETF compounding at
almost three times the broad pair, and 510500's own worst month (-28.0%) sits inside that average.
The tilt is a *difference of two positive legs*, which is exactly why it cannot be read as a
small-cap bucket return.

**(c) The dependence is era-specific and the newest era is the fragile one, not the oldest.**
`months_to_half` is 1 in 2021_2023, 2024_now and full (a handful of months decide those readings),
14 in 2017_2020 (genuinely spread), and 2 in pre2017. And **2024_now is the only era whose sign
flips under a single dropped month** (-139.4 .. +768.4 around +252.8; 2026-07 alone is -195.0% of
the sum). The era that looked "recent and therefore safest" is the one whose sign is a
one-month artefact; the era flagged as thin (44 months) keeps its sign.

## Controls / honest

- The two legs are equal-weighted inside themselves and are priced only on months where **every**
  member of that leg is present and clean — a partial roster would silently re-weight the leg
  (selftest legs pin this).
- LOMO is not a confidence interval; no p-value is claimed. `months_to_half` counts contribution
  in the sign of the mean, so it names concentration, not robustness.
- The small leg is one name: the number is that ETF's own return, labelled as such in the face.
- Eras remain calendar partitions of one monthly series and do not add to the full row.
- Descriptive census: no gate, no verdict, no prereg, no trial count.