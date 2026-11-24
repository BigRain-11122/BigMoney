"""Append r2037's row to fleet/round_reports-bm-c.md.

Two pitfalls this writer is built to avoid (both fired in r2036):
  1. appending to a file that does not end in a newline glues the new row onto the previous one
     and `git diff --numstat` reports 1/0, hiding the lost row -- so the tail is checked first;
  2. a `%s` left inside a format string that was never given its argument publishes the literal
     `%s` -- so the row is formatted once and written once.

Usage
    python results/_r2037bmc_report.py
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

TZ = timezone(timedelta(hours=8))
TS = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")

ROW = (
    "| {ts} | r2037 **新增文件面**（竞争窗 rc=3·不动共享面） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=5 / resident_servers=1=ComfyUI 空闲）。"
    "竞争探针 `results/_repo_write_contention.bm-c.json` **rc=3 CONTENTION**（2 宿主：本宿 pid 67272；"
    "对端 interactive pid 51252 自 11-22 20:10 常驻 36.2h、22 张共享面在轮首前被写、重叠窗 0 张）→ "
    "按 r1907 同树多宿主律只落新增文件面、未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。"
    "**产品（产品优先律）**：r2036 把两腿放上付费尺后留下一个符号——`THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT`，"
    "IM 领先 2.87pp。一个符号算在 52 期上就可能是样本造出来的。本面把同样 52 期切五刀。"
    "**读数一（锚）**：全窗 IM **9.39%** / ETF **6.52%**，gap **+2.87pp**，与 r2036 逐位相同（差 0.00e+00）——是分解不是重算。"
    "**读数二（前后半 + 样本内外）**：前半 **3.04pp** / 后半 **2.69pp**；样本内 **4.06pp** / 样本外 **2.27pp**，"
    "四块全为正，翻面不是拟合段的产物。"
    "**读数三（四个季度块）**：**3.24 / 2.86 / 4.91 / 0.61pp**，四块全正——但最新一季（2025-10-16..2026-11-11）只剩 **0.61pp**，"
    "是中位块 3.05pp 的 **1/5**，也是唯一落进 1pp 平手带的块。"
    "**读数四（滚动 26 期，stride 1）**：**27 条窗全部 IM 领先（100%）**，累计 gap 3.32..11.05pp、中位 7.02pp；"
    "年化 min 1.56pp / median 3.13pp / max 4.79pp——全窗那个 2.87pp 是中间情形，不是最好的那条窗。"
    "**读数五（逐期符号检验）**：34 胜 18 负（63.5%），二项双尾 **p=0.0365**，均值 **+0.2218pp/期**——真偏不是硬币。"
    "**读数六（drop-one，52 次）**：最大移动只有 **0.562pp**（丢 2025-06-18 那期），且 **52 次全为正**——不靠单一观测。"
    "**读数七（把 r2036 的 caveat 2 关掉）**：抵押现金从 2% 扫到 0/4/6/8/10%，gap 走 **3.24/2.48/2.10/1.70/1.30pp**，"
    "打平点 **16.34%**，而本书自己的 funded 回报只有 **9.39%**——冻结的卖出款要跑赢整本书才够翻回来，"
    "**翻面不依赖那个观测不到的存款利率**。"
    "**判词** `THE_FLIP_IS_A_PROPERTY_OF_THE_RULE+THE_FLIP_IS_NARROWING+THE_FLIP_DOES_NOT_NEED_A_DEPOSIT_RATE`。"
    "｜**验证证据**：`--selftest` **47/47 PASS**；`run` rc0；`check` **rc0**（三父面 sha + 全字段逐值重推 + 页面 token 在场 + "
    "内容哈希自洽）；负控 `results/_r2037bmc_stability_negative.py` **10/10 PASS**（手改 gap→CHECK FAILED 且不带 STALE；"
    "页面丢判词→CHECK FAILED；父面动→STALE 且不带 CHECK FAILED；缺面/缺页→STALE 不崩；改 rolling 计数→CHECK FAILED；"
    "跑完五个发布件逐字节未动）。｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` **orphans=0** 零杀；"
    "`repo_write_contention` rc=3 → 只落新增文件面。｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本 / 3 处历史缩行 healed 照录）；fleet/inbox 0 件。"
    "｜**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` 都是共享面），"
    "本轮以 47/47 selftest + 10/10 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（共享面）。"
    "｜**S7**：state round_no 2036→2037；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，首燃 08:40 未动）；"
    "pre-commit / pre-push 爪与 `Tools/git-hooks/` 源同（MATCH/MATCH）；"
    "心跳 `heartbeat_write apply` rc0（ack 前后均 329 未缩，`heartbeat_epoch_utc` 为 int）。"
    "｜**CEO 过程可见面**：当前活＝把 r2036 的「排序翻面」当成一个符号去检验，同样的 52 期切五刀看符号还在不在；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_STABILITY.md`"
    "（2026-11-24 08:3x·**27 条滚动窗 100% IM 领先、四季全正、逐期 34/52（p=0.0365）、drop-one 52 次全正**；"
    "**但最新一季只剩 0.61pp（中位 3.05pp）——符号稳、幅度在缩**；"
    "**抵押要到 16.34% 才打平（本书 9.39%），翻面不依赖存款利率**）"
    "＋`results\\astock_veto_hedge_stability.json`＋`scripts\\astock_veto_hedge_stability.py`（selftest 47/47）"
    "＋`results\\_r2037bmc_stability_negative.py`（负控 10/10）；"
    "下个里程碑＝（a）竞争窗结束后把 r2022–r2037 十五面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）用「符号稳、幅度在缩（0.61pp vs 中位 3.05pp）」改写 CEO 一页纸与票据仓位节，"
    "替掉只引全窗 2.87pp 的写法（≤48h）。"
    "｜**未验证（如实）**：①52 期本身是不是公平样本，本面只证「在这 52 期里怎么切都一致」，没证这 52 期代表未来 regime；"
    "②13 期季度块的年化只由 13 个观测放大，符号检验因此用累计口径，年化列只作对照；"
    "③27 条滚动窗彼此重叠 25/26 期，不是 27 次独立试验，不宣称做了多重比较校正；"
    "④打平收益率是在 r2036 的融资恒等式里扫出来的，分档计息或直接冻结的券商是另一条曲线；"
    "⑤只切 k=1、全额抵押、最便宜租金这一个参考格，其他 k 与 haircut 未重切；"
    "⑥窗口起点仍在 IM 面板起点（2022-07），只存在于该日之后的 regime 在所有块里；"
    "⑦符号稳不等于尺寸稳：本面只检验两腿排序，不检验任一回报值不值得投。"
    "｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「翻面」这个符号做成切窗一致性与打平收益率两条可复核读数，"
    "属证据与载体；方法论卡锁存待无竞争轮）。 |"
)


def main() -> int:
    with open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    before = text.count("\n")
    tail_ok = text.endswith("\n")
    row = ROW.format(ts=TS)
    if not tail_ok:
        text += "\n"
    text += row + "\n"
    with open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    after = text.count("\n")
    print("row appended: %s | lines %d -> %d | tail-newline guard %s"
          % (TS, before, after, "applied" if not tail_ok else "not needed"))
    print("numstat should be +%d/-0" % (after - before))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
