# QA · sina-mf-ic-p1-r719 (bm-a, 2026-10-05)

Artifact: scripts/sina_mf_ic_p1.py + results/shortline/sina_mf_ic_p1.json +
research/shortline/sina_mf_ic_p1_results.csv + research/shortline/SINA_MF_IC_P1.md
(§7/§8 backfilled) + results/_r719bma_sina_mf_null_p95_addendum.json
Lane: research (trial-labor supply line survivor confirmation; watermark
next_pick "moneyflow IC reference batch" claimed r717; T-2026-10-05-171).

## Checklist (all PASS)

1. Meaning-gate three questions in prereg §0/§1: research question (does the
   census-enriched retail-absorption face survive reference caliber: T+1
   tradable lag + same-mask nulls + positional IS/OOS?), consumer (factor
   library material pool -> strategy consumption = fresh prereg; honest park
   if failed), dedup (r718 census = the only prior sina_mf consumption, this
   batch = its direct survivor confirmation; EM moneyflow IC never burned;
   mirror law: main-side group share excluded, one side only). PASS
2. Freeze discipline (R99/R250): pre-freeze probe (coverage facts only, zero
   IC faces) results/_r719bma_sina_mf_ic_p1_probe.json; claim-lock commit
   (ticket) precedes freeze commit (prereg + SEED_REGISTRY sina_mf_ic_p1=58_700
   band 58_700..58_999 rg-scanned free + probe files); runner touched the real
   panel only AFTER the freeze commit. banned_direction_gate ADMIT rc0
   (matched=[]; two pattern-collision phrases in honest disclosures were
   reworded pre-freeze, semantics unchanged, no exception claimed). PASS
3. selftest 9/9 PASS (hermetic tmp sandbox, zero real-data): factor law
   (small_share==r3_net/buy exact-row, retail==(r2+r3)/buy), shift1 lag,
   min_periods semantics (d5->3 / d20->12 first-valid positions), width gate
   + positional split, V-gate arithmetic on designed blocks (V3 flip /
   period-gate fail cases), M1 designed-block pass + missing_input refusal,
   run-gate honest exit 2 with zero output files, full pipeline 10 rows with
   weak-check D6 + cutoff_meta key, null determinism (same seeds -> identical
   threshold). Two Windows fixtures fixed during selftest bring-up: np.load
   mmap handle must be detached before TemporaryDirectory rmtree (WinError
   32), and **pd.Timestamp(numeric) reads ns-since-epoch NOT seconds — the
   census-verbatim datetime.fromtimestamp(us/1e6) is the correct loader**
   (toy-debug caught it before any real-panel run; zero burn-window waste).
   PASS
4. Real run rc0 (104s single process, zero network, Money02 read-only
   memmap): panel 5,228 files / 1,294,199 rows / 0 read errors; selfcheck
   1,294,199/1,294,199 rows within 1e-3; 6 sina-only newer IPOs excluded;
   10,444 tail rows after price cutoff unconsumable (disclosed); window
   2025-09-15..2026-09-22 (248 days); gate PASS (files 5,228>=5,000;
   eligible_h10 238>=150). PASS
5. evidence_cutoff=2026-09-22 via science_gates.cutoff_meta top-level key;
   ledger append_ledger(batch_trials=10) prev 653,411 -> total 653,421
   (dict schema, live chain head, zero hand-copy); engine trials ledger N
   untouched. PASS
6. Verdict per frozen lines (V1=max(0.02,null p95|IC|) floor-dominated both
   horizons; V2 |IR|>=0.30; V3 OOS same-sign & >=0.5x IS; period IS>=100/
   OOS>=30): **7/10 PASS** — small_share_d5@h20, d10@h10, d10@h20, d20@h10,
   d20@h20, retail_group_d5@h10, retail_group_d5@h20; FAILs = d1 both (V1+V2)
   + d5@h10 (V1 marginal 0.0186<0.02). Direction (negative IC = retail
   absorption -> underperformance) survives T+1 across all 10 cells; all 7
   passing cells RETAIN and STRENGTHEN in OOS (2-3x IS magnitudes in the
   2026-05-18..09-22 segment — regime-strength note recorded). PASS
7. Null + M1 + D6 faces: raw null p95|IC| 0.0021/0.0022 (h10/h20, addendum
   file, deterministic same-seed recompute — burn JSON single-shot face
   untouched); p95|IR| 0.1481/0.164; M1 HLZ |t|>=3.0 claimable layer 8/10
   (max t=7.17 at d20@h20) with prereg §4/§7.2 overlap-inflation caveat;
   D6 lhb_count_20 strong check ok (max|corr| 0.2287-0.2733 over 232-237
   days), ths pairs weak_check declared (0 overlap days, probe fact), EM
   cross-source out-of-scope declared. M3 family sina_mf_tier_ic = open.
   PASS
8. Known-limitation disclosure (prereg §7.2, P-1a §7.4 kin): white-noise
   nulls are loose for PERSISTENT factors (d5-d20 smoothing = daily
   persistence -> real noise band higher than fresh-noise line; the 0.02
   family floor partially absorbs this, M1 naive-t does not) + ~250td short
   window + size-proximity untested. Three discount labels carried into the
   factor-library material pool; strategy consumption requires fresh prereg
   (explicit exit-axis + CN-C7 stock costs + persistent-null calibration).
   PASS
9. Attrition ledger: SINA_MF_IC_P1 row appended (entries 99->100,
   cells_ledger_delta=10, losses itemized); attrition_ledger_guard scan
   CLEAN rc0 (4 ledgers). PASS

## Disposition

7/10 cells -> factor-library material pool (T+1 caliber, short-window,
size-untested labels). NEXT: (a) strategy-grade consumption prereg = fresh
transaction when a consumer lane opens (P-2-style composite or single-face
long-short; exit axis three-way + CN-C7 costs + persistent-factor null
calibration); (b) EM cross-source correlation batch when the EM panel
self-heals; (c) opposite-direction inflow-reversal faces stay exploration-only
(r718 census law). Ticket T-2026-10-05-171 -> done.
