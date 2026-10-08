"""r782 bm-c S6 log key-face extractor (clone of r781 s6read pattern)."""
import io
import re

p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r782bmc_s6_log.txt"
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

s = seg("t35_paper_export")
for line in s.split("\n"):
    if "export" in line or "equity" in line.lower():
        print("t35:", line.strip()[:150])
        break

s = seg("daily_report")
for line in s.split("\n"):
    if "REPORT" in line and ("written" in line or "faces" in line or "regen" in line):
        print("daily_report:", line.strip()[:150])
        break

s = seg("strategy_scorecard")
for line in s.split("\n"):
    if "scorecard" in line.lower() or "written" in line.lower():
        print("scorecard:", line.strip()[:150])
        break

s = seg("token_meter")
for line in s.split("\n"):
    if "delta" in line.lower() or "bytes" in line.lower() or "usage" in line.lower():
        print("token:", line.strip()[:150])
        break

s = seg("live_paper")
for line in s.split("\n"):
    if "ENFORCE" in line or "blocked" in line or "anchor" in line.lower():
        print("live_paper:", line.strip()[:160])
        break

s = seg("t35_open_fill_verify")
for line in s.split("\n"):
    if "PASS" in line or "BREACH" in line or "0" == line.strip()[:1]:
        print("t35_open_fill:", line.strip()[:150])
        break

s = seg("market_clock_call")
for line in s.split("\n"):
    if "CALL" in line:
        print("market_clock:", line.strip()[:150])
        break
