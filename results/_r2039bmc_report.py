"""r2039 round-report row: append one line to the machine's own report face.

Two guards this file exists for (r2036/r2039 pitfall):
  * a file with no trailing newline glues the new row onto the last one -- the row is
    therefore written with an explicit '\\n' probe before it;
  * '%' formatting and the written text must come from one source -- the row is built
    once, then written, never re-assembled in two steps.

The append is asserted by line count: exactly one line may be added.
"""
from __future__ import annotations

import io
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)

ROW = (
    "| {ts} | r2039 **新增文件面**（竞争窗 rc=3·不动共享面） | "
    "**watermark：red=false / lane=healthy · 孤儿面=0**"
    "（py_faces=4 / resident_servers=1=ComfyUI 空闲）。竞争探针 "
    "`results/_repo_write_contention.bm-c.json` **rc=3 CONTENTION**"
    "（2 宿主：本宿 pid 78424；对端 interactive pid 51252 自 11-22 20:10 常驻 36.6h、"
    "20 张共享面在轮首前被写、重叠窗 0 张）→ 按 r1907 同树多宿主律只落新增文件面、"
    "未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。"
    "**产品（产品优先律）**：r2038 把等待开成一张价签，却在边界里写「部分对冲的读者付得更少」"
    "——没算。本面把这句话做成阶梯表，用的不是新数据，是 band 面自己印的五条残差行。"
    "**读数一（五条行是一个二次型）**：`R(k)^2 = Var(book) - 2k*Cov + k^2*Var(hedge)` 三个参数、"
    "五个点 → 多出的两行就是检查：逐点最大误差 **5.96e-14**，反解出的账本波动 **27.3433%** 与 "
    "band 面印的逐位相同，反解出的残差最小点 **0.970652** 与 band 面的全窗 beta 差 **1.29e-12**。"
    "**读数二（阶梯，每百万镜头，参考臂 k=0.9013=3,919 手）**："
    "k=0 **16.580pp/年**（165,803 元，倍率 1366.5——与 r2038 的 16.5803/1366.55 逐位对齐，check 硬腿差>0.02pp 就红）；"
    "k=0.25 10.746 / k=0.5 5.421 / **k=0.65 2.724pp（27,242 元/年，倍率 224.5）** / k=0.75 1.296 / "
    "k=0.85 0.301 / k=0.9 0.006 / k=0.95 -0.138 / **k=1.0 -0.124** / k=1.0263 -0.054。"
    "**读数三（打平带）**：k ∈ **[0.8986, 1.0427]**（3,907..4,534 手）——在这个带内等待每年多扛的波动"
    "不到它买到的东西；低边界 = 部署量的 **99.7%**。也就是说：**等带宽减半的前提是对冲几乎已经全部上完**，"
    "「留着大部分等待」在物理上就是把账本裸着（→ `YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE`）。"
    "**读数四（BUDGET 规则 A 落在带外很远）**：k=0.65 每年 2.724pp、倍率 224.5 "
    "→ `PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP`（部分对冲减轻但不改变结论：等待仍是它买到的东西的百倍价）。"
    "**读数五（天花板是一个比例，不是一段等待）**：r2038 把残差 10.763%→10.639% 记作等待的收益，"
    "而 10.639% 正是 **k=1.0** 那一行——今天把比例挪到 1.0 就已经拿到，不用等 10.24 年 "
    "→ `THE_CEILING_IS_A_RATIO_NOT_A_WAIT`。**读数六（点估计是三个 beta 里最差的）**："
    "在残差表自己的窗口上，点估计 10.763% > 单位 beta 10.639% > 样本外 10.709% "
    "→ `THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS`（只陈述现象：点估计是样本内 43 期拟合，"
    "残差行评估在配对全窗 77 期，窗口不同即成因，本面不解释来源）。"
    "｜**验证证据**：`--selftest` **49/49 PASS**；`run` rc0；`check` **rc0**（2 父面 content+file 双 sha + "
    "10 级阶梯逐格重推 + 打平带四点重推 + 二次型三参数重推 + k=0 复现 r2038 硬腿 + 页面四 token 在场 + 内容哈希自洽）；"
    "负控 `results/_r2039bmc_ladder_negative.py` **29/29 PASS**（健康副本必绿；改一格阶梯→CHECK FAILED 且不带 STALE；"
    "改打平边界→CHECK FAILED；二次型失配→点名 identity；页面丢判词→missing token；父面加一字节→STALE 且不带 CHECK FAILED；"
    "第二个父面同样在监；缺面/缺页→STALE 不崩；数字写成字符串→红不 traceback；k=0 不复现→点名 anchor；"
    "跑完五个发布件逐字节未动）。"
    "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` **orphans=0** 零杀；`repo_write_contention` rc=3 → 只落新增文件面。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本 / 3 处历史缩行 healed 照录）；fleet/inbox 0 件。"
    "｜**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` 都是共享面），"
    "本轮以 49/49 selftest + 29/29 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（共享面）。"
    "｜**S7**：state round_no 2038→2039；`heartbeat_write apply --fields` **rc0**（ack 前后均 329 未缩、"
    "`heartbeat_epoch_utc` 为 int、gpu_probe util 9.0% / used 8,977 MiB）；`& Tools/register_loop_task.ps1` "
    "**phase ok**（pin=0 current=0，首燃 09:25 未动）；pre-commit / pre-push 爪与 `Tools/git-hooks/` 源同（MATCH/MATCH）；"
    "`idle_trigger --worked` 清零（idle_rounds 1→0、agenda_starved→false）。"
    "｜**CEO 过程可见面**：当前活＝把「等待」从一张价签拆成一条按对冲比例查的阶梯；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_WAIT_LADDER.md`"
    "（2026-11-24 09:2x·**打平带 k∈[0.8986,1.0427]，k=0.65 仍每年 2.724pp、倍率 224.5**；"
    "**等待追的 0.124pp 天花板今天把比例挪到 1.0 就拿到了**；**点估计是三个 beta 里残差最差的**）"
    "＋`results\\astock_veto_hedge_wait_ladder.json`＋`scripts\\astock_veto_hedge_wait_ladder.py`（selftest 49/49）"
    "＋`results\\_r2039bmc_ladder_negative.py`（负控 29/29）；"
    "下个里程碑＝（a）竞争窗结束后把 r2022–r2039 十七面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）把「等带宽减半 = 对冲几乎要全上完（k≥0.8986）」写进 CEO 一页纸与票据仓位节（≤48h）。"
    "｜**未验证（如实）**：①台阶假设等待期内 k 恒定，边等边加仓会产生换手成本，本面没算；"
    "②k=1.0 在残差表自己的窗口上最好，换窗口重选比例就是又在窗口上挑数，不宣称它「更对」；"
    "③残差行评估窗口=配对全窗 77 期、点估计 beta=样本内 43 期，「点估计最差」只陈述现象不解释来源；"
    "④52/77 期是否代表未来 regime 未证（r2037 沿用）；"
    "⑤打平带宽度由「四倍期数」标准误律决定，若 beta 本身在动，带宽收窄与残差下降不是一回事；"
    "⑥本面只给「等」定价，不选 k、不宣称对冲值得做。"
    "｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（本行）；"
    "无方法论新增：把一个二次型反解当检查面属证据与载体，方法论卡锁存待无竞争轮。 |"
)


def main() -> int:
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        before = fh.read()
    n_before = before.count("\n")
    prefix = "" if before.endswith("\n") else "\n"
    row = ROW.format(ts=NOW.strftime("%Y-%m-%d %H:%M"))
    with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(prefix + row + "\n")
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        after = fh.read()
    added = after.count("\n") - n_before
    print("newline guard used: %s" % bool(prefix))
    print("lines added: %d (expected 1)" % added)
    print("row starts with a pipe: %s" % row.startswith("|"))
    print("literal %%s present: %s" % ("%s" in row))
    return 0 if added == 1 and row.startswith("|") and "%s" not in row else 1


if __name__ == "__main__":
    raise SystemExit(main())
