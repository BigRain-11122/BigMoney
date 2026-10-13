# -*- coding: utf-8 -*-
# r971 S6 chain (bm-c) - full maintenance sequence, self-guarding legs, background runner
import subprocess, sys, time, io, os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
LOG = os.path.join(REPO, r"results\_r971bmc_s6_chain.log")
out = io.open(LOG, "w", encoding="utf-8", newline="")
def w(msg):
    out.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), msg)); out.flush()

LEGS = [
    ("dualrun",      [sys.executable, "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit",[sys.executable, "scripts\\compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts\\py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts\\update_daily.py"]),
    ("market_regime",[sys.executable, "scripts\\market_regime.py"]),
    ("scorecard",    [sys.executable, "scripts\\strategy_scorecard.py"]),  # host=bm-a guard: honest skip
    ("market_clock", [sys.executable, "scripts\\market_clock_call.py", "run"]),
    ("update_lhb",   [sys.executable, "scripts\\update_lhb.py"]),
    ("zt_pool",      [sys.executable, "scripts\\update_zt_pool.py"]),
    ("heat",         [sys.executable, "scripts\\update_heat.py"]),          # host guard
    ("futures",      [sys.executable, "scripts\\update_futures.py"]),
    ("repo",         [sys.executable, "scripts\\update_repo.py"]),
    ("options",      [sys.executable, "scripts\\update_options.py"]),        # host guard
    ("moneyflow",    [sys.executable, "scripts\\update_moneyflow.py"]),     # host guard
    ("sina_mf",      [sys.executable, "scripts\\update_sina_mf.py"]),       # host guard
    ("astock",       [sys.executable, "scripts\\update_astock_daily.py"]),  # host bm-b guard
    ("etf_daily",    [sys.executable, "scripts\\update_etf_daily.py"]),     # host bm-b guard
    ("thermo",       [sys.executable, "scripts\\regime_thermo_build.py"]),
    ("dualarm",      [sys.executable, "scripts\\regime_gate_dualarm.py", "run"]),  # host bm-b guard
    ("rev_osc",      [sys.executable, "scripts\\rev_osc_signal_export.py", "run"]), # host bm-b guard
    ("minute_feed",  [sys.executable, "scripts\\update_minute_feed.py"]),   # host bm-b guard
    ("ths_panel",    [sys.executable, "scripts\\update_ths_panel.py"]),     # host guard
    ("ah_panel",     [sys.executable, "scripts\\ah_panel_puller.py"]),     # host guard
    ("fund_premium", [sys.executable, "scripts\\update_fund_premium.py", "snapshot"]),  # bm-c lane
    ("fundamental",  [sys.executable, "scripts\\update_fundamental.py"]),
    ("b_layer",      [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("fund_statements",[sys.executable, "scripts\\update_fund_statements.py"]),  # host guard
    ("live_paper",   [sys.executable, "-m", "live.paper"]),   # REGIME_GUARD env set below
    ("t35_openfill", [sys.executable, "scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect", [sys.executable, "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_promotion",[sys.executable, "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr_paper",   [sys.executable, "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper",  [sys.executable, "scripts\\alloc_paper.py", "run"]),
    ("grid_paper",   [sys.executable, "scripts\\grid_paper.py", "run"]),
    ("sysv1_paper",  [sys.executable, "scripts\\system_v1_paper.py", "run"]),  # host bm-a guard
    ("t35_export",   [sys.executable, "scripts\\t35_paper_export.py", "run"]),
    ("daily_score",  [sys.executable, "scripts\\daily_scorecard.py"]),        # host bm-a guard
    ("daily_report", [sys.executable, "scripts\\daily_report.py", "run"]),
    ("ceo_usage",    [sys.executable, "scripts\\ceo_live_usage.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),         # host bm-a guard
    ("token_meter",  [sys.executable, "scripts\\token_meter.py"]),
]

env = dict(os.environ)
env["BIGMONEY_REGIME_GUARD"] = "enforce"   # T-21 v3: date gate open since 2026-10-01; legs self-guard no-op without new bars
env["PYTHONIOENCODING"] = "utf-8"

rcs = {}
for name, cmd in LEGS:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, timeout=1800)
        rc = p.returncode
        tail = (p.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        last = tail[-1][:200] if tail else ""
        err = (p.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        lasterr = err[-1][:200] if err else ""
    except Exception as e:
        rc = -99; last = "EXC %s" % e; lasterr = ""
    rcs[name] = rc
    w("%-15s rc=%d  %.1fs  %s%s" % (name, rc, time.time()-t0, last, (" | ERR:"+lasterr) if rc != 0 else ""))

w("CHAIN DONE rcs=" + repr(rcs))
bad = {k: v for k, v in rcs.items() if v not in (0,)}
w("NONZERO: %s" % (bad if bad else "ALL rc0"))
out.close()
