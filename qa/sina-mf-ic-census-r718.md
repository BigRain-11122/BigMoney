# QA · sina-mf-ic-census-r718 (bm-a, 2026-10-05)

Artifact: scripts/sina_mf_ic_census_p1.py + results/sina_mf_ic_census_p1.json
Lane: research (trial-labor supply line, cheap-screen-first; bandit next_pick
event-attention lane; SINA_MF_PREREG frozen data lane consumed as INDEPENDENT
causal sub-face per its sec.2 isolation law -- EM face still source-blocked
53/5222, no EM mapping / no quantity fabrication per frozen spec).

## Checklist (all PASS)

1. 意义门三问 in script header: research question (sina four-tier flow factors
   carry stock-level forward IC?), consumer (trial-labor supply -> prereg only
   if enriched -> judged burn -> TRIAL paper), dedup (zero prior sina_mf factor
   consumption in repo -- S6 collectors only; EM moneyflow IC never burned;
   theme-judge/LHB/P-1e = different faces; smart_retail declared in-batch
   composite). PASS
2. Frozen grid declared in header BEFORE first real run; no threshold edits
   after results. One selftest-leg fix (L6 binomial-tail assertion math:
   P(X>=5|n=10)=638/1024=0.623, NOT 0.5) -- test-fixture fix, gate/judgment
   lines untouched. PASS
3. selftest 6/6 PASS (alpha detection, noise non-detection, share-construction
   scale-invariance + buy_total=0 guard, window reindex mapping, determinism,
   sign-test sanity). PASS
4. Real run rc0: panel pass 5228/5228 files read, 1,294,199 rows, 0 read
   errors; panel self-check (R215 verifier aggregate) 1,294,199/1,294,199
   rows within 1e-3 (netamount == sum(r*_net)); window 2025-09-15..2026-09-22
   (248 rows); IC legs elapsed 7.6s; single process, zero network, Money02
   read-only (memmap). PASS
5. evidence_cutoff = 2026-09-22 (p1c cache last date); sina tail rows
   2026-09-23/24 unconsumable (no forward returns) -- disclosed in JSON
   honesty block. PASS
6. Honest verdict per frozen AND-gate (primary h10 cells: p<=0.05 AND |t|>=2.0
   in DECLARED predicted direction):
   - **CENSUS_ENRICHED: small_share-d5** (ic_mean -0.0184, t=-3.02,
     one-sided p=0.00043 in predicted "-" direction, n=236 dates,
     ic_pos_pct 0.39) -- retail-small sustained absorption -> 10td
     underperformance, folk direction confirmed;
   - robustness context (reported, non-gating): small_share-d5 strengthens
     monotonically with horizon (h5 t=-1.87 / h10 t=-3.02 / h20 t=-5.05,
     p=7e-05);
   - opposite-direction exploratory facts (NOT claimed, recorded for future
     fresh preregs only): d5-smoothed inflow faces all show significant
     NEGATIVE IC (super_share-d5 t=-4.59, mid_share-d5 t=-4.84,
     net_ratio-d5 t=-3.27, smart_retail-d5 t=-2.74) = sustained-inflow
     crowding->reversal structure, opposite to their declared "+" direction;
     gate NOT weakened post-hoc to claim these. PASS
7. Universe alignment: 5222/5222 p1c syms have sina panels; 6 sina-only
   newer IPOs structurally excluded (count in JSON meta). PASS
8. Zero ledger rows / zero marks / zero engine / descriptive-census discipline
   (no verdict claims, no multiple-testing-line statements). PASS

## Disposition

CENSUS_ENRICHED (small_share-d5) -> next round first act: full prereg draft
from research/PREREG_TEMPLATE.md (batch family = sina-mf retail-absorption;
alpha mechanism = behavioral bias face; D6 sleeve corr vs in-book members +
in-queue functions; explicit exit-axis three-way choice; SEED_REGISTRY band
registration; evidence_cutoff 2026-09-22 + cutoff_meta; banned-direction
gate + F-04 seat MSG before any burn). Opposite-direction inflow-reversal
faces: any future prereg on them must be a fresh pre-registration citing this
census as exploration evidence only (r717 law).
