# -*- coding: utf-8 -*-
"""r239 T-75 wiring: byte-precise single-line insert of daily_report.py run
into the OS-loop S6 chain (Tools/iteration_prompt.txt), before the
monitor.build_status leg. Preserves: no-BOM UTF-8, LF-only single line
(R236 iteration_prompt precedent). Idempotent: skips if already wired.
"""
import io

P = "Tools/iteration_prompt.txt"
ANCHOR = "→ python -m monitor.build_status 刷新总控面板"
LEG = ("→ python scripts\\daily_report.py run（T-75 每日战报·O-0940："
       "工作日≥15:45 且当日未生成→四面战报（战况全账户族/研发 24h 吞吐/决策日志尾/明日队列）"
       "落 docs\\daily_report\\REPORT-YYYYMMDD.md+json 孪生·append-only 禁改史；"
       "周末/当日已生成/<15:45=合法 no-op；selftest 子命令=离线自检；"
       "exit 0=正常/no-op、2=机制故障原样上报勿掩盖）")

raw = io.open(P, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf"), "unexpected BOM"
txt = raw.decode("utf-8")
if "daily_report.py run" in txt:
    print("already wired, no-op")
    raise SystemExit(0)
assert ANCHOR in txt, "anchor not found"
assert txt.count(ANCHOR) == 1, "anchor not unique"
txt = txt.replace(ANCHOR, LEG + ANCHOR, 1)
io.open(P, "wb").write(txt.encode("utf-8"))
check = io.open(P, "rb").read()
assert b"\r" not in check, "CRLF leaked"
print("wired OK: daily_report.py run inserted before monitor.build_status leg "
      "(size %d -> %d)" % (len(raw), len(check)))
