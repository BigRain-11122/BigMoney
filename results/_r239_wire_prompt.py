# -*- coding: utf-8 -*-
"""R239 T-75/T-74 wiring v2: byte-precise insertion into Tools/iteration_prompt.txt.
Separator style in the S6 chain is '）→ python ...' (arrow, no leading space).
(a) market_clock_call.py run inserted between market_regime leg and update_lhb leg
(b) daily_report.py run inserted between daily_scorecard leg and monitor.build_status leg
Idempotent; atomic (single write only after both asserts pass)."""
import io

P = "Tools/iteration_prompt.txt"
src = open(P, "r", encoding="utf-8", newline="").read()

LEG_A = ("python scripts\\market_clock_call.py run（T-74 s1 市场时钟当日判定·MARKET_CLOCK_COMBO s0 v1.0："
         "读 v3 政体+LHB 热度复合+core48 板块面→results\\market_clock\\CALL-*+call_latest.json；"
         "幂等零网络当日再生；exit 0=正常、2=机制故障原样上报勿掩盖；selftest 子命令=离线自检）→ ")
LEG_B = ("python scripts\\daily_report.py run（T-75 每日战报·O-20260926-0940：四面上聚合一页 "
         "docs\\daily_report\\REPORT-YYYYMMDD.md+JSON 孪生，当日重复运行原地再生幂等、他日永不动；"
         "token 行=T-77 消费面；exit 0=正常、2=机制故障原样上报勿掩盖；selftest 子命令=离线自检）→ ")

if "market_clock_call.py" in src or "daily_report.py" in src:
    print("already wired -- no changes")
    raise SystemExit(0)

i_reg = src.find("python scripts\\market_regime.py")
i_sco = src.find("python scripts\\daily_scorecard.py")
assert i_reg >= 0 and i_sco >= 0, "anchor legs missing"
i_lhb = src.find("python scripts\\update_lhb.py", i_reg)
i_bst = src.find("python -m monitor.build_status", i_sco)
assert i_lhb > i_reg, "update_lhb leg after market_regime missing"
assert i_bst > i_sco, "build_status leg after daily_scorecard missing"

src = src[:i_lhb] + LEG_A + src[i_lhb:]
# recompute i_bst: insertion A shifted positions
i_bst = src.find("python -m monitor.build_status", i_sco)
src = src[:i_bst] + LEG_B + src[i_bst:]

with io.open(P, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("wired A+B | new chars:", len(src))
