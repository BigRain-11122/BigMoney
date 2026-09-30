# -*- coding: utf-8 -*-
# r491 bm-a: S6 maintenance chain driver (37-leg house sequence, per-leg rc log).
# Same law as r468 chain: dualrun MUST precede compute_audit (O evidence-window
# law); bar-gated paper family honest-skip when no new bar landed (cutoff 09-29,
# 09-30 bar source-unpublished per r485 -- worst window 10-09).
# New this round: after the chain, gate product evidence leg is separate.
import subprocess, sys, io, time, json, os, csv

LOG = r"logs\iteration-loop\s6_r491_chain.log"
SUMMARY = r"results\_r491bma_s6.json"

PRE_LEGS = [
    ("dualrun",   ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("audit",     ["python", "scripts\\compute_audit.py"]),
    ("wm_probe",  ["python", "scripts\\py_watermark.py", "probe"]),
    ("daily",     ["python", "scripts\\update_daily.py"]),
    ("regime",    ["python", "scripts\\market_regime.py"]),
    ("scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("clock",     ["python", "scripts\\market_clock_call.py", "run"]),
    ("lhb",       ["python", "scripts\\update_lhb.py"]),
    ("heat",      ["python", "scripts\\update_heat.py"]),
    ("futures",   ["python", "scripts\\update_futures.py"]),
    ("repo",      ["python", "scripts\\update_repo.py"]),
    ("options",   ["python", "scripts\\update_options.py"]),
    ("moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("sinamf",    ["python", "scripts\\update_sina_mf.py"]),
    ("astock",    ["python", "scripts\\update_astock_daily.py"]),
    ("etfdaily",  ["python", "scripts\\update_etf_daily.py"]),
    ("revosc",    ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minfeed",   ["python", "scripts\\update_minute_feed.py"]),
    ("ths",       ["python", "scripts\\update_ths_panel.py"]),
    ("ah",        ["python", "scripts\\ah_panel_puller.py"]),
    ("fundprem",  ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundam",    ["python", "scripts\\update_fundamental.py"]),
    ("blayer",    ["python", "-m", "firm.risk.b_layer_filter"]),
]

BAR_GATED = [
    ("livepaper", ["python", "-m", "live.paper"]),          # REGIME_GUARD env set by caller leg wrapper
    ("t35v",      ["python", "scripts\\t35_open_fill_verify.py"]),
    ("t24paper",  ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24promo",  ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr",      ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc",     ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid",      ["python", "scripts\\grid_paper.py", "run"]),
    ("sysv1",     ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35exp",    ["python", "scripts\\t35_paper_export.py", "run"]),
]

POST_LEGS = [
    ("dailysc",   ["python", "scripts\\daily_scorecard.py"]),
    ("dayrep",    ["python", "scripts\\daily_report.py", "run"]),
    ("ceolive",   ["python", "scripts\\ceo_live_usage.py"]),
    ("buildstat", ["python", "-m", "monitor.build_status"]),
    ("token",     ["python", "scripts\\token_meter.py"]),
]

def panel_tail_date():
    """510300 daily panel tail bar date (local ETF calendar primary source)."""
    for cand in (r"data\daily\sh510300.csv", r"data\daily\510300.csv"):
        if os.path.exists(cand):
            with io.open(cand, encoding="utf-8-sig", errors="replace") as fh:
                rows = list(csv.reader(fh))
            for row in reversed(rows):
                if row and len(row[0].split("-")) == 3:
                    return row[0]
    return "UNKNOWN"

def run_leg(log, name, cmd, env_extra=None):
    t0 = time.time()
    env = None
    if env_extra:
        env = dict(os.environ)
        env.update(env_extra)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=600,
                           encoding="utf-8", errors="replace", env=env)
        rc, out, err = p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        rc, out, err = -99, "", repr(e)
    dt = time.time() - t0
    log.write("[%s] rc=%d %.1fs %s\n" % (name, rc, dt, out[-700:].replace("\n", " | ")[:700]))
    if err:
        log.write("[%s] stderr: %s\n" % (name, err[-300:].replace("\n", " | ")))
    log.flush()
    return rc

def main():
    log = io.open(LOG, "w", encoding="utf-8")
    results = {}
    tail = panel_tail_date()
    today = time.strftime("%Y-%m-%d")
    has_new_bar = (tail == today)
    log.write("S6 chain r491 start %s pre=%d gated=%d post=%d panel_tail=%s today=%s new_bar=%s\n"
              % (time.strftime("%Y-%m-%d %H:%M:%S"), len(PRE_LEGS), len(BAR_GATED),
                 len(POST_LEGS), tail, today, has_new_bar))
    log.flush()
    bad = []
    for name, cmd in PRE_LEGS + POST_LEGS:
        rc = run_leg(log, name, cmd)
        results[name] = rc
        if rc not in (0,):
            bad.append((name, rc))
    if has_new_bar:
        for name, cmd in BAR_GATED:
            # REGIME_GUARD anchoring gate: enforce only when a new bar exists
            rc = run_leg(log, name, cmd, env_extra={"BIGMONEY_REGIME_GUARD": "enforce"})
            results[name] = rc
            if rc not in (0,):
                bad.append((name, rc))
    else:
        for name, _ in BAR_GATED:
            results[name] = "skip_no_new_bar"
        log.write("[bar-gated family] honest skip: no new bar (tail=%s, today=%s per r485 source-lag)\n" % (tail, today))
    log.write("S6 chain done %s non_green=%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), bad))
    log.close()
    with io.open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump({"round": "r491 bm-a", "panel_tail": tail, "today": today,
                   "new_bar": has_new_bar, "legs": results,
                   "non_green": bad, "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")},
                  fh, ensure_ascii=False, indent=1)
    print("chain done non_green=", bad)

if __name__ == "__main__":
    main()
