import subprocess, sys, time

LEGS = [
    ("dualrun",  [sys.executable, "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("audit",    [sys.executable, "scripts\\compute_audit.py"]),
    ("wm_probe", [sys.executable, "scripts\\py_watermark.py", "probe"]),
    ("daily",    [sys.executable, "scripts\\update_daily.py"]),
    ("regime",   [sys.executable, "scripts\\market_regime.py"]),
    ("scorecard",[sys.executable, "scripts\\strategy_scorecard.py"]),
    ("clock",    [sys.executable, "scripts\\market_clock_call.py", "run"]),
    ("lhb",      [sys.executable, "scripts\\update_lhb.py"]),
    ("heat",     [sys.executable, "scripts\\update_heat.py"]),
    ("futures",  [sys.executable, "scripts\\update_futures.py"]),
    ("repo",     [sys.executable, "scripts\\update_repo.py"]),
    ("options",  [sys.executable, "scripts\\update_options.py"]),
    ("moneyflow",[sys.executable, "scripts\\update_moneyflow.py"]),
    ("sina_mf",  [sys.executable, "scripts\\update_sina_mf.py"]),
    ("ths",      [sys.executable, "scripts\\update_ths_panel.py"]),
    ("ah",       [sys.executable, "scripts\\ah_panel_puller.py"]),
    ("fundmntl", [sys.executable, "scripts\\update_fundamental.py"]),
    ("b_layer",  [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("aggr",     [sys.executable, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc",    [sys.executable, "scripts\\alloc_paper.py", "run"]),
    ("grid",     [sys.executable, "scripts\\grid_paper.py", "run"]),
    ("sysv1",    [sys.executable, "scripts\\system_v1_paper.py", "run"]),
    ("t35exp",   [sys.executable, "scripts\\t35_paper_export.py", "run"]),
    ("dscore",   [sys.executable, "scripts\\daily_scorecard.py"]),
    ("dreport",  [sys.executable, "scripts\\daily_report.py", "run"]),
    ("liveuse",  [sys.executable, "scripts\\ceo_live_usage.py"]),
    ("build",    [sys.executable, "-m", "monitor.build_status"]),
    ("token",    [sys.executable, "scripts\\token_meter.py"]),
]

results = []
for name, cmd in LEGS:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                           creationflags=0x08000000)
        rc = r.returncode
        out = (r.stdout or "").strip().splitlines()
        tail = out[-1][:160] if out else (r.stderr or "").strip()[:160]
    except subprocess.TimeoutExpired:
        rc, tail = 99, "TIMEOUT 600s"
    dt = time.time() - t0
    results.append((name, rc, round(dt, 1), tail))
    print("%-9s rc=%d %6.1fs | %s" % (name, rc, dt, tail), flush=True)

bad = [r for r in results if r[1] not in (0, 1)]
print("\nSUMMARY: %d legs, rc0/1=%d, bad=%d" % (len(results), len(results)-len(bad), len(bad)))
for name, rc, dt, tail in bad:
    print("BAD %s rc=%d %s" % (name, rc, tail[:120]))
