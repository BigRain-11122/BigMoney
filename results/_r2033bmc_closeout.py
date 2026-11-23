"""r2033 closeout: append the round report row, advance the state face, emit heartbeat fields.

Multi-writer faces (the round report, the state) are read fresh inside one process and written
once, per r2026 -- replace-style edits would silently drop a concurrent row.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
HB_FIELDS = os.path.join(ROOT, "results", "_r2033bmc_hb_fields.json")

ROUND = 2033
PREV = 2031
NOW = datetime.now(timezone(timedelta(hours=8)))
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

ROW = (
    "| 2026-11-24 07:1x | r2033 **新增文件面**（竞争窗 rc=3·不动共享面） | "
    "**两条对冲腿放在同一把尺上**：`scripts/astock_veto_hedge_carrier.py` + "
    "`results/astock_veto_hedge_carrier.json` + `research/ASTOCK_VETO_HEDGE_CARRIER.md`。"
    "r2022–r2031 十面每次只引一条腿，而 IM 贴水被当成「每年 8.9% 的对冲成本」在页面上流传。"
    "本面把它钉死：**同一 52 期、同一本书、同一 k**。"
    "①**读数一（同窗同 k=1）**：ETF 空头年化 **12.39%**、IM 空头 **12.31%**，差 **0.354pp/年**"
    "（在 1pp 打平带内）；不对冲同一本书 11.03%。"
    "②**读数二（IM 腿更安静）**：年化波动 **10.94% vs 11.39%**，夏普 1.12 vs 1.09。"
    "③**读数三（两把尺差一个量级）**：基差面把「中位日」年化成 **8.91%/年**（净 carry 5.89%），"
    "而同窗空头对空头的**复利实现差只有 0.354pp/年 = 25 倍小**。"
    "典型日确实向期货空头收费，但期货跌得比指数狠的那几天把它还回来，复利之后几乎不剩。"
    "④**读数四（名义相同、占款不同）**：空 901,331 元名义——IM 按 12% 保证金锁 108,160 元、"
    "剩 891,840 元按 2% 吃息/**+17,837 元/年**；ETF 融券锁 450,666..901,331 元、"
    "还要付借券费 **1.80..7.21pp/年**。**判词** `DISCOUNT_IS_A_MEDIAN_ARTIFACT+IM_WINS_ON_CAPITAL`"
    "（同时成立 `CARRIER_TIES_ON_RETURN_IM_QUIETER`）。"
    "**验证**：`--selftest` **33/33** PASS；`check` rc0（父母面 sha 双验 + 6 臂×7 字段 + 实现差 + "
    "表面读数 + 资本表 15 行逐格 + 判词重推 + 页面词在场）；负控 `results/_r2033bmc_carrier_negative.py` "
    "**19/19** PASS（期货腿毒化两个方向 → 判词分别转 CARRIER_GAP_DISCLOSED / CARRIER_ETF_WINS，"
    "表面读数降到 2pp → ARTIFACT 消失退到 TIE，父面动 → STALE 不带 CHECK FAILED，页面丢词 → "
    "CHECK FAILED 不带 STALE，缺面 → STALE 不崩，跑完发布四件逐字节未动）。"
    "**S0**：`fleet/machine.json`=bm-c；orphan_face_probe py_faces=5 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（对端 interactive pid 51252 常驻 34.8h、"
    "24 张共享面在轮首前被写、重叠窗 0 张）→ 只落新增文件面、未改共享代码/数据面、未跑 S6 链、"
    "未跑全量 smoke。**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / "
    "unacked=[]）；集团 decisions.md 原字节 sha256 仍 79e3083b85c130b8 == 水位 → 零新决策；"
    "fleet/inbox 0 件。**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` "
    "都是共享面），本轮以 33/33 selftest + 19/19 负控 + run/check 双 rc0 背书，**不宣称全绿**。"
    "**S6**：未跑（共享面）。**S7**：state round_no 2031→2033（round_no_prev 留痕 2031；2032 由对端 "
    "yield 轮占用）；心跳经 `Tools/heartbeat_write.py apply` 合并写；`& Tools/register_loop_task.ps1` 幂等；"
    "`attrition_ledger_guard scan` **CLEAN**（4 账本，4 处历史缩行 healed 注记照录）。"
    "**CEO 过程可见面**：当前活＝把「IM 贴水 8.9% 是对冲成本」这个在页面上流传的读数换成实现差；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_CARRIER.md`"
    "（2026-11-24 07:1x·**同窗两腿差 0.354pp/年、表观贴水 8.91% 是 25 倍的伪读数**；"
    "**IM 赢在占款：同样空 90 万名义，IM 锁 10.8 万还能吃息、ETF 要锁 45..90 万还要付 1.8..7.2pp 券费**）"
    "＋`results\\astock_veto_hedge_carrier.json`＋`scripts\\astock_veto_hedge_carrier.py`（selftest 33/33）"
    "＋`results\\_r2033bmc_carrier_negative.py`（负控 19/19）；下个里程碑＝（a）竞争窗结束后把 "
    "r2022–r2033 十一面接 S6 链腿 + 冒烟两腿（≤48h）；（b）把「约 3,900 手 IM + 锁 10.8 万保证金」这条"
    "执行口径接到 CEO 一页纸与票据仓位节，替掉现在只说手数、不说占款的写法（≤48h）。"
    "**未验证（如实）**：①两腿各用自己面板（512100 二级市场收盘 vs IM 主力连续收盘），"
    "ETF 跟踪误差与溢价折价混在差里未拆分；②窗口只有 52 期（IM 面板 2022-07 起），ETF 腿更长的 77 期"
    "记录在本面任何地方都未使用；③保证金/券源参数是扫档不是单值，2% 现金收益是声明假设不是实测；"
    "④券源可得性完全没建模（A 股融券经常借不到，数字治不了）；⑤本面是尺与执行注记，不是交易指令。"
    "记账：本行 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把两条腿放进同一窗口同一占款尺上比，"
    "属证据与载体；方法论卡锁存待无竞争轮）。 |"
)

STATE_PATCH = {
    "round_no": ROUND,
    "round_no_prev": PREV,
    "rounds_done": 1966,
    "machine": "bm-c",
    "who_did": "bm-c",
    "who_did_r": ROUND,
    "status": "product",
    "work": ("r2033 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_carrier.py + "
             "results/astock_veto_hedge_carrier.json + research/ASTOCK_VETO_HEDGE_CARRIER.md —— "
             "两条对冲腿同窗同 k 对决：ETF 12.39% / IM 12.31%，差 0.354pp/年；"
             "IM 波动 10.94% vs 11.39%、夏普 1.12 vs 1.09；表观贴水 8.91%/年 是同窗实现差的 25 倍"
             "（中位日不是一年）；同名义空头 IM 锁 10.8 万保证金吃息 +17,837 元/年，"
             "ETF 锁 45..90 万还要付 1.80..7.21pp 券费"),
    "当前任务": ("r2033: 两条对冲腿同窗对决——ETF 空头 12.39% vs IM 空头 12.31%（差 0.354pp/年，在打平带内），"
                 "IM 更安静（10.94% vs 11.39% 波动、夏普 1.12 vs 1.09）；占款差是决定性的"),
    "当前任务_en": ("r2033: the two carriers on one ruler -- ETF short 12.39% vs IM short 12.31% "
                    "(0.354pp/yr apart, inside the tie band); the futures leg is quieter "
                    "(10.94% vs 11.39% vol, Sharpe 1.12 vs 1.09); the blocked cash decides"),
    "当前活": "把「IM 贴水 8.9% 是对冲成本」这个在页面上流传的读数，换成同窗实现差与占款差",
    "最新判词": "DISCOUNT_IS_A_MEDIAN_ARTIFACT+IM_WINS_ON_CAPITAL",
    "最新实物": ("research/ASTOCK_VETO_HEDGE_CARRIER.md + results/astock_veto_hedge_carrier.json + "
                 "scripts/astock_veto_hedge_carrier.py (selftest 33/33, check rc0, negative 19/19)"),
    "最近实物": ("research/ASTOCK_VETO_HEDGE_CARRIER.md + results/astock_veto_hedge_carrier.json + "
                 "scripts/astock_veto_hedge_carrier.py（selftest 33/33·check rc0·负控 19/19）"
                 "（2026-11-24 07:1x）"),
    "本次": ("52 期（2022-07-26..2026-11-11）：k=0 两腿同为 11.03%/波动 28.44%；k=1 ETF 12.39%/vol 11.39%/SR 1.09，"
             "IM 12.31%/vol 10.94%/SR 1.12；空头累计 ETF -21.03%、IM -22.17%，实现差 -0.354pp/年；"
             "表观基差中位日年化 8.91%（净 5.89%）；资本：名义 901,331，IM 8%/12%/15% 保证金=72,107/108,160/135,200，"
             "剩余现金 927,893/891,840/864,800 按 2% 得息 18,558/17,837/17,296 元/年；"
             "ETF 融券 50/80/100% haircut × 2/5/8% 券费，借券成本 18,027/45,067/72,107 元/年"),
    "verify_r2033": ("astock_veto_hedge_carrier selftest 33/33 PASS | check rc0 "
                     "(parents sha256 x2, 6 arms x 7 fields, realised gap, surface reading, "
                     "capital table 15 rows, verdicts re-derived, page token present) | "
                     "negative _r2033bmc_carrier_negative.py 19/19 PASS "
                     "(two-way poisoned futures leg flips the headline, 2pp surface kills the "
                     "artifact flag, drifted parent -> STALE without CHECK FAILED, page missing "
                     "token -> CHECK FAILED without STALE, missing face -> STALE, four published "
                     "files byte-identical afterwards)"),
    "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2033 腿 + "
                 "knowledge/METHODOLOGY_ASSETS.md 卡（锁存：中位日不是一年；跨载体对比必须同窗同占款）+ CODELY 一行；"
                 "(b) 把 r2033 的占款结论接进 CEO 一页纸与票据仓位节（现在只说手数、不说保证金与券费）；"
                 "(c) ETF 腿更长的 77 期记录里 IM 缺席的那 25 期能不能用 IM 上市前的替代腿补上，先问上证 1000 指数本身有没有"),
    "下个里程碑": ("(a) 竞争窗关后把 r2022–r2033 十一面接 S6 链腿与冒烟两腿（≤48h）；"
                   "(b) 把「约 3,900 手 IM + 锁 10.8 万保证金」的执行口径接进 CEO 一页纸与票据仓位节（≤48h）"),
    "未验证": ("①两腿各用自己面板（512100 二级市场收盘 vs IM 主力连续收盘），ETF 跟踪误差与溢价折价混在差里未拆分 "
               "②窗口只有 52 期，ETF 腿更长的 77 期未使用 ③保证金/券源参数是扫档不是单值，2% 现金收益是声明假设 "
               "④券源可得性未建模 ⑤本面是尺与执行注记，不是交易指令"),
    "记账_r2033": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（方法论卡锁存待无竞争轮）",
    "watermark_note": ("竞争探针 rc=3：对端 interactive pid 51252 常驻 34.8h（state 的 yield_note 已实测其 CPU 0.0%），"
                       "24 张共享面在轮首前被写、重叠窗 0 张 → 按 r1927 只落新增文件面，未改共享面、未跑 S6"),
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "s0_note": "orphan_face_probe py_faces=5 orphans=0 零杀；repo_write_contention rc=3 CONTENTION",
    "s05_note": ("orders_ack_scan CLEAN（116 令 / 329 回执 / unacked=[]）；decisions.md 原字节 sha256 "
                 "79e3083b85c130b8... == 水位 -> 零新决策；fleet/inbox 空"),
    "s6_chain": "not run (CONTENTION rc=3)",
    "s6_note": "whole chain NOT run: shared faces are written by the resident peer host -> new-file-face only, per r1907",
    "s7_attrition": "attrition_ledger_guard scan CLEAN（4 账本，4 处历史缩行 healed）",
    "s7_loop": "Bigmoney-IterationLoop 经 & Tools/register_loop_task.ps1 幂等核验",
    "smoke": "not run this round (CONTENTION); 以 33/33 selftest + 19/19 负控 + run/check 双 rc0 背书，不宣称全绿",
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 5, resident_servers 1)",
    "本地未达 origin commit 数": 0,
    "本地未达origin": 0,
    "last_seen": NOW_ISO,
    "updated_at": NOW_ISO,
    "ts": NOW_ISO,
    "why_not_bookkeeping": "本轮主产出是一条把十个面隐含错误直觉纠正过来的尺（脚本+JSON+md+负控），不是记账",
    "went_well": "把「中位日年化」和「复利实现差」并排印，读者第一次能看见 8.9% 与 0.35pp 差 25 倍（r1313 族第三例）",
}


def main() -> int:
    # 1. round report: fresh read, single write (multi-writer face)
    with open(REPORT, "r", encoding="utf-8", newline="") as fh:
        body = fh.read()
    if "r2033" in body:
        print("round report already carries r2033 -- not appending twice")
    else:
        if not body.endswith("\n"):
            body += "\n"
        body += ROW.rstrip("\n") + "\n"
        with open(REPORT, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        print("round report appended")

    # 2. state face
    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    state.update(STATE_PATCH)
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("state round_no=%s rounds_done=%s" % (state["round_no"], state["rounds_done"]))

    # 3. heartbeat fields for Tools/heartbeat_write.py apply
    fields = {
        "last_seen": NOW_ISO,
        "ts": NOW_ISO,
        "clock_read": NOW_ISO,
        "heartbeat_epoch_utc": EPOCH,
        "round": ROUND,
        "round_no": ROUND,
        "当前任务": STATE_PATCH["当前任务"],
        "当前活": STATE_PATCH["当前活"],
        "最近实物": STATE_PATCH["最近实物"],
        "下个里程碑": STATE_PATCH["下个里程碑"],
        "verdict": "healthy",
        "idle_rounds": 0,
        "agenda_starved": False,
        "空闲RAM": "27.3 GB free / 60.0 GB",
        "vram_free_gb": 12.7,
        "vram_total_gb": 16.0,
        "vcpu": 32,
        "latest_work": "r2033 astock_veto_hedge_carrier (selftest 33/33, negative 19/19)",
    }
    with open(HB_FIELDS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("heartbeat fields -> %s" % os.path.relpath(HB_FIELDS, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
