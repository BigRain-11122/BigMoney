#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""append the r2109 round-report line to round_reports-bm-c.md (fresh read, one line)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

LINE = (
    "2026-11-25T23:5x+08:00 | r2109 | bm-c | **CONTENTION 轮**（证据 "
    "`results/_repo_write_contention.bm-c.json`：rc3 CONTENTION，2 宿主存活"
    "（98008@20:02 interactive + 本窗 100380@23:45），开工前 20 张共享面已被别宿主写过、"
    "重叠窗内不可归因 0 张；工作树脏 ~1,950 件）→ 按 r1907 只落新增文件面，禁改共享面、"
    "禁重跑 S6 链、不跑全量冒烟；state/心跳为多宿主共写态面（对端仍持有），本窗不碰。"
    "watermark verdict=**绿**（`results/watermark_red.json` red=false lane=healthy）。"
    "**PRODUCT**：把梯子那两个「写死的风险常数」第一次沿时间摊开——`L2_CARRY_VOL=4.0` 与 "
    "`RHO=0.10` 是八年平均，而风险预算不能建在平均值上。期货块（1 手 IC + 1 手 IM）声明波动 "
    "**8.96%**，全样本实测 **13.64%**（少报 4.67 pp）；120 日滚动窗里相关 5%→95% 跨 **0.239**，"
    "块波动中位 **11.69%**、95% **24.55%**、最大 **24.70%**，**70.4%** 的窗高于声明数。"
    "两件要紧的：①**压力下分散消失**——95% 窗块波动是中位窗的 **2.10 倍**，且 95% 相关比中位高 "
    "0.116，最同向的 120 日窗收在 **2024-02-07（相关 0.966）**，也就是说两条腿在真正出事时一起动；"
    "②**逐年一看就懂**——2023 块波动 6.51%（在声明数以内）、**2024 21.72%（声明数的 2.4 倍）**、"
    "2025 10.97%、2026 12.92%，同一块期货在不同年份的风险差 3 倍，一个常数表达不了。"
    "跨面对照：`idx_fut_carry_ladder_risk` 同一档 `l2_vol_measured_pct` = **13.636%**，与本面逐位相同 "
    "→ CROSS_FACE_MATCHES（兄弟面印的 10.46% 已含权益袖，本面 8.96% 只是期货块，页内写清不是两答案）。"
    "｜证据：`--selftest` **21/21**；`check` **CHECK_OK**（漂移说 STALE、同输入不符说 CHECK FAILED "
    "且**不含 STALE**）；负控 `python results/_r2109bmc_ladder_stability_negative.py` **10/10 "
    "ALL_CONTROLS_PASS**（手改数字→CHECK FAILED 且无 STALE／阶梯漂移→STALE／腿漂移→STALE／"
    "兄弟面漂移→STALE／判词翻面→CHECK FAILED／删跨面块→CHECK FAILED／阶梯公式复现声明数 8.9627 vs 8.963／"
    "页面必须带三个判词与跨面判词）。面 `results/idx_fut_carry_ladder_stability.json`、页面 "
    "`research/IDX_FUT_CARRY_LADDER_STABILITY.md`、QA `qa/ladder-stability-r2109.md`。"
    "｜本轮自捕两枚：①负控「荒谬声明数」那条腿写错（judge 的覆盖面读数由 summarize 算好，测试却拿 0.5 的 "
    "summary 去配 1e6 的声明数）——是断言错不是判据错，改后转绿；②页面第二节表头走的是无格式化 "
    "`add()` 却写了转义 `%%`，渲染成 `5%%`（页面上肉眼可见的 `%%` 就是信号）。"
    "｜未做（如实）：①未改梯子两个常数（`policy_return_lattice.py` 共享面，竞争窗禁写）；"
    "②未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面）；"
    "③全量冒烟未跑；④state/心跳未写（多宿主共写态面）。"
    "｜S0.5 双扫：fleet/orders **117 件** vs 心跳 orders_ack 归 **258 条** → **未回执 0**；"
    "集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B sha256 79e3083b85c130b8…** == 自持水位 "
    "→ **零新决策零动作**（`git show > file` 直落字节、不带 2>&1、不经 PS 字符串往返）。"
    "｜S7：孤儿面=**0**（`py_faces=9` / resident_servers=2，`results/_orphan_face_probe.bm-c.json`）；"
    "attrition tripwire 本窗未跑（无账本改动）；IterationLoop / Watchdog / hooks 未触碰（脏树轮不做自愈）。"
    "｜**本地未达 origin commit 数=0**（commit **70eaa7d315** 直推 origin/main 475b7a3942..70eaa7d315，"
    "两次 remote rejected（Internal Server Error / commit_refs_rules）后第三次成功，非 FF 未发生；"
    "fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；`git ls-tree` 核验 **5/5** "
    "件在位，`_r[0-9]*` 文件按忽略规则 `git add -f` 入库）。"
    "｜**CEO 三行**：当前活＝把 carry 梯子那两个写死的风险常数沿时间摊开，回答「这个数是常数还是平均值」"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\IDX_FUT_CARRY_LADDER_STABILITY.md`"
    "（2026-11-25T23:5x·声明 8.96% vs 实测 13.64%·2024 一年 21.72% 是声明数的 2.4 倍·70.4% 的窗超线）"
    "｜下个里程碑＝把期货块输入换成滚动读数并按 95% 窗定手数，同时接进链与冒烟腿（需独占窗，≤48h）"
    "| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3"
)


def main():
    with io.open(PATH, encoding="utf-8", newline="") as f:
        body = f.read()
    if "| r2109 |" in body:
        print("already present, no-op")
        return 0
    if not body.endswith("\n"):
        body += "\r\n" if body.endswith("\r") else "\n"
    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(body + LINE + ("\r\n" if "\r\n" in body[-400:] else "\n"))
    print("appended r2109 line")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
