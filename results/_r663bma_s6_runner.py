# r663 bm-a S6 chain driver: run registered maintenance chain in order,
# capture per-leg rc + last line, write log to results/_r663bma_s6_log.txt
import subprocess, sys, time

LEGS = [
    ("pool_dualrun", ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts\\compute_audit.py"]),
    ("py_watermark", ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("market_regime", ["python", "scripts\\market_regime.py"]),
    ("strategy_scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("market_clock_call", ["python", "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts\\update_lhb.py"]),
    ("update_heat", ["python", "scripts\\update_heat.py"]),
    ("update_futures", ["python", "scripts\\update_futures.py"]),
    ("update_repo", ["python", "scripts\\update_repo.py"]),
    ("update_options", ["python", "scripts\\update_options.py"]),
    ("update_moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts\\update_etf_daily.py"]),
    ("rev_osc_signal_export", ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["python", "scripts\\update_minute_feed.py"]),
    ("update_ths_panel", ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", ["python", "scripts\\ah_panel_puller.py"]),
    ("update_fund_premium", ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["python", "scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["python", "scripts\\update_fund_statements.py"]),
    ("t35_open_fill_verify", ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", ["python", "scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", ["python", "scripts\\daily_scorecard.py"]),
    ("daily_report", ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
]
# live.paper: golden-week no-new-bar day -> honest skip (r660 precedent)

log_lines, fails, t0 = [], [], time.time()
for name, cmd in LEGS:
    t_leg = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=600)
        rc = p.returncode
        tail = (p.stdout or b'').decode('utf-8', errors='replace').strip().splitlines()
        last = tail[-1][:150] if tail else ''
        if not last:
            terr = (p.stderr or b'').decode('utf-8', errors='replace').strip().splitlines()
            last = ('ERR: ' + terr[-1][:130]) if terr else '(no output)'
    except subprocess.TimeoutExpired:
        rc, last = 99, 'TIMEOUT 600s'
    dt = time.time() - t_leg
    line = f"{name:24s} rc={rc:2d} {dt:5.1f}s | {last}"
    log_lines.append(line)
    print(line, flush=True)
    if rc not in (0,):
        fails.append((name, rc))

print(f"\nTOTAL legs={len(LEGS)} fails={len(fails)} elapsed={time.time()-t0:.1f}s")
if fails:
    print("FAILS:", fails)
with open('results/_r663bma_s6_log.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines) + f"\nTOTAL legs={len(LEGS)} fails={len(fails)}\n")
sys.exit(0 if not fails else 1)
