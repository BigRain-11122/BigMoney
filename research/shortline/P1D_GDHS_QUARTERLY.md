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

## §6 Results (backfilled after run — one-shot, deterministic double-run verified)

Run: 9.3s, one-shot. Determinism: re-run diff (excl. elapsed_s) = identical.

Panel/events: 44 canonical quarter events (2015Q3..2026Q2), 0 irregular
placements dropped; 41 usable-with-forward rows → **35 IS ICs + 6 OOS ICs**
(2 early IS events dropped by ic_from_ranks ≥5-names/zero-variance filter +
last event no-forward + 1 more; disclosed vs prereg expectation 37/6).
Universe median 2,446 stocks/event (max 3,319).

Nulls (K=50, seed 48_000): p95 |mean IC| = 0.0061 / 0.0063 / 0.0078
(chg_q/chg_2q/level) → **V1 floor 0.02 dominated** as predicted. Null p95
|IR| = **0.3252 / 0.3010 / 0.4121** → the frozen effective-V2-line
correction (max(0.30, null p95 IR)) was decisive — see level below.

| factor | IS IC | IS IR | IS n | OOS IC | OOS n | eff. V2 line | verdict |
|---|---|---|---|---|---|---|---|
| gdhs_chg_q  | −0.0263 | −0.544 | 35 | −0.0337 | 6 | 0.3252 | **PASS** |
| gdhs_chg_2q | −0.0421 | **−0.675** | 35 | −0.0557 | 6 | 0.3010 | **PASS** |
| gdhs_level  | −0.0493 | −0.302 | 35 | −0.0169 | 6 | 0.4121 | FAIL |

**2/3 PASS** — both shareholder-CHANGE factors pass all three gates with
wide margins; OOS (2025+, n=6 thin) **retained AND deepened** (chg_q
−0.0337 vs IS −0.0263; chg_2q −0.0557 vs −0.0421). Per prereg §4: **zero
registration** — recorded as candidate material for a future preregistered
strategy conversion (quarterly rebalance, shareholder-count tilt).

Mechanism readings:
- 股东户数变化负向预测下季收益（户数减少=筹码集中=后续涨）在 A 股股票池
  季度口径成立；chg_2q (两季累计) 强于 chg_q = 持续筹码集中比单季骤变更有
  信息量（反向于「平滑衰减」直觉）。
- gdhs_level: biggest mean IC (−0.0493) but IC std 0.1632 (3.4× chg_2q's)
  → IR collapses. Level is a slow structural variable (散户密度) whose
  quarterly IC is regime-volatile; killed by the null-corrected line
  (0.302 < 0.4121) — **the raw 0.30 line would have let it pass by 0.002**
  = the SS3 power correction flipped a real verdict (first decisive use).
- Verdict robustness under seed-collision disclosure: all three margins
  (0.544−0.325=0.219 / 0.675−0.301=0.374 / 0.412−0.302=0.110) exceed
  any plausible null-band wobble (±15% → max line 0.374/0.346/0.352);
  chg_q & chg_2q still PASS, level still FAIL under the whole band.

### Seed collision disclosure (honest, post-run)

Prereg registered seed 48_000 **without checking** that p4_pairs (bm-a R42,
committed ~05:43, after my prereg draft started) had already taken 48_000.
Kept as-run: prereg frozen before results; machinery fully disjoint
(pair-index draws vs value permutations); robustness argument above.
Future preregs must grep SEED_REGISTRY for the base BEFORE freezing (§5 of
this doc did not include that check — added to the reconciliation below).

### Prediction reconciliation (SS7)

1. chg_q negative ✓ (70% → confirmed, IS −0.0263 / OOS −0.0337)
2. level negative sign ✓ but gate FAIL (55% → direction right, IR killed)
3. chg_2q negative ✓ but "weaker than chg_q" ✗ — actual STRONGER (|IR|
   0.675 vs 0.544, |IC| 0.0421 vs 0.0263): double-quarter accumulation
   amplifies, does not damp. Half-right.
4. Survivors "0–1 of 3" ✗ — actual 2/3 PASS (pessimistic miscalibration;
   r60 had the opposite miss on the same family — overestimated it in the
   daily framing, underestimated at the correct quarterly frequency. Both
   misses share one root: no prior anchor for quarterly-frequency power).
5. Null p95 |meanIC| ≈ 0.003–0.007 → actual 0.0061/0.0063/0.0078:
   level slightly above band (half-right); V1 floor dominance ✓.
6. OOS noisy/thin ✓ disclosed (n=6), but retention >1 (deepening) beat
   the "noisy retention" expectation.
7. (NEW, process): seed-base registry check missing from prereg checklist
   → now standard: `rg -n '"<base>"' scripts/science_gates.py` before
   freezing any prereg seed.


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
