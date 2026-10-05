# QA · style-rot-census-r717 (bm-a, 2026-10-05)

Artifact: scripts/style_rot_census_p1.py + results/style_rot_census_p1.json
Lane: research (trial-labor supply line, cheap-screen-first; T-73 s2 lineage;
r690/r693 planned "style-rotation drafting" pointer — bm-b astock panel landed,
stock-level face belongs to p1c_stock frozen cache on bm-a host).

## Checklist (all PASS)

1. 意义门三问 in script header: research question (stock-level dual-horizon
   style-rotation), consumer (trial-labor supply → prereg only if enriched),
   dedup (t73_s2 = ETF-panel descriptive closed r259; T-139 trio = single-style
   cross-sections; no stock-level rotation-timing face prior). PASS
2. Frozen grid declared in header BEFORE first run; no threshold edits after
   results (LOWAMP law honored). PASS
3. selftest 5/5 PASS (synthetic alpha direction, NaN-name exclusion,
   sign-test sanity, reversal path, determinism). PASS
4. Real run rc0, 9.6s elapsed, single process, zero network, ~550MB RAM
   (CEO CPU 10%-headroom law: trivially compliant). PASS
5. evidence_cutoff = 2026-09-22 (p1c cache last date, µs-epoch convention)
   disclosed in output JSON. PASS
6. Honest verdict: NO_CENSUS_ENRICHMENT per frozen AND-gate
   (primary p<=0.05 AND |t|>=2.0):
   - TREND faces (step 63): hit 0.35/0.40, sign-p 0.9998/0.9878 — annual-trend
     continuation from ETF face DOES NOT replicate at stock level (strong
     anti-persistence direction);
   - REVERSAL faces (step 63): flip sign-p 0.00984 (SIZE) / 0.00031 (TURN) —
     direction supported, but |t|=1.36/1.62 < 2.0 → below frozen effect-size
     line → NOT enriched; gate NOT weakened post-hoc. PASS
7. Zero ledger rows / zero marks / zero engine / Money02 read-only
   (memmap cache consumption, no writes). PASS
8. Descriptive census discipline: no verdict claims, no paper claims, no
   multiple-testing-line statements (theme_ignition_census v0.3 law). PASS

## Disposition

NO_CENSUS_ENRICHMENT → honest park: no prereg, no burn (CEO meaning-order:
no wasted burn). Recorded exploration facts for future rounds: stock-level
style spreads mean-revert at both horizons (anti-trend hit 0.32-0.40);
reversal-face sign tests sub-gate. Any future style-reversal prereg must be
a fresh pre-registration citing this census as exploration evidence only.
