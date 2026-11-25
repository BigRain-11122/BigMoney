#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""append the r2111 round line to round_reports-bm-c.md with a fresh read (multi-host tree)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-26T00:4x+08:00 | r2111 | bm-c | **CONTENTION 轮**（证据 `results/_repo_write_contention.bm-c.json`："
    "rc3 CONTENTION，2 宿主存活（98008@20:02 interactive + 本窗 98944@00:20），开工前 22 张共享面已被别宿主写过、"
    "重叠窗内不可归因 0 张；工作树脏 1,957 件）→ 按 r1907 只落新增文件面，禁改共享面、禁重跑 S6 链、不跑全量冒烟；"
    "state/心跳为多宿主共写态面（对端持有），本窗不碰。watermark verdict=**绿**（`results/watermark_red.json` "
    "red=false lane=healthy）。**PRODUCT**：把近三轮各犯一次的同一个缺陷做成**静态闸**——r2105 `%/yr`、r2109 `5%%`、"
    "r2110 表头裸 `%`，三种症状同根：「这一串到底走不走 `%`」决定转义方向，而两者规则正好相反。`Tools/page_fmt_guard.py` "
    "用 `ast` 读源码**不执行**，只问两个问题：`LITERAL_DOUBLE_PCT`（含 `%%` 却没走 `%`，读者会看到两个百分号）与 "
    "`BARE_PCT_IN_FORMAT`（走了 `%` 但含非法转换，渲染期 ValueError）。**全仓首跑：2,666 文件 / 1,194 个页面渲染器 / "
    "28,939 个含 `%` 常量 → 31 处字面 `%%` + 5 处非法转换 + 1 处读不出的旧脚本**；再拿发布面逐字对账：**15 个 .md 现在真的"
    "躺着字面 `%%`**（`ETF_BOOK_CAPACITY_FLOOR_GAP.md` 5 处、`HANDOVER.md` 4 处、`IDX_FUT_BASIS_VERDICT.md` 3 处、"
    "`POLICY_RETURN_LADDER.md` 2 处…）——不是理论风险，是已经发到读者眼里的字。精确度也当场校准：首版 137 条里 48 条 `bare` "
    "是 `(\"%.\" + str(d) + \"f\") % x` 这种拼接片段、多数 `literal` 是断言消息（`_ok(...)` 实参），加「片段排除 + "
    "写入器实参才判」两条后降到 37 条；亲自核过真伪两例（`etf_book_capacity_floor_gap.py:328` 真缺陷 / "
    "`astock_veto_hedge_band.py:551` 误报已消）。｜证据：`--selftest` **19/19 ALL_PASS**（6 条 fixture 覆盖 clean/literal/"
    "bare/非页面/f-string/docstring + 标签可分辨 + `%.3f%%`/`%-8s|%05.2f|%+d|%*d` 不误报 + `%/yr`/`% |` 必报 + "
    "语法错误不静默 + 真树跑通且每条带文件行号）；扫描面 `results/page_fmt_guard.scan.json`；发布面实证 "
    "`results/_r2111bmc_leak_verify.json`（verdict=SHIPPED_LITERAL_DOUBLE_PCT）+ 直接扫 md 全文 15 件；QA "
    "`qa/page-fmt-guard-r2111.md`。｜未做（如实）：①**未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`**（两者均为对端"
    "未提交脏面，竞争窗禁写共享面）——本闸当前是独立可跑工具不是链上腿；②**未修那 31 条真实泄漏**（全在他人脚本面，修法"
    "明确：未格式化的串把 `%%` 改回 `%`，留独占窗）；③不判实参个数不匹配（需类型信息）；④全量冒烟未跑；⑤state/心跳未写"
    "（多宿主共写态面，对端持有）。｜S0.5 双扫：fleet/orders **117 件** vs 心智回执集 → 最新令 O-20261124-2300 已回执、"
    "**未回执 0**；集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B sha256 79e3083b85c130b8…** == 自持水位 → "
    "**零新决策零动作**（`git show > file` 直落字节、不带 `2>&1`、不经 PS 字符串往返）。｜S7：孤儿面=**0**"
    "（`py_faces=8` / resident_servers=2，`results/_orphan_face_probe.bm-c.json`）；attrition tripwire 本窗未跑（无账本"
    "改动）；IterationLoop / Watchdog / hooks 未触碰（脏树轮不做自愈）。｜**CEO 三行**：当前活＝把「同一种页面百分号缺陷」从"
    "连续三轮各炸一次改成出生即拦的静态闸｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\qa\\page-fmt-guard-r2111.md`"
    "（2026-11-26T00:4x·全仓 2,666 文件查出 31 处字面 `%%`+5 处非法转换·15 个已发布页面确实印着 `%%`）｜下个里程碑＝独占窗把"
    "这 31 处改回单 `%` 并把闸接进链与冒烟腿（≤48h）| 记账：轮报告 1 处 + QA 1 件 = 2\n"
)

with io.open(P, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(LINE)
print("appended %d chars; file now %d bytes" % (len(LINE), os.path.getsize(P)))
