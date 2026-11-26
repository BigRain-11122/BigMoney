# -*- coding: utf-8 -*-
"""r2121 bookkeeping: round report row, state keys, heartbeat fields.

Kept as a file (repo convention for `results/_r<round>bmc_*`) so the exact text of
this round's evidence is reproducible from git rather than from a shell history.
"""
import datetime as dt
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORTS = os.path.join(ROOT, "round_reports-bm-c.md")

REPORT = (
    "| 2026-11-26 08:1x | 2121 | **PRODUCT（产品优先律·watermark=绿 red=false lane=healthy·孤儿面=0·"
    "竞争窗 rc=0 CLEAN 单宿主）**：把 r2117 留下的那条 P0 关掉——这本书对**同一张 ¥1,000,000 单、"
    "同一个 2026-11-25 收盘**印两个词，而没有任何一张面把它们并排：整手面 `TRADABLE_AT_1000000`"
    "（100 份一手、残差 0.0886% NAV）是**手数算术**，供给闸 `CONDITIONAL`（唯一没过 Y4_top2_share）"
    "才是**许可**；读者把前者当后者，就被一张只数过手的面告知「可以买」。新面 "
    "`scripts/etf_book_permission_vs_size.py` 三件事：①**选回执**（在这张单所在那一档读的那张说话="
    "`etf_book_wrapper_year_gate`@2026-11-25；`etf_book_partial_year_caliber`@2026-11-06 保留但驳回——"
    "它回答的是「换口径会不会换词」，三种口径下这本书都读 CONDITIONAL，所以它没有资格把词改回 "
    "ADMIT）；②**量尺寸能不能买回许可**：本金 250,000→4,000,000 五档**现算**（build(capital=…)，"
    "0.1s），两年份额恒 **73.37%**（线 70.00%）、到线距离恒 **-8.82pp**，只有这段距离值多少钱随本金"
    "线性变（**-31,128 → -498,053**），判词 **SIZE_CANNOT_BUY_THE_YEAR_TEST**——份额是比值不是仓位，"
    "所以这张单的问题是**年形状**不是尺寸（要翻面=2025 那一年少 8.82pp/当时 100 万上 -124,513 元）；"
    "③**对照腿**：同一批本金进整手面词会变（250k/500k/1M/2M/4M 全 TRADABLE_AT_*，残差 0.43%→0.035%），"
    "正说明尺寸只对手数摩擦有话语权。**上读者页**：`scripts/ceo_live_usage.py` 新增 "
    "`_etf_permission_face()`+渲染块——CEO 一页纸此前 23 处「票面」讲钱、**零处**讲许可（r1782 族："
    "研究面可读≠读者可读），现在直接印「下得进 ≠ 许不准持有」+五档不变性+回执选举（页 "
    "`docs/live_usage/LIVE-2026-11-26.md` generated 07:4x·判词随出处自印）。接线：链 "
    "`permission_vs_size_write`(run)+`permission_vs_size`(check) 两腿挂 `supply_gate_decision` 之后、"
    "ceo_live_usage 之前；冒烟两腿 `selftest`(14/14 PASS)+`check`(rc0)。**顺带修掉的红（全量冒烟 "
    "757/777 PASS·20 FAIL 里本窗处理 9 条）**：`etf_book_k_grid`(面落后账本一根 bar)/"
    "`etf_book_admit_cost_ladder`(引面漂移→重生→verdict 由 NO_ARMS_PRICED 变 "
    "PASS_IS_A_COST_ASSUMPTION)/`etf_book_concentration_levers`/`etf_book_rebal_adoption`/"
    "`year_concentration_money`×2(与 YEAR-GATE 差一代 + 自检 29/30)/`etf_book_year_gate_vote`"
    "(14 字段漂移)/`etf_book_premium_swap`(as_of 11-24≠票面 11-25)/`中文页英文散文普查`(4 行是**他面**"
    "的数据道缺失自陈原文，按普查自己的 accept 机制入库、hits/inherited 计数照印、未改写)。"
    "**carry 到下一轮（11 条·非本窗引入）**：`etf_book_phase_atlas_arms`(144 腿 9 失败=三臂需重烧)/"
    "`paper book owns the book the card sells`(NAV_IDENTITY_BROKEN rc1)/`the CEO page's sections each "
    "name the bar`(`k_gap` 节落后且**无链腿重跑**)/`fleet: a lane that appended nothing`/"
    "`toll-ladder verdict is recomputable`/票据溢价与 forward 五条「页不印 or 与产出面对不上」/"
    "`the page prices the cost assumption`(no_control)。"
)

STATE_KEYS = {
    "本轮_r2121": (
        "r2121 PRODUCT: this book prints two words about one ¥1,000,000 ticket on one 2026-11-25 "
        "close and no face joined them -- the lot face says TRADABLE_AT_1000000 (100-share lots fit, "
        "residue 0.0886% NAV) and the supply gate says CONDITIONAL (Y4_top2_share). New face "
        "scripts/etf_book_permission_vs_size.py elects the authoritative receipt (the one read on the "
        "close the ticket is priced on; the 2026-11-06 caliber receipt is kept but rejected -- it "
        "answers a different question and reads the same word under A/B/P), and prices the only "
        "question that decides whether re-sizing is a fix: the top-2 share at five capitals recomputed "
        "live (250k..4M, 0.1s). Share is 73.37% at every capital against a 70.00% line, the gap is "
        "-8.82pp at every capital, only the money moves linearly (-31,128 -> -498,053), so the verdict "
        "is SIZE_CANNOT_BUY_THE_YEAR_TEST: the ticket's problem is year shape, not size. The reader "
        "reaches it: ceo_live_usage now carries _etf_permission_face() and prints the block on the CEO "
        "one-pager, which had 23 ticket mentions about money and zero about permission (r1782 family). "
        "Chain legs permission_vs_size_write/check wired after supply_gate_decision; smoke legs "
        "selftest 14/14 and check rc0."
    ),
    "竞争_r2121": (
        "rc=0 CLEAN (results/_repo_write_contention.bm-c.json: fewer than two codely hosts alive; this "
        "host pid=18500 from 07:30:03). Separately, the loop task's S6 chain (pythonw pid 80572, round "
        "2117, started 04:15) was still running when the round opened and finished mid-round; several "
        "of the 20 smoke reds were faces it rewrote while the comparison legs read them."
    ),
    "通过_r2121": (
        "orders 117 files / heartbeat orders_ack 331 / state 273 -> unacked 0 (stale_acks only the "
        "pre-2026-10-26 lane broadcasts, r2066 precedent); fleet group decisions.md raw bytes 250,586B "
        "sha256 79e3083b85c130b8... == own watermark -> zero new decisions, zero action; fleet/inbox "
        "empty; orphan_face_probe py_faces=7 orphans=0 resident_servers=2; attrition + hooks + loop task "
        "self-heal checked this round."
    ),
    "smoke_r2121": (
        "full suite completed detached: 757/777 PASS, 20 FAIL. Nine of the twenty were mended in-window "
        "(4x face-generation drift: k_grid behind the ledger bar, admit_cost_ladder quoted face moved, "
        "concentration_levers DRIFT, rebal_adoption control did not reproduce; plus year_concentration_"
        "money x2, year_gate_vote 14 fields, premium_swap as_of 11-24 vs ticket 11-25, and the Chinese-"
        "page English-prose census whose 4 new lines are other faces' lane self-declarations accepted "
        "into the census allow list with counts still printed). Eleven are carried as next round's P0 "
        "and are named in the round report; none was introduced by this round's code."
    ),
    "记账_r2121": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3",
}


def main():
    # 1) round report row
    with io.open(REPORTS, "a", encoding="utf-8", newline="") as fh:
        fh.write("\n" + REPORT + "\n")

    # 2) state keys (+ round_no)
    with io.open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = 2121
    for k, v in STATE_KEYS.items():
        st[k] = v
    with io.open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)

    # 3) heartbeat
    now = dt.datetime.now().astimezone()
    with io.open(HB, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    hb["ts"] = now.isoformat(timespec="seconds")
    hb["clock_read"] = now.isoformat(timespec="seconds")
    hb["heartbeat_epoch_utc"] = int(now.timestamp())
    hb["current_task"] = ("r2121: permission vs size (lot word != permission word; top-2 share "
                          "invariant across capital; both on the CEO page)")
    hb["verdict"] = "OK"
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    with io.open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    # 4) self-verify the two typed fields the smoke leg checks
    with io.open(HB, encoding="utf-8") as fh:
        chk = json.load(fh)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in chk["clock_read"] and chk["clock_read"][10] == "T", "clock_read must use T"
    print(json.dumps({"round_no": st["round_no"], "state_keys": len(st),
                      "epoch": chk["heartbeat_epoch_utc"], "clock": chk["clock_read"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
