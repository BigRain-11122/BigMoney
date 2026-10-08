# r892 bm-a targeted S6 re-run driver -- 12 SZ members 10-08 bar catch-up window
# (backoff unlocked 21:41:06; sina published the SZ bars ~21:0x-21:1x per direct
# endpoint probe _r893 scratch; smoke 2 FAIL + 3 S6 reds all hinge on these bars).
# Same run_leg machinery as _r891bma_s6_driver.py (bloodline rolled one generation).
# ASCII console output only; JSON summary -> results/_r892bma_s6_rerun.json
import subprocess, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

LEGS = [
    ("update_daily", [sys.executable, "scripts/update_daily.py"], None, 300),
    ("live_paper", [sys.executable, "-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"}, 600),
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"], None, 300),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"], None, 300),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"], None, 300),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"], None, 900),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"], None, 300),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"], None, 300),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"], None, 300),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"], None, 300),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"], None, 300),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"], None, 300),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"], None, 300),
    ("build_status", [sys.executable, "-m", "monitor.build_status"], None, 600),
    ("token_meter", [sys.executable, "scripts/token_meter.py"], None, 300),
]

def run_leg(name, cmd, env_extra, timeout):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    t0 = datetime.datetime.now()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
        rc = p.returncode
        out = (p.stdout or b"").decode("utf-8", errors="replace")
        err = (p.stderr or b"").decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -9, "", "TIMEOUT"
    dt = (datetime.datetime.now() - t0).total_seconds()
    tail = "\n".join((out.strip().splitlines() or [""])[-3:])
    print(f"[{now()}] {name}: rc={rc} ({dt:.0f}s)", flush=True)
    if rc not in (0,):
        print(f"  TAIL>> {tail[:400]}", flush=True)
        if err.strip():
            print(f"  ERR>> {err.strip().splitlines()[-1][:300]}", flush=True)
    return {"name": name, "rc": rc, "sec": round(dt, 1), "tail": tail[-600:], "err_tail": err.strip()[-300:]}

def main():
    summary = {"start": now(), "legs": [], "purpose": "12 SZ member 10-08 bar catch-up targeted re-run (smoke 2 FAIL + 3 S6 reds root-cause)"}
    for name, cmd, env_extra, timeout in LEGS:
        summary["legs"].append(run_leg(name, cmd, env_extra, timeout))
    summary["end"] = now()
    reds = [[l["name"], l["rc"]] for l in summary["legs"] if l["rc"] != 0]
    summary["bad_legs"] = reds
    json.dump(summary, open("results/_r892bma_s6_rerun.json", "w", encoding="utf-8"), indent=1)
    print(f"== rerun done {summary['start']} -> {summary['end']}: {len(LEGS)} legs, reds={reds}", flush=True)
    return 0 if not reds else 1

if __name__ == "__main__":
    sys.exit(main())
