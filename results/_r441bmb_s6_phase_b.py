# S6 phase B: paper/panel legs. No new bars this round (20:36 bars consumed
# at r440); legs are idempotent same-day -> honest no-ops expected.
import subprocess, sys, io, time, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

LEGS = [
    ("live.paper", [sys.executable, "-m", "live.paper"]),
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_status", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
]

env = dict(os.environ)
env["BIGMONEY_REGIME_GUARD"] = "enforce"

results = {}
for name, cmd in LEGS:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1200, env=env)
        rc = r.returncode
        tail = (r.stdout or "").strip().splitlines()[-3:]
        err = (r.stderr or "").strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        rc = -9
        tail = ["TIMEOUT 1200s"]
        err = []
    results[name] = {"rc": rc, "sec": round(time.time() - t0, 1), "tail": tail, "err": err}
    print(f"[{rc}] {name} ({results[name]['sec']}s)")
    for l in tail[-2:]:
        print("    ", l[:220])

io.open("results/_r441bmb_s6_legs_b.json", "w", encoding="utf-8").write(
    __import__("json").dumps(results, ensure_ascii=False, indent=1))
print("== S6 phase B done ==")
