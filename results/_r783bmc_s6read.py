"""r783 bm-c S6 log key-face extractor (clone of r782 s6read pattern)."""
import io
import re

p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r783bmc_s6_log.txt"
txt = io.open(p, encoding="utf-8", errors="replace").read()


def seg(name):
    m = re.search(r"===== %s =====(.*)" % name, txt, re.S)
    return m.group(1) if m else ""


s = seg("py_watermark")
m = re.search(r'"verdict": "([a-z_]+)"', s)
print("py_watermark verdict:", m.group(1) if m else "N/A")

s = seg("compute_audit")
m = re.search(r'"flags": \[([^\]]*)\]', s)
print("compute_audit flags:", m.group(1) if m else "N/A")

s = seg("update_daily")
for line in s.split("\n"):
    if "new rows" in line.lower() or "cutoff" in line.lower():
        print("update_daily:", line.strip()[:160])

s = seg("update_fund_premium")
for line in s.split("\n"):
    if "NAV" in line or "no-op" in line.lower() or "expected" in line.lower():
        print("fund_premium:", line.strip()[:160])

s = seg("t35_paper_export")
for line in s.split("\n"):
    if "export" in line or "equity" in line.lower():
        print("t35:", line.strip()[:150])
        break

s = seg("market_regime")
for line in s.split("\n"):
    if "regime" in line.lower() or "state" in line.lower() or "ORANGE" in line:
        print("regime:", line.strip()[:160])
        break

s = seg("live_paper")
for line in s.split("\n"):
    if "ENFORCE" in line or "blocked" in line or "anchor" in line.lower():
        print("live_paper:", line.strip()[:160])
        break

s = seg("daily_report")
for line in s.split("\n"):
    if "REPORT" in line and ("written" in line or "faces" in line or "regen" in line):
        print("daily_report:", line.strip()[:150])
        break

s = seg("token_meter")
for line in s.split("\n"):
    if "delta" in line.lower() or "bytes" in line.lower() or "usage" in line.lower():
        print("token:", line.strip()[:150])
        break

s = seg("market_clock_call")
for line in s.split("\n"):
    if "CALL" in line:
        print("market_clock:", line.strip()[:150])
        break

s = seg("pool_dualrun_reconcile")
for line in s.split("\n"):
    if "streak" in line.lower() or "drift" in line.lower() or "ZERO" in line:
        print("dualrun:", line.strip()[:160])
        break

s = seg("aggressive_lab")
for line in s.split("\n"):
    if "no-op" in line.lower() or "marks" in line.lower():
        print("aggr:", line.strip()[:160])
        break
