# r574 bm-b S6 chain driver: runs the full data/maintenance pipeline in the
# protocol order, captures per-command rc + tail line for the round report.
# (reuse of _r561bmb_s6_driver.py per reuse-not-rewrite law; holiday no-op
# faces expected; W82 engine burn running in parallel at BelowNormal)
import subprocess, sys, io, os, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CHAIN = [
    ("dualrun",   ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("audit",     ["python", "scripts\\compute_audit.py"]),
    ("wm",        ["python", "scripts\\py_watermark.py", "probe"]),
    ("daily",     ["python", "scripts\\update_daily.py"]),
    ("regime",    ["python", "scripts\\market_regime.py"]),
    ("scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("mcc",       ["python", "scripts\\market_clock_call.py", "run"]),
    ("lhb",       ["python", "scripts\\update_lhb.py"]),
    ("heat",      ["python", "scripts\\update_heat.py"]),
    ("futures",   ["python", "scripts\\update_futures.py"]),
    ("repo",      ["python", "scripts\\update_repo.py"]),
    ("options",   ["python", "scripts\\update_options.py"]),
    ("mflow",     ["python", "scripts\\update_moneyflow.py"]),
    ("sinamf",    ["python", "scripts\\update_sina_mf.py"]),
    ("astock",    ["python", "scripts\\update_astock_daily.py"]),
    ("etf",       ["python", "scripts\\update_etf_daily.py"]),
    ("revosc",    ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minfeed",   ["python", "scripts\\update_minute_feed.py"]),
    ("ths",       ["python", "scripts\\update_ths_panel.py"]),
    ("ah",        ["python", "scripts\\ah_panel_puller.py"]),
    ("fundprem",  ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundament", ["python", "scripts\\update_fundamental.py"]),
    ("blayer",    ["python", "-m", "firm.risk.b_layer_filter"]),
]

PAPER = [
    ("paper",     ["python", "-m", "live.paper"]),
    ("t35ofv",    ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24pa",     ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24pb",     ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr",      ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc",     ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid",      ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1",     ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35exp",    ["python", "scripts\\t35_paper_export.py", "run"]),
]

TAIL = [
    ("dscore",    ["python", "scripts\\daily_scorecard.py"]),
    ("dreport",   ["python", "scripts\\daily_report.py", "run"]),
    ("liveuse",   ["python", "scripts\\ceo_live_usage.py"]),
    ("bstatus",   ["python", "-m", "monitor.build_status"]),
    ("token",     ["python", "scripts\\token_meter.py"]),
]

def run(tag, cmd, env=None):
    e = dict(os.environ)
    if env: e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=e, timeout=900)
    tail = (p.stdout or '').strip().splitlines()
    last = tail[-1][:150] if tail else (p.stderr or '').strip().splitlines()[-1][:150] if (p.stderr or '').strip() else ''
    print(f"{tag:10s} rc={p.returncode} :: {last}")
    return p.returncode

def new_bar_present():
    # holiday 2026-10-02 (National Day week): market closed, no new bar
    # expected. Gate = panel file mtime changed within the last 45 min AND
    # tail is a fresh bar day (r561 generic gate; r573 closed 11:59 today).
    try:
        import csv
        with open('data/daily/sh510300.csv', 'rb') as f:
            lines = f.read().decode('utf-8', errors='replace').strip().splitlines()
        tail_date = lines[-1].split(',')[0]
        mtime = os.path.getmtime('data/daily/sh510300.csv')
        age_min = (datetime.datetime.now().timestamp() - mtime) / 60
        new = (age_min < 45)
        print(f"[gate] panel tail={tail_date} mtime_age={age_min:.0f}min new_bar={new}")
        return new
    except Exception as ex:
        print(f"[gate] detection failed {ex}; conservative no-new-bar")
        return False

print('=== S6 batch 1 (supply/maintenance) ===')
for t, c in CHAIN: run(t, c)

print('=== paper chain gate ===')
if new_bar_present():
    print('=== S6 batch 2 (paper chain, REGIME_GUARD=enforce) ===')
    for t, c in PAPER: run(t, c, env={'BIGMONEY_REGIME_GUARD': 'enforce'})
else:
    print('=== S6 batch 2 SKIPPED (no new bar; paper scripts are per-day idempotent no-ops) ===')

print('=== S6 batch 3 (reporting) ===')
for t, c in TAIL: run(t, c)
print('=== S6 done ===')
