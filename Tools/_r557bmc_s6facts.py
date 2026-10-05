# -*- coding: utf-8 -*-
"""r557 bm-c S6 facts probe: dual-lane split anchors per r547 law (verdict
fact pinned to the py_watermark leg block, never global first-match)."""
import re

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
s = open(ROOT + r"\results\_r557bmc_s6_log.txt", encoding="utf-8-sig", errors="replace").read()

m = re.search(r"streak (\d+)", s)
streak = m.group(1) if m else "?"
print("streak=" + streak)

seg = ""
if "=== 02_compute_audit" in s:
    seg_try = s.split("=== 02_compute_audit", 1)[1].split("=== 03_py_watermark", 1)[0]
    if '"verdict"' in seg_try:
        seg = seg_try
if not seg:
    seg = s.split("=== 03_py_watermark", 1)[1].split("=== 04_update_daily", 1)[0]
mv = re.search(r'"verdict": "([^"]+)"', seg)
if not mv:
    mv = re.search(r"verdict.: .(\w+)", seg)
print("py_verdict=" + (mv.group(1) if mv else "?"))

ca = s.split("=== 03_py_watermark", 1)[0]
cf = re.search(r"flags.{0,3}\[([^\]]*)\]", ca)
print("compute_audit_flags=" + (cf.group(1) if cf else "?"))

d = s.split("=== 07_clock_call", 1)[1].split("=== 08_lhb", 1)[0]
cm = re.search(r"cell=(\S+)", d)
print("cell=" + (cm.group(1) if cm else "?"))

rd = s.split("=== 05_market_regime", 1)[1].split("=== 06_scorecard", 1)[0]
rm = re.search(r'(state|regime)[=": ]+([A-Z_]+)', rd)
print("regime_face=" + (rm.group(2) if rm else "?"))

tm = s.split("=== 38_token_meter", 1)[1] if "=== 38_token_meter" in s else ""
tdm = re.search(r"delta[=: ] ?(\S+)", tm)
print("token_delta=" + (tdm.group(1) if tdm else "no-line"))

# supply floor / verdict faces inside compute_audit leg
sf = re.search(r"supply_floor[^\n]*", ca)
print("supply_floor=" + (sf.group(0)[:120] if sf else "?"))
