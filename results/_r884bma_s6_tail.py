# r884 bm-a S6 tail driver (r883 dead-leg residual: 12 legs after t35_open_fill_verify)
# ASCII console output only. Writes results/_r884bma_s6_tail.json summary.
import subprocess, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

LEGS = [
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
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

summary = {"start": now(), "legs": []}
for name, cmd in LEGS:
    t0 = datetime.datetime.now()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=900)
        rc = p.returncode
        out = (p.stdout or b"").decode("utf-8", errors="replace")
        err = (p.stderr or b"").decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -9, "", "TIMEOUT"
    dt = (datetime.datetime.now() - t0).total_seconds()
    tail = "\n".join((out.strip().splitlines() or [""])[-2:])
    print(f"[{now()}] {name}: rc={rc} ({dt:.0f}s)")
    if rc != 0:
        print(f"  TAIL>> {tail[:300]}")
        if err.strip():
            print(f"  ERR>> {err.strip().splitlines()[-1][:250]}")
    summary["legs"].append({"name": name, "rc": rc, "sec": round(dt, 1),
                            "tail": tail[-400:], "err_tail": err.strip()[-250:]})

summary["end"] = now()
summary["bad_legs"] = [(l["name"], l["rc"]) for l in summary["legs"] if l["rc"] != 0]
with open("results/_r884bma_s6_tail.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print("SUMMARY bad_legs:", summary["bad_legs"] or "NONE")
