# P-1d GDHS Quarterly-Frequency Dedicated IC Batch — Preregistration

- Batch ID: `p1d_gdhs_quarterly`
- Lane: P-1d extension-slot factor line (bm-b), sanctioned follow-up of
  P1D_EXT_SLOTS_IC.md r60 verdict: gdhs family was *structurally
  unevaluable* in the daily pipeline (37 IS cross-sections << MIN_PERIODS=500),
  "专用口径另开预注册才可评" — this prereg is that dedicated口径.
- Frequency: **quarterly event IC** (not daily). Zero engine runs (factor
  evidence only; engine ledger N=2858 untouched).
- Evidence cutoff: 2026-09-22 (panel truncation, same as all P-1d/P-1c).

## §1 Scope & universe

- Factors (same 3 as P-1d, construction reused verbatim from
  `p1d_ext_slots_ic.build_gdhs`):
  1. `gdhs_chg_q` = 股东户数-增减比例 / 100 (single-quarter change)
  2. `gdhs_chg_2q` = count / count[t-2] − 1 (stock's own 2-records-back)
  3. `gdhs_level` = log(股东户数 / 总股本)
- Universe per event: stocks with a **fresh record placed at that event's
  availability bar** (placement pos == event pos, pre-ffill semantics),
  inside the p1c panel × b_layer `ok_static` (P-1d SS1 universe, N=3517).
- Availability rule (frozen from P-1d): record 统计截止日 +45 natural days →
  first calendar bar strictly after (GDHS_LAG_DAYS=45).
- Events = the 44 canonical quarter snapshots; usable event = one whose
  *next canonical event* exists inside the data window (the 2026Q2 event
  has no forward → excluded). Records with irregular placement (own qe not
  mapping onto the canonical event pos) are excluded from the universe and
  counted in audit (expected ~0; disclose actual).

## §2 Method

- Forward return: `close[pos_next_event] / close[pos_event] − 1`
  (event-to-event ≈ 1 quarter, ~90 natural days). Requires finite close at
  both bars.
- Per-event IC: cross-sectional Spearman rank IC (factor vs forward return)
  within the event universe.
- Splits: **IS = events with event date < 2025-01-01** (expect ~37);
  **OOS = events ≥ 2025-01-01** (expect ~6 — thin, disclose).
- Report per factor: IS mean IC, IS IR (= mean/std of per-event ICs, n_is),
  OOS mean IC, retention = OOS_mean/IS_mean (sign-adjusted), n_universe
  median, n_events (is/oos).

## §3 Nulls (K=50, seed 48_000 — registered in SEED_REGISTRY)

- Per factor: 50 seeded permutation nulls — per event, permute the factor
  vector within the event universe (numpy Generator, seed 48_000, sequential
  draws), same IC machinery. Null run = mean IC over the same events.
- Null band: p95 of |null mean IC| across 50 runs; null p95 |IR| reported.
- IR null honest expectation: under H0, IR ≈ N(0, 1/√n_is) → p95 ≈ 0.33
  at n_is=37 — **the V2 0.30 line sits *below* the quarterly null p95**;
  survivors must clear both the null p95 IR and 0.30, i.e. effective
  quarterly V2 line = max(0.30, null_p95_IR). Frozen here before run.

## §4 Gates (frozen)

- V1: |IS mean IC| > max(0.02, null p95 |mean IC|)
- V2: |IS IR| ≥ max(0.30, null p95 |IR|)   ← quarterly-power correction above
- V3: OOS same sign AND retention ≥ 0.5 AND n_oos ≥ 5
- Pass = V1 & V2 & V3. **No registration regardless of outcome** — factor-
  level evidence only; strategy conversion needs a separate prereg (this
  batch creates no trader).
- Power disclosure (frozen): n_is≈37 → IR 0.30 ≈ t≈1.8 two-sided p≈0.08;
  quarterly verdicts are horizon-unique (one draw per quarter, info does not
  overlap the daily family). All verdicts carry this thin-power caveat.

## §5 Predictions (before run — SS7 discipline)

1. `gdhs_chg_q` IS direction: **negative** (户数减少=筹码集中=后续涨;
   A-share folklore + classic concentration literature). Confidence 70%.
2. `gdhs_level` direction: negative (高散户密度→弱). Confidence 55%.
3. `gdhs_chg_2q`: negative, weaker |IC| than chg_q (double-quarter smoothing
   damps the signal). Confidence 60%.
4. Survivors through V1&V2&V3: **0–1 of 3** (quarterly power marginal).
5. Null p95 |mean IC| ≈ 0.003–0.007 (per-event IC se ≈ 1/√n_univ≈0.017,
   ÷√37) → V1 floor 0.02 dominates.
6. OOS (n≈6): even a survivor stays observation-grade; retention check
   expected noisy.

## §6 Results (PLACEHOLDER — fill only after run; numbers here before run = fraud)

## §7 Ledger

- Factor ledger: prev=5241 (chain head `results/shortline/xlib_synth.json`),
  batch_trials = 3 primary + 3×50 nulls = **153**, total = **5394**.
- Engine ledger: untouched (2858). IC counting audit block in JSON.
- Top-level `evidence_cutoff` = 2026-09-22 (science_gates.cutoff_meta key).

## §8 Constraints

- Zero network. No engine runs. No registration. No threshold edits after
  run (禁止跑到达标为止). ggplot-free. If PASS → material recorded as
  candidate for a *future* preregistered strategy conversion; if FAIL →
  gdhs line closes for good (second dedicated口径 verdict).
