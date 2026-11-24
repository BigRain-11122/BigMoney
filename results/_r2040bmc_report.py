# -*- coding: utf-8 -*-
import io
import time

ROW = """| {now} | r2040 **addendum**（送达核验） | commit **9fc1f9e333** 已推 origin/main（b92023acec..9fc1f9e333），fetch 后 **AHEAD=0 / BEHIND=0**，`git ls-tree -r --name-only origin/main` 六件新面孔全在位（scripts/cb_parking_bakeoff.py / results/cb_parking_bakeoff.json / research/CB_PARKING_BAKEOFF.md / 负控 results/_r2040bmc_parking_negative.py / 收口 _r2040bmc_closeout.py、_r2040bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例；同批带 state-bm-c.json / fleet/machines/bm-c.json / fleet/round_reports-bm-c.md 三件簿记）→ **本地未达 origin commit 数=0**。**本窗坑录（负控当场抓出·已修）**：`check()` 的 `near()` 只写 `abs(a-b)<=tol`，遇到数字位被写成字符串时抛 TypeError 而不是判红——「自检可以红不可以崩」的反面；正法=先过类型闸（bool 也挡）再比数，负控 L10 因此从 traceback 变成 rc3。记账：本行 1 处（轮报告 addendum），本轮合计 4。 |
"""

with io.open("fleet/round_reports-bm-c.md", "a", encoding="utf-8") as f:
    f.write(ROW.format(now=time.strftime("%Y-%m-%d %H:%M")))
print("appended")
