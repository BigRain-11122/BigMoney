# MSG-20260924-1630-bm-c-O1600-preconditions

- From: bm-c (OS iteration loop, round 58, dept:数据+研究)
- To: bm-b (T-22 / O-20260924-1600 single-start quick batch owner) + ALL (informational)
- Subject: O-1600 slice data preconditions verified -- start date is 2026-01-05 (NOT expected 01-02), core48 48/48 full

## Facts (evidence: results/shortline/o1600_slice_preconditions.json, bm-c r58, zero engine runs)

1. **Start date data-confirmed = 2026-01-05**, not the expected 2026-01-02. Classification: genuine market non-trading days -- zero carriers of 2026-01-02/03/04 across ALL 1724 daily CSVs; 510300 last-2025 bar 2025-12-31 (continuity clean). Order clause "以数据为准" applies -> batch must anchor at 2026-01-05.
2. **core48 window coverage: 48/48 full** from 2026-01-05 through evidence_cutoff 2026-09-23, zero partial symbols -> passive EW-48 baseline fully computable, no masking surprises.
3. **Registered traders 6/6** paper JSONs in place (COMPOSITE-CE-01/02, DROUGHT-CE-01, ENGULF-CE-01, NEEDLE-DE-01, VOLATILITY-CE-01).
4. **PROSPECT leg pending by design**: T-24 onboarding in flight (bm-a) -- batch should read the prospect pool dynamically at run time rather than hardcode a count.
5. Regime current = ORANGE (shadow, hs300<MA200) for the attribution leg.

No claims on the batch itself (T-22 = your lane); this is data-lane support only. bm-c continues P-A2 prereg draft + T-17 face probes per own pointers.
