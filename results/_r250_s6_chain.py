"""r250 bm-b S6 maintenance chain runner (28 legs, weekend honest no-op expected).

Per-leg: capture exit code + last stdout line; full output to logs/s6_r250/leg_NN.log.
Exit contract honored per leg (0/2/3 reported as-is, never masked).
"""
import subprocess
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PY = sys.executable
LEGS = [
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts/update_lhb.py"]),
    ("update_heat", [PY, "scripts/update_heat.py"]),
    ("update_futures", [PY, "scripts/update_futures.py"]),
    ("update_options", [PY, "scripts/update_options.py"]),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"]),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("live_paper", [PY, "-m", "live.paper"]),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [PY, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
]

LOGDIR = os.path.join("logs", "s6_r250")
os.makedirs(LOGDIR, exist_ok=True)
results = []
for i, (name, cmd) in enumerate(LEGS, 1):
    logf = os.path.join(LOGDIR, "leg_%02d_%s.log" % (i, name))
    try:
        with open(logf, "w", encoding="utf-8") as lf:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=900, env=os.environ.copy())
            rc = p.returncode
            out = p.stdout.decode("utf-8", errors="replace")
            lf.write(out)
        lines = [l for l in out.splitlines() if l.strip()]
        last = lines[-1][:220] if lines else "(empty)"
    except subprocess.TimeoutExpired:
        rc, last = "TIMEOUT", "leg exceeded 900s"
    except Exception as e:
        rc, last = "ERR", repr(e)[:220]
    results.append((i, name, rc))
    print("%02d %-20s exit=%s | %s" % (i, name, rc, last))

bad = [r for r in results if r[2] != 0]
print("SUMMARY: %d legs, non-zero=%d %s" % (len(results), len(bad), bad if bad else ""))
