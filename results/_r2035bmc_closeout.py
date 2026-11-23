"""r2035 closeout: append the round report row, advance the state face, emit heartbeat fields.

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
HB_FIELDS = os.path.join(ROOT, "results", "_r2035bmc_hb_fields.json")

ROUND = 2035
PREV = 2034
NOW = datetime.now(timezone(timedelta(hours=8)))
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

ROW = (
    "| 2026-11-24 07:5x | r2035 **新增文件面**（竞争窗 rc=3·不动共享面） | "
    "**12% 是每手保证金，不是这个头寸消耗的资本**：`scripts/astock_veto_hedge_margin.py` + "
    "`results/astock_veto_hedge_margin.json` + `research/ASTOCK_VETO_HEDGE_MARGIN.md`。"
    "r2033 把「901,331 名义空头按 12% 锁 108,160 元」当资本表印出来，r2027 只给一条粗界"
    "「一个反向波动等于保证金比例就亏光」。两张面都没走过账户。本面把 1,050 个 IM 交易日"
    "（2022-07-22..2026-11-20）当成一条保证金路径走完。"
    "①**读数一（12% 档第 15 个交易日就被追缴）**：账户在 **2022-08-11** 跌破维持保证金，"
    "此后 **322 个交易日** 一直在维持线之下 —— 对冲刚开仓两周就被叫，远早于它要保的那次回撤。"
    "②**读数二（真正要压的现金是 3.7 倍）**：要整段窗口不被追缴，得压 **403,938 元**"
    "（**44.8% 名义 / 40.4% 本书**），是 12% 比例隐含的 108,160 元的 **3.7 倍**。"
    "③**读数三（把利润划走会让要求翻倍）**：按常规资金管理把超额保证金划走，要求升到 **834,029 元**"
    "（**92.5% 名义**，是无划走版的 **2.1 倍**）—— 利润就是缓冲，划走它账户就变薄。"
    "④**读数四（粗界是四年的第一天）**：最坏单日 +10.35%（=12% 档的 0.9 倍，r2027 的粗界就是这一行），"
    "但最坏 **20 日** 反弹 **36.22%**、**60 日** **44.80%**（= 12% 档的 **3.0 / 3.7 倍**）—— "
    "按「一次波动」写的界，定不了「一个季度」的回撤。"
    "⑤**读数五（追缴的价格）**：12% 档在 2022-08-11 平仓只实现 **-42,678 元**，可后面 1,035 个交易日的"
    "对冲本来能赚 **+110,374 元 = 本书的 11.0%** —— 追缴拿走的不是平仓那点亏损，是「之后就没有保险了」。"
    "⑥**读数六（偿付力与流动性是两件事）**：按本书自己的 20 日簿记，多空合并账户 52 期最低 **+5,703 元**、"
    "期末 **+450,291 元**，从没为负 —— 抵押品是存在的，只是不在那个每天被盯市的账户里。"
    "**判词** `THE_MARGIN_RATIO_IS_NOT_THE_CAPITAL+CALL_ARRIVES_BEFORE_THE_INSURANCE_PAYS`"
    "（同时成立 `SWEEPING_PROFITS_DOUBLES_THE_REQUIREMENT`、`THE_CRUDE_BOUND_UNDERSTATES_THE_PATH`）。"
    "**验证**：`--selftest` **32/32** PASS；`check` rc0（IM 面板 sha + 父母面 sha 双验 + 3 档 × 2 资金制度 × "
    "7 字段 + 6 个持有期最坏反弹 + 所需现金 6 格 + 净账户 3 字段 + 判词重推 + 页面词在场）；"
    "负控 `results/_r2035bmc_margin_negative.py` **10/10** PASS（单调上涨面板 → 所需现金 828,504 > 403,938 且早追缴旗在；"
    "单调下跌面板 → 全程零追缴、判词翻成 ACCOUNT_SURVIVES_AS_POSTED；面板加一行 → STALE rc3 不带 CHECK FAILED；"
    "改一个所需现金数 → CHECK FAILED rc1 不带 STALE；页面丢判词 → CHECK FAILED；缺面 → STALE 不崩；"
    "跑完发布四件逐字节未动）。"
    "**S0**：`fleet/machine.json`=bm-c；orphan_face_probe py_faces=6 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主：本宿 pid 73756；对端 interactive pid 51252 常驻 35h、"
    "19 张共享面在轮首前被写、重叠窗 0 张）→ 只落新增文件面、未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。"
    "**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` 原字节 sha256 仍 **79e3083b85c130b8** → 零新决策；"
    "fleet/inbox 0 件。**S1（诚实边界）**：全量 smoke 未跑（`smoke_test.py` 与 `logs/smoke_legs.json` 都是共享面），"
    "本轮以 32/32 selftest + 10/10 负控 + run/check 双 rc0 背书，**不宣称全绿**。**S6**：未跑（共享面）。"
    "**S7**：state round_no 2034→2035（round_no_prev 留痕）；心跳经 `Tools/heartbeat_write.py apply` 合并写；"
    "`& Tools/register_loop_task.ps1` 幂等；`attrition_ledger_guard scan` **CLEAN**（4 账本）。"
    "**CEO 过程可见面**：当前活＝把「保证金比例」这个静态读数换成「保证金路径」，"
    "回答这个对冲到底要压多少钱、什么时候被叫；最近实物＝"
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_MARGIN.md`"
    "（2026-11-24 07:5x·**12% 档第 15 个交易日就追缴、要压 40.4% 本书才不叫、划走利润要压 83% 本书**；"
    "**粗界低估 3 倍；被追缴等于丢掉之后 11% 本书的对冲收益**）"
    "＋`results\\astock_veto_hedge_margin.json`＋`scripts\\astock_veto_hedge_margin.py`（selftest 32/32）"
    "＋`results\\_r2035bmc_margin_negative.py`（负控 10/10）；下个里程碑＝（a）竞争窗结束后把 "
    "r2022–r2035 十三面接 S6 链腿 + 冒烟两腿（≤48h）；（b）用本面的 40.4% 去改写 r2033 的资本表与票据仓位节 —— "
    "现在那张表说「IM 锁 10.8 万」，实际是 40.4 万，这会改变「IM 比 ETF 便宜一个量级」的结论（≤48h）。"
    "**未验证（如实）**：①面板是 IM 主力连续收盘，移仓成本混在标记里未拆 ②settle 列全空，本面是收盘标记而券商按结算价标记 "
    "③保证金比例是券商条款、本仓观测不到，按档印刷不认单值 ④保证金余额不计息、有价证券充抵未建模 "
    "⑤本书只有 20 日簿记，净账户是 20 日声明贴着日频声明放，这个错配本身就是流动性问题 ⑥名义恒定，真实账户被追缴后会降杠杆。"
    "记账：本行 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「比例」还原成「路径」属证据与载体；"
    "方法论卡锁存待无竞争轮）。 |"
)

STATE_PATCH = {
    "round_no": ROUND,
    "round_no_prev": PREV,
    "rounds_done": 1968,
    "machine": "bm-c",
    "who_did": "bm-c",
    "who_did_r": ROUND,
    "status": "product",
    "work": ("r2035 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_margin.py + "
             "results/astock_veto_hedge_margin.json + research/ASTOCK_VETO_HEDGE_MARGIN.md —— "
             "把 1,050 个 IM 交易日走成一条保证金路径：12% 档 2022-08-11（第 15 个交易日）就跌破维持线、"
             "此后 322 个交易日在线下；整段不追缴要压 403,938 元 = 44.8% 名义 / 40.4% 本书（比例隐含值的 3.7 倍）；"
             "划走超额则升到 834,029 元 = 92.5% 名义；最坏 20/60 日反弹 36.22%/44.80% = 粗界的 3.0/3.7 倍；"
             "追缴拿走的不是平仓亏损而是之后 110,374 元 = 11.0% 本书的对冲收益"),
    "当前任务": ("r2035: 保证金路径——12% 是每手最低额不是资本消耗；整段不被追缴要压 40.4% 本书，"
                 "第 15 个交易日就会被叫，粗界低估 3 倍"),
    "当前任务_en": ("r2035: walk the margin account -- a 12% ratio is a per-contract minimum, "
                    "not the capital consumed; surviving the window costs 40.4% of the book, the "
                    "first call arrives on session 15, and the crude bound is 3x optimistic"),
    "当前活": "把「保证金比例」这个静态读数换成「保证金路径」，回答这个对冲要压多少钱、什么时候被叫",
    "最新判词": "THE_MARGIN_RATIO_IS_NOT_THE_CAPITAL+CALL_ARRIVES_BEFORE_THE_INSURANCE_PAYS",
    "最新实物": ("research/ASTOCK_VETO_HEDGE_MARGIN.md + results/astock_veto_hedge_margin.json + "
                 "scripts/astock_veto_hedge_margin.py (selftest 32/32, check rc0, negative 10/10)"),
    "最近实物": ("research/ASTOCK_VETO_HEDGE_MARGIN.md + results/astock_veto_hedge_margin.json + "
                 "scripts/astock_veto_hedge_margin.py（selftest 32/32·check rc0·负控 10/10）"
                 "（2026-11-24 07:5x）"),
    "本次": ("1,050 个 IM 交易日 2022-07-22..2026-11-20（IM 累计 -20.28%）；名义 901,331 元（beta 0.9013 × 1,000,000）；"
             "8/12/15% 档：首次追缴 2022-07-28 / 2022-08-11 / 2022-08-16，线下 346/322/313 个交易日，"
             "最低权益 -259,725/-223,671/-196,632 元，需补 313,805/295,778/286,765 元；"
             "不划走所需现金 385,911/403,938/421,964 元（42.8/44.8/46.8% 名义，38.6/40.4/42.2% 本书），"
             "划走 816,002/834,029/852,055 元（90.5/92.5/94.5% 名义）；"
             "最坏反弹 1/5/10/20/40/60 日 = 10.35/33.67/40.82/36.22/43.52/44.80%（=12% 档的 0.86/2.81/3.40/3.02/3.63/3.73 倍）；"
             "12% 档平仓实现 -42,678 元、尾部 +110,374 元（11.0% 本书）；"
             "净账户 52 期最低 +5,703 元、期末 +450,291 元"),
    "verify_r2035": ("astock_veto_hedge_margin selftest 32/32 PASS | check rc0 "
                     "(IM panel sha256, parents sha256 x2, 3 rungs x 2 regimes x 7 fields, "
                     "6 horizon rallies with dates, required cash 6 cells, net account 3 fields, "
                     "verdicts re-derived, page tokens present) | "
                     "negative _r2035bmc_margin_negative.py 10/10 PASS "
                     "(monotone rising panel -> required cash 828,504 and early flag on; monotone "
                     "falling panel -> zero calls and verdict flips to ACCOUNT_SURVIVES_AS_POSTED; "
                     "appended bar -> STALE rc3 without CHECK FAILED; tampered required-cash number "
                     "-> CHECK FAILED rc1 without STALE; page missing token -> CHECK FAILED; "
                     "missing face -> STALE without crash; four published files byte-identical)"),
    "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2035 腿 + "
                 "knowledge/METHODOLOGY_ASSETS.md 卡（锁存：保证金比例是每手最低额，资本消耗是路径的最深回撤；"
                 "单日粗界定不了持有期回撤）+ CODELY 一行；"
                 "(b) 用本面 40.4% 改写 r2033 资本表与票据仓位节（那张表说 IM 锁 10.8 万，实际 40.4 万，"
                 "「IM 比 ETF 便宜一个量级」这个结论要重算）；"
                 "(c) 保证金与券费合起来才是持有成本，下一面把两边的资金占用并到同一张资本表上"),
    "下个里程碑": ("(a) 竞争窗关后把 r2022–r2035 十三面接 S6 链腿与冒烟两腿（≤48h）；"
                   "(b) 用 40.4% 本书的保证金要求改写 r2033 资本表与票据仓位节（≤48h）"),
    "未验证": ("①面板是 IM 主力连续收盘，移仓成本混在标记里未拆 ②settle 列全空，本面是收盘标记而券商按结算价标记 "
               "③保证金比例是券商条款、本仓观测不到，按档印刷不认单值 ④保证金余额不计息、有价证券充抵未建模 "
               "⑤本书只有 20 日簿记，净账户是 20 日声明贴着日频声明 ⑥名义恒定，真实账户被追缴后会降杠杆"),
    "记账_r2035": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（方法论卡锁存待无竞争轮）",
    "watermark_note": ("竞争探针 rc=3：对端 interactive pid 51252 常驻 35h，19 张共享面在轮首前被写、"
                       "重叠窗 0 张 → 按 r1907 只落新增文件面，未改共享面、未跑 S6"),
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "s0_note": "orphan_face_probe py_faces=6 orphans=0 零杀；repo_write_contention rc=3 CONTENTION",
    "s05_note": ("orders_ack_scan CLEAN（116 令 / 329 回执 / unacked=[]）；decisions.md 原字节 sha256 "
                 "79e3083b85c130b8... == 水位 -> 零新决策；fleet/inbox 空"),
    "s6_chain": "not run (CONTENTION rc=3)",
    "s6_note": "whole chain NOT run: shared faces are written by the resident peer host -> new-file-face only, per r1907",
    "s7_attrition": "attrition_ledger_guard scan CLEAN（4 账本）",
    "s7_loop": "Bigmoney-IterationLoop 经 & Tools/register_loop_task.ps1 幂等核验",
    "smoke": "not run this round (CONTENTION); 以 32/32 selftest + 10/10 负控 + run/check 双 rc0 背书，不宣称全绿",
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 6, resident_servers 1)",
    "本地未达 origin commit 数": 0,
    "本地未达origin": 0,
    "last_seen": NOW_ISO,
    "updated_at": NOW_ISO,
    "ts": NOW_ISO,
    "why_not_bookkeeping": "本轮主产出是一条把「静态比例」还原成「动态路径」的尺（脚本+JSON+md+负控），不是记账",
    "went_well": "把一个所有人都当资本用的比例还原成一条 1,050 个交易日的路径：答案从「锁 10.8 万」变成「要压 40.4 万，第 15 天就被叫」",
}


def main() -> int:
    # 1. round report: fresh read, single write (multi-writer face)
    with open(REPORT, "r", encoding="utf-8", newline="") as fh:
        body = fh.read()
    if "r2035" in body:
        print("round report already carries r2035 -- not appending twice")
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
        "空闲RAM": "25.8 GB free / 55.9 GB",
        "vram_free_gb": 12.7,
        "vram_total_gb": 16.0,
        "vcpu": 32,
        "latest_work": "r2035 astock_veto_hedge_margin (selftest 32/32, negative 10/10)",
    }
    with open(HB_FIELDS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("heartbeat fields -> %s" % os.path.relpath(HB_FIELDS, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
