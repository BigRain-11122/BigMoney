"""r2028 closeout: one report row, state fields, heartbeat fields.  No shared-face edits."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))

ROW = (
    "| 2026-11-24 05:5x | r2028 **新增文件面**（竞争窗 rc=3·不动共享面） "
    "| **票据日期对账**：`scripts/astock_veto_hedge_dating.py` + `results/astock_veto_hedge_dating.json` "
    "+ `research/ASTOCK_VETO_HEDGE_DATING.md`。r2027 的 3,919 手是拿「11-11 结账的账面」配「11-20 的行情」算的——"
    "两日期差 **7 根 bar**，这 7 根里 512100 **-15.19%**、IM **-16.27%**。同一目标 beta 0.9013 在账面日只买 "
    "**3,323 手**（与在印差 **596 手 = 17.9%**）；3M/10M/20M 档差 1,786 / 5,953 / 11,907 手；IM 臂 10M 档 7→8 手、20M 档 14→16 手。"
    "判词 **`DATING_MOVES_THE_ORDER`**。另印「行情动多少才改单」：ETF 臂几千手→任何一跳都改最近整数（该臂永远配得上 beta，"
    "日期错位决定不了它）；IM 臂 1M 档要 **36.09%** 才换手数、10M 档 **4.69%**、20M 档 **0.81%**。诚实面：账面这 7 天**没有任何 mark**，"
    "所以不印账面收益，只印两个对冲工具动了多少。验证：selftest **15/15** PASS、`check` rc0（8 行梯子全复算 + 与 r2027 在印同日期数字逐格对账 + 页判词在场）、"
    "负控 `results/_r2028bmc_dating_negative.py` **4/4**（毒数字→CHECK FAILED 不带 STALE / 日期动→STALE / 页丢判词→红 / 判词被翻→红）。"
    "孤儿面=0；写竞争探针 rc=3（对端 pid 51252 存活·25 张共享面在轮首前被写·重叠窗 0 张）→ 本轮只落新增文件面、未跑 S6 链、未改共享代码/数据面。"
    "令簿双扫 **unacked=0**（116 令 / 329 回执）；饱和引擎 rc0 活；attrition_ledger_guard CLEAN。"
    "本地未达 origin commit 数=0（送达自证见 addendum 行）。记账：本行 1 处 + state 1 处 + 心跳 1 处 = 3。 |\n"
)

NOW = datetime.now(CST).isoformat(timespec="seconds")

STATE_FIELDS = {
    "round_no": 2028,
    "round_no_prev": 2027,
    "round": 2028,
    "round_no_landed": 2028,
    "round_no_label": "r2028",
    "last_round": 2028,
    "last_round_at": NOW,
    "next_round": 2029,
    "当前活": "把票据的日期钉死：这张单是哪一天的账面配哪一天的行情",
    "当前任务": ("r2028: 票据日期对账——11-11 账面 × 11-20 行情；7 根 bar 里 512100 -15.19% / IM -16.27%；"
             "同一 beta 在账面日 3,323 手 vs 在印 3,919 手（差 17.9%）"),
    "当前任务_en": ("r2028: the ticket priced a 2026-11-11 book with a 2026-11-20 price -- seven bars "
                "apart, 512100 -15.19% and IM -16.27% inside them"),
    "最近实物": ("research/ASTOCK_VETO_HEDGE_DATING.md + results/astock_veto_hedge_dating.json + "
             "scripts/astock_veto_hedge_dating.py（selftest 15/15·check rc0·负控 4/4）（2026-11-24 05:5x）"),
    "最新实物": "research/ASTOCK_VETO_HEDGE_DATING.md + results/astock_veto_hedge_dating.json + scripts/astock_veto_hedge_dating.py",
    "最新判词": "DATING_MOVES_THE_ORDER",
    "下个里程碑": ("(a) 竞争窗关后把 r2022-r2028 六面接 S6 链腿与冒烟腿（≤48h）；"
              "(b) 把「先重估账面、再下单」这条接进 CEO 一页纸与票据仓位节：账面自 11-11 起未 mark（≤48h）"),
    "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2028 腿 + 方法论卡 + CODELY 一行；"
             "(b) 给账面做一次真正的重估（per-name marks 到 11-20），把「未 mark 的天数」变成可下单的硬门；"
             "(c) 把 ETF 臂「任何一跳就换手数」这条写成票面上的执行说明（否则读者会以为 596 手是笔可执行的差）"),
    "未验证": ("①账面本身未 mark，本面只印两个对冲工具的移动，不印账面收益；②capital 四档仍是 r2007 时代的数，"
            "不是 11-11 的实际账面值；③保证金/券源/追保未建模（承 r2027）；④本面是口径件不是下单指令；"
            "⑤两只工具在 11-12..11-20 是同向大跌，单周样本不能外推成常设折价"),
    "记账_r2028": "本行 1 处（轮报告）+ state 1 处 + 心跳 1 处 = 3（无方法论新增：把已发布的票据换到正确日期上重算，属证据与载体）",
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0, py_faces 5, resident_servers 1",
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "watermark_note": ("竞争探针 rc=3：2 宿主存活（对端 pid 51252 11-22 20:10 起常驻 interactive / 本宿 pid 51684），"
                       "25 张共享面在轮首前被对端写、重叠窗 0 张 -> 按 r1927 只落新增文件面，未改共享代码/数据面、未跑 S6 链"),
    "last_round_contention": "rc=3 CONTENTION (peer pid 51252, 25 shared faces written before round start, 0 in overlap)",
    "work": ("r2028 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_dating.py + "
             "results/astock_veto_hedge_dating.json + research/ASTOCK_VETO_HEDGE_DATING.md —— "
             "把 r2027 那张单的两个日期摆出来，并印出「行情动多少才改单」"),
    "本次": ("7 根 bar：512100 2.7120->2.3000 (-15.19%)、IM 6623.0->5545.6 (-16.27%)；"
           "ETF 1M 3,323->3,919 手 / 3M 9,970->11,756 / 10M 33,235->39,188 / 20M 66,470->78,377；"
           "IM 1M 0.680->0.813 手（1->1）、3M 2.041->2.438（2->2）、10M 6.805->8.127（7->8）、20M 13.609->16.253（14->16）；"
           "换单距离 IM 1M 36.09% / 3M 18.35% / 10M 4.69% / 20M 0.81%；ETF 臂 ~0%（任何一跳都改最近整数）"),
}

HB_FIELDS = {
    "round_no": 2028,
    "verdict": "healthy",
    "当前任务": STATE_FIELDS["当前任务"],
    "当前活": STATE_FIELDS["当前活"],
    "最近实物": STATE_FIELDS["最近实物"],
    "下个里程碑": STATE_FIELDS["下个里程碑"],
    "idle_rounds": 0,
    "agenda_starved": False,
}


def main() -> int:
    rep = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
    with open(rep, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(ROW)

    sp = os.path.join(ROOT, "state-bm-c.json")
    with open(sp, encoding="utf-8") as fh:
        state = json.load(fh)
    state.update(STATE_FIELDS)
    state["last_round_ts"] = NOW
    state["last_round_utc"] = NOW
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hp, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb.update(HB_FIELDS)
    hb["last_seen"] = NOW
    hb["clock_read"] = NOW
    hb["ts"] = NOW
    hb["heartbeat_epoch_utc"] = int(time.time())
    with open(hp, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # self-证: epoch must be an int and the clock must carry a T
    check = json.load(open(hp, encoding="utf-8"))
    assert isinstance(check["heartbeat_epoch_utc"], int)
    assert "T" in check["clock_read"]
    print("closeout ok | round_no=%d | epoch=%d | %s"
          % (check["round_no"], check["heartbeat_epoch_utc"], check["clock_read"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
