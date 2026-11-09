#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r1481 closeout: append the round-report row, bump state round_no, write the heartbeat.

All three writes are idempotent-by-content: re-running after a crash replaces the row
that this script itself wrote (marked by the TIMESTAMP tag) rather than appending twice.
"""
import io
import json
import os
import socket
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
MACHINE = "bm-c"
CST = timezone(timedelta(hours=8))
TAG = "2026-11-09T22:5x"
ROUND = 1481

ROW = (
    "| {tag} | r1481 (PRODUCT·一张票的迟到价格：均值是真的、单张是硬币；局部与聚合实测严格可加) | "
    "**当前活**：11-11 再平衡 · 决策行已带第三个价（晚一格约 932 CNY），票面 k=0.393073 仍在额度上、"
    "本次不欠裁剪 | **最近实物**：scripts/etf_book_late_sheet_price.py + results/etf_book_late_sheet_price.json + "
    "research/ETF_BOOK_LATE_SHEET_PRICE.md + research/digests/DIGEST-20261109-r1481-late-sheet-price.md + 卡 E491 + "
    "决策行 late_sheet 块（scripts/etf_book_decision_line.py，selftest 12→16/16）+ S6 腿 late_sheet_price + "
    "smoke 三腿（{tag}，selftest 10/10 · --check 10/10） | **下个里程碑**：把迟到价格接进「今天必须做还是可以等」"
    "的判别（票面在带宽外或欠裁剪时两者相加），并在真实额度漂移上开一次火（窗 ≤48h）。 "
    "**本轮产品**：r1480 量的是**政策**——每一张票都晚一个开盘，vt08 让出 1.87pp/年（18,700 CNY）。桌面用不了"
    "这句话：他手上只有一张票，问的是「今天下不了、明天补，这一张值多少」。政策数是 83 个决定之和，在不知道"
    "这个和是不是由 83 个小价格拼成之前，不能转让给单张票（E238 族：成员与聚合是两个对象）。本轮把单事件价格"
    "单独量出来：控制路径在每个决策 bar 把持仓从 old 换成 new，准时成交在下一根 bar 持 new，晚一格则那一根仍持 "
    "old、下一根才换 new，之后两条路径完全相同——**所以一张票的迟到价格恰好是一根 bar 的收益差**，"
    "delta_cny = 决策时点 NAV ×(r_old − r_new)。读数（5 相位 ×83 bar=415 个事件）：vt08 单张中位 **−932 CNY**、"
    "p10..p90 −10,347..+5,907、极端 −55,846/+46,122、均值 **−12.2bps 且 t=−4.61**；**41.2% 的事件晚一点反而更好**；"
    "base 臂中位 −1,450 CNY、均值 −19.1bps、t=−4.32、41.0% 反向。三个新事实：①**局部与聚合严格可加**——415 个"
    "局部对数差求和 vs 实跑聚合臂（etf_book_punctuality.replay(lag=1) 同相位网格）的残差 **5e-15**（vt08）/ "
    "**3e-15**（base），不是巧合是构造（两票之间路径相同，晚一格只替换一根 bar），所以单张价格不是近似、它就是"
    "政策数字的加数；聚合臂复算落回 r1480 原话 −1.87pp/年（5/5 相位为负，−2.30..−0.68）、base −3.68pp；"
    "②**均值可判 ≠ 单张可判**：t=−4.61 说明均值离零很远，但 41% 的票晚一点更好、p10..p90 跨 1.6 万 CNY——"
    "纪律在预算上成立（每张预留约 932 CNY），在单张上不成立（不知道这次是赚还是亏），判决 "
    "MEAN_IS_PRICED_EACH_SHEET_IS_NOT；③**这条价格接上了人读的那张纸**——票面本次不欠裁剪时，决策行原文只剩"
    "「无需裁剪」，读者会读成「什么都不欠」，实际欠的是准时；现在同一条句子里印「晚一格 932 CNY、41% 反向、"
    "t=−4.61，而这张票本来不欠裁剪所以迟到是它唯一的价」，缺面一律 UNKNOWN（绝不 0.00）。落地：selftest **10/10**"
    "（tape 复现引擎、事件落在 20 根网格上、不换书就没有价格、平盘价格恒为 0、真换书有价格、符号约定一致、"
    "一根 bar 的替换严格可加、常量样本没有 t、空样本不是 0、平移相位事件数不变）+ `--check` **10/10**（控制复现、"
    "判决由自身分布重算、bps 与 CNY 同事件数、每相位带残差、聚合臂可由自身 finals 复算）+ 决策行 selftest 12→16"
    "（迟到的价必须从已发布面读、必须带自己的噪声、缺面 UNKNOWN、欠裁剪时说「迟到是唯一的价」而不是 0.00x）+ "
    "S6 腿 late_sheet_price（rc0 1.1s）+ smoke 两腿。 **未跑/未验证**：全量 smoke——本轮 22:27 起跑的那套"
    "（pid 66480 → results/_smoke_r1481.out）跑在**改动前**的树上，收轮时仍在跑；终态面已重新起跑"
    "（results/_smoke_r1481b.out），**不宣称全绿**；上一套 r1480 终判 5 条红项全是别机车道（moneyflow 认证尾巴 / "
    "fund_statements 法定期 / marks 成因表 / etf_panel+minute_feed 双属主）与 bm-a 执笔的 CEO 页现金三档，"
    "本机不能改。watermark verdict: {wm}；idle_trigger 不达档（ram_free {ram}GB）。S0-1 锚定 machine_id=bm-c；"
    "S0 fetch 后 0 ahead / 0 behind；轮首脏树=他窗/链腿再生数据面（含 moneyflow 状态件与心跳），本轮只定向 add "
    "自有件；S0.5 fleet/orders 116 件 vs 心跳 acks 241 = **0 unacked**；decisions 水位 raw-blob SHA-256 "
    "e2891af5… 恒等=零动作；round-zero orphan probe py_faces 9 / **orphans 0**；attrition 4 账本 CLEAN"
    "（3 行历史缩行 healed）。**S7**：本机 Bigmoney 计划任务在 CEO 2026-10-17「清理本机所有自动化任务」令下"
    "维持未注册，本轮不擅自重建（待 CEO 解禁件）。本地未达 origin commit 数=0（提交后自证）。 "
    "| 证据=results/etf_book_late_sheet_price.json + results/etf_book_decision_line.json(late_sheet) + 卡 E491 + "
    "S6 腿 late_sheet_price + smoke 三腿 | 下轮=r1482：把迟到价格接进「今天必须做还是可以等」的成本比较"
    "（票面在带宽外或欠裁剪时，裁剪的代价与迟到的代价相加给出一个可判的动作），并回答「晚 k 格的单事件价格"
    "是否等于 k 次一格替换之和」（用 r1480 的政策曲线做对位，验多窗口替换是否仍可加）。"
)


def read_text(path):
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main():
    now = datetime.now(CST)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

    # --- watermark verdict, read not invented
    wm = "unknown"
    try:
        w = json.loads(read_text(os.path.join(ROOT, "results", "watermark_red.json")))
        wm = "%s (red=%s, lane=%s)" % (
            "insufficient_history" if w.get("red") is False else "red",
            w.get("red"), w.get("lane"))
    except Exception as exc:  # noqa: BLE001
        wm = "unreadable (%s)" % exc

    ram_gb = "?"
    try:
        import ctypes

        class MEMSTAT(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

        st = MEMSTAT()
        st.dwLength = ctypes.sizeof(MEMSTAT)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
        ram_gb = "%.1f" % (st.ullAvailPhys / (1024.0 ** 3))
    except Exception:  # noqa: BLE001
        pass

    # --- 1. round report (replace our own row if it is already there)
    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    body = read_text(rr)
    nl = "\r\n" if "\r\n" in body else "\n"
    line = ROW.format(tag=TAG, wm=wm, ram=ram_gb).replace("\n", " ")
    lines = body.split(nl)
    hits = [i for i, l in enumerate(lines) if l.startswith("| " + TAG + " | r1481 ")]
    if hits:
        lines[hits[0]] = line
        for i in reversed(hits[1:]):
            del lines[i]
    else:
        if lines and lines[-1] == "":
            lines.insert(len(lines) - 1, line)
        else:
            lines.append(line)
    write_text(rr, nl.join(lines))
    print("round report rows for r1481:", len([1 for l in lines if l.startswith("| " + TAG + " | r1481 ")]))

    # --- 2. state round_no bump (next round number)
    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.loads(read_text(sp))
    st["round_no"] = max(int(st.get("round_no") or 0), ROUND) + 1
    st["current"] = ("r1481: one sheet's late price (median -932 CNY, mean -12.2bps t=-4.61, "
                     "41% of sheets better late) and the locals add up to the policy arm to 5e-15")
    st["current_task"] = "r1481 late-sheet price + decision line third price"
    st["current_task_short"] = "late sheet price"
    st["current_task_at"] = stamp
    st["current_task_ts"] = stamp
    st["activity_now"] = "r1481 closed: one sheet's late fill priced and printed on the decision line"
    write_text(sp, json.dumps(st, ensure_ascii=False, indent=1) + "\n")
    print("state round_no ->", st["round_no"])

    # --- 3. heartbeat
    hp = os.path.join(ROOT, "fleet", "machines", MACHINE + ".json")
    hb = json.loads(read_text(hp))
    hb.update({
        "last_seen": stamp,
        "ts": stamp,
        "clock_read": stamp,
        "heartbeat_epoch_utc": int(time.time()),
        "current": "r1481: late-sheet price face + decision-line third price",
        "current_task": "r1481 late-sheet price",
        "did": ("r1481: priced one sheet's late fill (-932 CNY median, -12.2bps t=-4.61, 41% of "
                "sheets better late) and proved the locals add up to the policy arm (5e-15); "
                "wired S6 leg + 2 smoke legs and put the price on the decision line"),
        "did_round": "r1481",
        "verdict": ("PRODUCT: one late open on one sheet is worth -932 CNY (median, 415 events), "
                    "-12.2bps t=-4.61, 41% of sheets are better late; locals add up to the policy "
                    "arm to 5e-15; the decision line now prints it"),
        "idle_rounds": 0,
        "agenda_starved": False,
        "hostname": socket.gethostname(),
    })
    write_text(hp, json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
    chk = json.loads(read_text(hp))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be an int"
    assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO with offset"
    print("heartbeat ok:", chk["heartbeat_epoch_utc"], chk["clock_read"])


if __name__ == "__main__":
    main()