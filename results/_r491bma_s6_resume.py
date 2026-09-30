# -*- coding: utf-8 -*-
# r491 bm-a: S6 chain RESUME (runner killed by 5-min silent tool timeout at
# [repo]; legs after repo never ran). Detached via Start-Process.
# Bar-gate corrected: the [daily] leg itself landed 36 new rows -> panel tail
# advanced to 2026-09-30 mid-chain -> gated paper family NOW RUNS (live.paper
# itself already ran synchronously inside the daily hook, rc=0 -- idempotent
# re-run no-ops / anchor-verifies only).
import subprocess, sys, io, time, json, os, csv

LOG = r"logs\iteration-loop\s6_r491_chain.log"
SUMMARY = r"results\_r491bma_s6.json"

RESUME_LEGS = [
    ("options",   ["python", "scripts\\update_options.py"]),   # gate: refresh already in flight
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
    ("livepaper", ["python", "-m", "live.paper"]),
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
    for cand in (r"data\daily\sh510300.csv", r"data\daily\510300.csv"):
        if os.path.exists(cand):
            with io.open(cand, encoding="utf-8-sig", errors="replace") as fh:
                rows = list(csv.reader(fh))
            for row in reversed(rows):
                if row and len(row[0].split("-")) == 3:
                    return row[0]
    return "UNKNOWN"

def run_leg(log, name, cmd):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=900,
                           encoding="utf-8", errors="replace")
        rc, out, err = p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        rc, out, err = -99, "", repr(e)
    dt = time.time() - t0
    log.write("[resume][%s] rc=%d %.1fs %s\n" % (name, rc, dt, out[-700:].replace("\n", " | ")[:700]))
    if err:
        log.write("[resume][%s] stderr: %s\n" % (name, err[-300:].replace("\n", " | ")))
    log.flush()
    return rc

def main():
    log = io.open(LOG, "a", encoding="utf-8")
    results = {}
    tail = panel_tail_date()
    today = time.strftime("%Y-%m-%d")
    has_new_bar = (tail == today)
    log.write("S6 chain r491 RESUME %s panel_tail=%s new_bar=%s\n"
              % (time.strftime("%Y-%m-%d %H:%M:%S"), tail, has_new_bar))
    log.flush()
    bad = []
    legs = list(RESUME_LEGS)
    if has_new_bar:
        legs += BAR_GATED + POST_LEGS
    else:
        log.write("[resume] bar-gated family honest skip (tail=%s)\n" % tail)
        legs += POST_LEGS
    for name, cmd in legs:
        rc = run_leg(log, name, cmd)
        results[name] = rc
        if rc not in (0,):
            bad.append((name, rc))
    log.write("S6 chain RESUME done %s non_green=%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), bad))
    log.close()
    with io.open(SUMMARY, "w", encoding="utf-8") as fh:
        json.dump({"round": "r491 bm-a (resume)", "panel_tail": tail, "today": today,
                   "new_bar": has_new_bar, "legs": results, "non_green": bad,
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")},
                  fh, ensure_ascii=False, indent=1)
    print("resume done non_green=", bad)

if __name__ == "__main__":
    main()
