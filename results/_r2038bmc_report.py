"""r2038 round-report line: append one row to fleet/round_reports-bm-c.md.

The report face is machine-owned, so this appends rather than rebuilds (r1052 family).

Usage
    python results/_r2038bmc_report.py
"""
from __future__ import annotations

import io
import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
FACE = os.path.join(ROOT, "results", "astock_veto_hedge_deploy_wait.json")

TZ = timezone(timedelta(hours=8))
STAMP = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
ROUND = 2038


def build_line() -> str:
    face = json.load(io.open(FACE, encoding="utf-8"))
    wait = face["wait"]
    rc = face["risk_ceiling"]
    arms = face["arms"]
    a0, a1, a2 = arms[0], arms[1], arms[2]

    parts = []
    parts.append("| %s | r2038 **新增文件面**（竞争窗 rc=3·不动共享面） | " % STAMP)

    # watermark first line
    parts.append(
        "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=3 / resident_servers=1=ComfyUI 空闲）。"
        "竞争探针 `results/_repo_write_contention.bm-c.json` **rc=3 CONTENTION**"
        "（2 宿主：本宿 pid 67380；对端 interactive pid 51252 自 11-22 20:10 常驻 36.6h、"
        "24 张共享面在轮首前被写、重叠窗 0 张）→ 按 r1907 同树多宿主律只落新增文件面、"
        "未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。")

    parts.append(
        "**产品（产品优先律）**：r2037 把同样 52 期切五刀，证明了「符号稳、幅度在缩」，"
        "但 BAND 面在收口句里留了一个决定：*924 手的带宽可以用更多期数据换，本面不选这个交易*。"
        "本面选它，并且把「等待」从一句修辞变成一张价签——**等待期你在付什么**。"
        "**读数一（等待多长）**：带宽减半 = 标准误减半 = 四倍期数，43 期 → **172 期**，"
        "按 12.6 期/年 = **再等 10.24 年**。"
        "**读数二（等待期每年付多少）**：账本自带 **27.343%%** 波动，对冲后 **10.763%%**——"
        "等待期这笔头寸不在，账本裸着，每年多扛 **16.580pp**（每百万 **165,803 元/年**）。"
        "**读数三（等到的天花板）**：完美 beta 的残差是 **10.639%%**，"
        "从 10.763%% 降下来只有 **0.124pp**（**1,242 元**）——等待买到的是波动，不是收益。"
        "**读数四（倍率）**：总价 **169.75pp**（**1,697,504 元**）÷ 天花板 **0.124pp** = "
        "**1366.55 倍** → `WAITING_IS_THE_EXPENSIVE_INSURANCE`。"
        "**读数五（反过来：部署错了要付多少）**：band 面自己印了样本外 beta **1.0263**，"
        "与点估计 **0.9013** 差 **0.1249**（**13.86%%**）——用点估计部署而真值是它，"
        "残差只多 **0.0538pp**（**538 元/年**），是等一年 **16.580pp** 的 **1/308** → "
        "`THE_BETA_ERROR_IS_CHEAPER_THAN_THE_WAIT_IT_AVOIDS`。"
        "**读数六（三臂并排）**：deploy_now beta=%.4f → %s 手、残差 %.3f%%、95%% 带 %s..%s 手；"
        "wait_for_half_band 目标 %s 手（半宽）、%.2f 年、年付 %.3fpp、总付 %.1fpp、天花板 %.3fpp、倍率 %.1f；"
        "deploy_and_be_wrong 残差 %.3f%%（vs 真值 %.3f%%）、风险上界 %.3fpp。"
        "**判词** `%s+%s`。"
        % (a0["beta"], "{:,.0f}".format(a0["lots"]), a0["residual_vol_pct"],
           "{:,.0f}".format(a0["band_lots"][0]), "{:,.0f}".format(a0["band_lots"][1]),
           "{:,.0f}".format(a1["target_band_lots"]), a1["years"], a1["yearly_cost_pp"],
           a1["total_cost_pp"], a1["benefit_ceiling_pp"], a1["ratio_cost_over_benefit"],
           a2["residual_vol_at_used_pct"], a2["residual_vol_at_true_pct"],
           rc["risk_ceiling_pp"], face["verdict"], face["risk_ceiling_verdict"]))

    parts.append(
        "｜**验证证据**：`--selftest` **28/28 PASS**；`run` rc0；`check` **rc0**"
        "（三父面 content+file 双 sha + 全字段逐值重推 + 页面双 token 在场 + 内容哈希自洽）；"
        "负控 `results/_r2038bmc_deploy_wait_negative.py` **12/12 PASS**"
        "（手改 yearly_cost→CHECK FAILED 且不带 STALE；页面丢 verdict→CHECK FAILED；"
        "页面丢 risk_ceiling token→CHECK FAILED；父面加一字节→STALE 且不带 CHECK FAILED；"
        "缺面/缺页→STALE 不崩；改 ratio→CHECK FAILED；把 risk_ceiling_pp 写成字符串→CHECK FAILED 不 traceback；"
        "跑完五个发布件逐字节未动）。")

    parts.append(
        "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` **orphans=0** 零杀；"
        "`repo_write_contention` rc=3 → 只落新增文件面。")

    parts.append(
        "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
        "集团 `git -C K:\\Fluxgroup\\FluxGroup cat-file blob origin/main:docs/decisions.md` 原字节 sha256 "
        "仍 **79e3083b85c130b8** → 零新决策；`attrition_ledger_guard scan` **CLEAN**"
        "（4 账本 / 3 处历史缩行 healed 照录）；fleet/inbox 0 件。")

    parts.append(
        "｜**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` 都是共享面），"
        "本轮以 28/28 selftest + 12/12 负控 + run/check 双 rc0 背书，**不宣称全绿**。")

    parts.append("｜**S6**：未跑（共享面）。")

    parts.append(
        "｜**S7**：state round_no 2037→2038；`heartbeat_write apply --fields` **rc0**"
        "（ack 前后均 329 未缩、`heartbeat_epoch_utc` 为 int、gpu_probe util 2.0%% / used 1,716 MiB）。")

    parts.append(
        "｜**CEO 过程可见面**：当前活＝在 sizing 块上给「现在部署 vs 等带宽变窄」开一张价签，"
        "把等待从一句修辞变成每年付多少钱；"
        "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_DEPLOY_WAIT.md`"
        "（2026-11-24 08:5x·**等待 10.24 年、每年付 16.580pp（16.6 万元/百万）、"
        "天花板只有 0.124pp（1,242 元）→ 1367 倍；部署错了只多 0.054pp（538 元）→ 1/308**）"
        "＋`results\\astock_veto_hedge_deploy_wait.json`＋`scripts\\astock_veto_hedge_deploy_wait.py`"
        "（selftest 28/28）＋`results\\_r2038bmc_deploy_wait_negative.py`（负控 12/12）；"
        "下个里程碑＝（a）竞争窗结束后把 r2022–r2038 十六面接 S6 链腿 + 冒烟两腿（≤48h）；"
        "（b）把「等待 1367 倍 / 部署错 1/308」写进 CEO 一页纸仓位节（≤48h）。")

    parts.append(
        "｜**未验证（如实）**：①「等待 = 完全不对冲」是本面的定价前提，"
        "跑部分对冲（如 BUDGET 面规则 A 的 k=0.65）的读者付得更少；"
        "②10.24 年假设 beta 标准误按 1/√n 收窄，而 band 面的滚动拟合范围 0.885..1.280 说明 beta 本身在动，"
        "带宽收窄不一定带来更准的 beta；"
        "③52 期是否代表未来 regime 未证（r2037 已明说符号稳不等于样本公平），本面沿用；"
        "④16.580pp 是波动差不是收益差——本面没有给波动定价（那是 BUDGET 面的活）；"
        "⑤只切 k=1、全额抵押、最便宜租金这一个参考格；"
        "⑥「每年付 16.580pp」按常数波动算，若等待期正好是低波 regime 实际等待费更低；"
        "⑦本面不宣称这个对冲值得做，只宣称「等」比「做」贵。")

    parts.append(
        "｜**本地未达 origin commit 数**＝推送后复核。"
        "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
        "（无方法论新增：等待的价格是「未对冲暴露 − 已对冲残差」这个减法，属证据与载体；"
        "方法论卡锁存待无竞争轮）。 |")

    return "".join(parts)


def main() -> int:
    line = build_line()
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    print("appended r2038 line (%d chars) -> %s"
          % (len(line), os.path.relpath(REPORT, ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
