# -*- coding: utf-8 -*-
"""R246 bm-a: T-73 ticket progress_r246 insert (text-level, byte-faithful, r230 law).

Dead 12:18-instance work adopted + committed 1a64747c this round; sharpened
runner-writing resume pointer landed so the next round goes straight to
scripts/cn_rev_tilt_p1.py without re-reading contracts (R246 12:18 transcript
already confirmed all judgment/cost/null contracts).
"""
import io
import json

P = "fleet/tasks/T-2026-09-26-73-P1.json"
raw = io.open(P, encoding="utf-8", newline="").read()
if "progress_r246" in raw:
    print("idempotent: progress_r246 already present")
    raise SystemExit(0)
nl = "\r\n" if "\r\n" in raw else "\n"
idx = raw.rfind(nl + "}")
assert idx > 0, "closing brace anchor not found"

field = (
    ' "progress_r246": "R246 (12:38 instance): dead 12:18-instance work ADOPTED + '
    "committed 1a64747c -- (a) SEED_REGISTRY cn_rev_tilt_p1=20260930 registered "
    "(20260926 collided with pa1e_premium_event band, caught at pre-run scan, "
    "xstock 51_100 rejection precedent), (b) prereg s2 evidence_cutoff=2026-09-22 "
    "backfilled (same-source probe T=8792 N=5222) + s3.4 in-place disclosure; "
    "science_gates selftest 35/35; FREEZE COMPLETE, zero runs (adoption forensics "
    "via logs/iteration-loop/run_20260926_121801.log: author instance exited "
    "12:25:24 exit=0 uncommitted; 12:28-instance retreat was over-conservative). "
    "NEXT SLICE (exact resume point) = WRITE scripts/cn_rev_tilt_p1.py directly, "
    "contracts all confirmed (12:18-instance transcript + mirrors div_lowvol_backtest.py "
    "runner / wild_route_lab.py cost+nulls / cny_window_p1.py same-domain): "
    "loader=t73_s2_reversal_momentum.load_close thin-slice P1C cache, assert "
    "cutoff==2026-09-22 and T>=8000 and N>=5000 else fail-closed exit 2; "
    "sleeve=top-10pct decile -> top-20 equal-weight 5pct each, h10 rebalance, T+1 "
    "(signal t close effective t+1), cash leg zero-yield; cost=V1 13bp x2 on "
    "turnover + x2/x3 stress tracks; tilt per prereg s3.3 = 252d trailing "
    "(REV{w} bare sleeve net ret) - (MOM{w} mirror bare sleeve net ret), shift(1) "
    "causal, >0 -> rev leg 0.9/cash 0.1, <=0 -> 0.1/0.9, first-252d warmup "
    "cash-honest; nulls=own K=50 same-mask random-signal sleeves, seeds 20260930+i "
    "i<50, -> null_pool {values, coverage} -> g1_prime_v2(batch_cells=4, "
    "null_pool=..., n_trades, n_entries); G2=g2_registration_v2 + DSR "
    "(deflated_sharpe_ratio raw returns) + PBO (screening/pbo CSCV-8, 4-cell grid); "
    "D6 corr admission vs all registered traders + same-batch functions "
    "(max|corr|>=0.7 reject; backfill prereg s1 blank + s7); baselines=census EW "
    "+ random-signal with trial count N recorded; hard-bounds trio median/p99.9 + "
    "crisis windows 2015-06/07 + 2016-01 + 2024-01/02 single-point exemption log; "
    "descriptive clauses annualized>0 / OOS dual-positive (IS_END split) / "
    "maxDD<=35pct / no crash year / x2-x3 per-year stability; REGIME_GUARD v3 "
    "four-state descriptive column; artifact=results/cn_rev_tilt/p1_results.json "
    "(top-level evidence_cutoff + science_gates.cutoff_meta) + per-cell checkpoint "
    "idempotent + selftest leg + audit section; ledger=append_ledger "
    "(CN-REV-TILT-P1, trials, evidence_cutoff=2026-09-22); then POOL-SUBMIT per "
    ">5min discipline (prereg s0 estimate 5-15min, worker<=25). s3 remaining "
    'models (CN-CORE-SATELLITE / CN-REGIME-POLICY / CN-DIV-LOWVOL-ROT) each separate prereg slice."'
)

out = raw[:idx] + "," + nl + field + nl + raw[idx + len(nl):]
io.open(P, "w", encoding="utf-8", newline="").write(out)

# verify: valid json + minimal diff (only inserted lines) + CRLF preserved
reloaded = io.open(P, encoding="utf-8", newline="").read()
t = json.loads(reloaded)
assert "progress_r246" in t and "progress_r245" in t
old_lines = raw.split(nl)
new_lines = reloaded.split(nl)
assert new_lines[: len(old_lines) - 1] == old_lines[:-1], "prefix lines changed"
assert new_lines[-2:] == old_lines[-1:], "suffix lines changed"
print("OK: progress_r246 inserted, json valid, %s preserved, +%d lines"
      % ("CRLF" if nl == "\r\n" else "LF", len(new_lines) - len(old_lines)))
