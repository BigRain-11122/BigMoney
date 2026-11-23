# -*- coding: utf-8 -*-
"""r2022 bm-c: append this round's row to the machine's own round report.

Appended, never rewritten: the file is a ledger of rounds and an append keeps every
earlier row byte-identical (the r1907 rule -- under a contention window, a file the
peer may also be appending to is only safe to touch at its tail, and this script
refuses if the tail changed under it).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")


ROW = (
    "| 2026-11-24 03:4x | r2022（**竞争探针 rc=3 CONTENTION·只落新增文件面**·"
    "27% 的波动那张票，反票买不买得成） | **watermark：red=false / lane=healthy · 孤儿面=0**"
    "（py_faces=5 / resident_servers=1=ComfyUI 空闲）。**产品（产品优先律）**：r2003 拟合出 B 臂对中证 1000 "
    "beta 0.976 / R² 0.857，并在正文里写死「这条 beta 腿是归因装置，不是谁在那个价位能买到的对冲」；"
    "r2014 补了 27.34% 波动与 -25.92% 回撤。两张面之间那句「真去买反票会怎样」一直没人接——本轮去打那张反票，"
    "并且用**两种真能交易的标的**：512100（中证 1000 ETF，全 77 期，2022-09-05 那段 +176.27% 的份额折算按 35% 单日线压平后"
    "再取收益）与 IM（中证 1000 股指期货主力连续，只在它自己上市窗内 52 期，不修跳空=移仓成本写在成交价里）。"
    "**读数一（beta 是同一个敞口）**：对 512100 样本内 beta **0.901**（R² 0.877）；对 IM 全窗 beta **0.976** / R² **0.853** "
    "——r2003 用**指数水平**也是 0.976 / 0.857，两根尺隔着不同标的落在同一个数上。**读数二（波动真的可以削掉）**："
    "一单位 beta 削掉 **84.9%** 的方差（这个份额等于同一次拟合的 R²，两面并列印出），年化波动 27.34% → 10.76%（按样本内 beta 落地）。"
    "**读数三（扣完成本，全窗夏普几乎翻倍）**：k=0/0.25/0.5/1.0/1.5 全窗夏普 0.492 / 0.540 / 0.606 / **0.685** / 0.299"
    "（每次移仓两侧 8 bp 打在空头名义额上）；最大回撤 -25.92% → -14.17%；年化 10.30% → 7.02%——"
    "**用 3.3pp 年化买 16.8pp 回撤**。**读数四（判词落在样本外）**：beta 只用 2023-12-31 前 43 期拟合，2024 起 34 期上读，"
    "对冲夏普 **0.619 vs 未对冲 0.621**——打平，判 `HEDGE_PAYS_IN_SAMPLE_ONLY`。k=1.5 是过度对冲（年化 3.34%、回撤 -24.05%），"
    "说明最优 k 在 1 附近。**读数五（拿掉判词的运气）**：IM 窗（含 2022H2-2024 下跌段）未对冲 0.501 → 对冲 0.938，"
    "但同一窗后一半（上涨段）用前一半拟合的 beta 1.153 去对冲，夏普从 1.173 掉到 0.395——**对冲买的是保险，不是新的边**。"
    "**读数六（融券成本会不会翻判词）**：0/2/5 %/年 三档全窗夏普 0.685 / 0.518 / 0.266，样本外 0.619 / 0.487 / 0.290"
    "——2% 还能守住全窗优势，5% 就守不住。**读数七（买得到吗）**：ETF 一手 230 元，100 万要 3918.83 手（可做，但**要借券**）；"
    "IM 一手 1,109,120 元，100 万连一手都不够（0.81 手），要到 1,230,535 元才谈得上按 beta 配——"
    "对照 r2017 的 IH 面（一手 81.6 万、100 万时 10.9 倍），**换小盘指数以后可执行性本身成了答案的一半**。"
    "｜**验证证据**：`--selftest` **33/33 PASS**（无噪直线恢复斜率与 R²=1 / 完美拟合下一单位 beta 不留方差 / "
    "方差份额与同一次拟合 R² 逐位相等 / k=0 逐位等于原书且零成本 / 移仓成本只打在空头名义额 / 正融券成本逐期压低且与 k 成比例 / "
    "过度对冲 k=1.5 波动回升 / 零 beta 对冲削不掉任何东西 / 缺价的期不按 0 计 / 平坦与单点序列无夏普 / 回撤恒非正 / "
    "年化用 12.6 期口径 / 期间末按下一调仓日与日历 +20 两根独立路径 / 未定价末日不造 0 收益 / 整手与一手名义额算术 / "
    "IM 一手超过 100 万 beta 中性需求 / IS 边界含当日 / 份额折算压平后才取收益 / 判词三态严格且赚钱为负不算 OUT_OF_SAMPLE / "
    "水下时间与复利曲线）；`run` rc0（77 期，evidence_cutoff **2026-11-20**）→ `results/astock_veto_hedgeable_beta.json` + "
    "`research/ASTOCK_VETO_HEDGEABLE_BETA.md`；`check` **rc0**（逐期重推对冲腿与账面、重拟合 beta、重算五臂与样本外、"
    "方差份额与 R² 对账、判词按自家规则重判、k=0 锚 r2014 逐位 **0.000e+00**、IM 窗期数不变）；**负控 "
    "`results/_r2022bmc_hedge_negative.py` 22/22 PASS**（原样 rc0 / 改截止日 STALE / 改一期对冲收益 CHECK FAILED / "
    "改一期账面收益 CHECK FAILED / 改样本内 beta CHECK FAILED / 改某臂样本外夏普 CHECK FAILED / 手改判词 CHECK FAILED / "
    "改方差份额 CHECK FAILED / 截断行集 CHECK FAILED 而不崩 / 删面 face missing / 改对冲腿最后一根 bar STALE / "
    "每次还原后逐字节相同且仍绿）。｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=5 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主存活：pid 51252 为 11-22 20:10 起的 interactive、本宿 73596；"
    "16 张共享面在本轮开始前被对端写，含 `fleet/machines/bm-c.json`、`fleet/round_reports-bm-c.md`、"
    "`research/ARBITER-BOARD.md`、`results/_attrition_guard_scan.json`）→ 按 r1927 只落**新增文件面**，"
    "未改共享代码/数据面、未跑 S6 链；fetch 后 0 ahead / 0 behind。｜**S0.5 双扫**：`Tools/orders_ack_scan.py` "
    "**CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；集团 `git cat-file blob origin/main:docs/decisions.md` "
    "**原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 → 零新决策零动作；fleet/inbox 空。"
    "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` / `logs/smoke_legs.json` 是共享面，竞争窗不覆盖）；"
    "本轮以 33/33 selftest + 22/22 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（`Tools/s6_chain_bmc.py` "
    "与链产物为对端写的共享面）。｜**S7**：`state round_no 2020→2022`（rounds_done 1957→1958；**2021 归对端在飞轮**，"
    "本窗不动它的号，`round_no_note` 留痕）；心跳经 `Tools/heartbeat_write.py apply` 合并写；"
    "`& Tools/register_loop_task.ps1` 幂等自愈；`attrition_ledger_guard scan` 照跑；`pre-commit`/`pre-push` 与 "
    "`Tools/git-hooks/` 逐字节（CR 归一）比对。｜**CEO 过程可见面**：当前活＝给这本 A 股书打一张「反票」："
    "27% 的波动里有 85% 可以卖空掉，卖空之后全窗夏普 0.49→0.69、回撤 -25.9%→-14.2%，但样本外打平——"
    "对冲买的是保险不是新边｜最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGEABLE_BETA.md`"
    "（2026-11-24 03:4x·beta 0.901/0.976 双侧互证、方差可削 84.9%、五档 k 曲线、样本内外分读、融券 0/2/5% 表、"
    "ETF 与 IM 的可执行性）＋`results\\astock_veto_hedgeable_beta.json`＋`scripts\\astock_veto_hedgeable_beta.py`"
    "（selftest 33/33）＋`results\\_r2022bmc_hedge_negative.py`（负控 22/22）｜下个里程碑＝（a）竞争窗结束后把本面接 "
    "S6 链腿 + 冒烟两腿（≤48h）；（b）**把「保险」定价成可选的句子**：给定这本书，多大回撤预算值得付多少融券成本"
    "（即把 k 从「机械的 1」变成「按预算选的」），并给出月界复核判据（≤48h）。｜**未验证（如实）**：①回撤是 20 根 bar "
    "期间曲线，不是日频 mark-to-market；②ETF 腿按 as-traded 价格（不含分红），卖空实付分红/借券的方向已写在文里但未并入头条；"
    "③IM 主力连续未做移仓调整，换月跳空混在价格里；④只有 77 期、2020 年 7 期；⑤票池现存标的（幸存者偏差，父面同）；"
    "⑥对冲腿的保证金占用与强平风险未建模。｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：本面把一个已发布的归因数字变成一张可执行的价格表，"
    "属证据与载体）。 |\n"
)


def main() -> int:
    with io.open(REPORT, "rb") as fh:
        before = fh.read()
    sha_before = hashlib.sha256(before).hexdigest()
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if "r2022" in text[-4000:]:
        print("row already present -- refusing to append twice")
        return 0
    sep = "" if text.endswith("\n") else "\n"
    new = text + sep + ROW
    with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    with io.open(REPORT, "rb") as fh:
        after = fh.read()
    if not after.startswith(before):
        print("append disturbed earlier bytes -- restore from git")
        return 2
    print("appended (%d -> %d bytes, prefix preserved from %s)"
          % (len(before), len(after), sha_before[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
