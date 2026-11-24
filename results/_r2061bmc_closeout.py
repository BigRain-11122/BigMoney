# -*- coding: utf-8 -*-
"""r2061 closeout: bump the per-machine round, refresh the heartbeat, append the
round-report line -- all through json.load/dump so the key set survives.

Why a script and not three edits: state-bm-c.json carries ~1.5k keys and
fleet/machines/bm-c.json ~580; a hand edit that drops one key is invisible until
some leg reads it (r2059 lost/duplicated keys twice on this exact face).
"""
import io
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
TZ = timezone(timedelta(hours=8))

now = datetime.now(TZ)
clock_read = now.isoformat(timespec="seconds")
epoch = int(time.time())

REPORT_LINE = (
    f"{clock_read} | r2061 | bm-c | watermark 绿（red=false·reason 空）；孤儿面=0"
    "（py_faces=6 / orphans=0 / resident_servers=1）；**S0 竞争探针 rc=3 CONTENTION**"
    "——2 宿主（interactive pid 79608 自 2026-11-24T22:39 起 137min + 本窗），"
    "轮首前 13 张共享面由别宿主写过（research/INGEST/* 八件、ARBITER-BOARD、"
    "results/arbiter/STATE.json、fleet/machines/bm-c.json），重叠窗内不可归因 0 张"
    "（证据 results/_repo_write_contention.bm-c.json）→ 按 r1907/r1927 本轮只落"
    "**新增文件面**：未改共享面、未重跑 S6 链。 | 本轮产品=**冒烟红项分类器**："
    "新建 scripts/smoke_red_triage.py（selftest 13/13）+ results/smoke_red_triage.json，"
    "把 r2049 起积压的 34 条红腿按『修法顺序』分类：EXCEPTION 2 / SUBCHAIN_FAILED 1 / "
    "CONTRADICTION 13 / STALE_OR_MISSING 3 / UNCLASSIFIED 15。为什么要分类而不是直接修："
    "链的 run_leg 只在文案自称 STALE 时才付钱补写（r1850），而『只重算自己』的 check 永不"
    "说过期（r1935）——两者混在同一个红列表里时，读者会把代差当缺陷手改（r1784 前科）。"
    "分类器把四种形状分开，并把『exit=1 | }』这种无诊断文本单独标 empty_detail，"
    "而不是猜一个类。 | 三类可立即动手的实物证据（逐条原文可取，见 json）："
    "①EXCEPTION=etf_book_permission_persistence（KeyError: 'gap_k'）与 "
    "etf_book_cash_roll_today（today's roll under the decision deadline）——有栈即真缺陷；"
    "②CONTRADICTION 13 条里 4 条同族『receipt 与 rederive 判词相反』"
    "（size_rulers_decision: receipt=IDENTITY_BROKEN vs rederive=SIZE_IS_A_RULER_CHOICE；"
    "decision_line: the receipts do not agree with each other）；"
    "③STALE 3 条=astock_resid_veto_layer / futures TSMOM / etf_book_admit_cost_ladder"
    "（NO_ARMS_PRICED n_arms=0），属链会自愈的那一族，不该手改。 | 未验证（如实）："
    "**全量冒烟本轮仍未跑**（连续第 10 轮）——上面 34 红是 2026-11-24T20:12:28 的上一份"
    "logs/smoke_legs.json（285.9min 旧），本轮的分类只对那份旧读数成立；S6 链连续第 10 轮未跑。"
    " | 下轮指针：(a) 无竞争窗时先 `python Tools/s6_chain_bmc.py <r> --only=<族>` 分批补跑，"
    "再按本分类器 fix_order 逐条修红（先 EXCEPTION 后 CONTRADICTION，STALE 交给链）；"
    "(b) smoke_red_triage 接一条冒烟腿，断言 classify 在已知红样本上给出的类不变（防分类器自身"
    "静默漂移）；(c) main 合入 + 方法论卡（跨机只认内容 / 代差与缺陷必须分开）。 | "
    "**CEO 三行**：当前活=把积压 34 条冒烟红腿分好类，让下一次修红按顺序做而不是凭感觉｜"
    "最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\smoke_red_triage.json"
    f"（{clock_read}·34 红五类·含逐条原文）｜下个里程碑=无竞争窗时 S6 分批补跑 + 按 "
    "fix_order 修红（≤48h）。| 记账：本行 1 处。\n"
)


def main() -> int:
    # --- state ---
    with io.open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    keys_before = len(st)
    prev_round = st.get("round_no")
    st["round_no"] = (prev_round or 0) + 1
    st["记账_r2061"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把『红腿的修法顺序』做成可复核分类属证据与载体；方法论卡锁存待无竞争轮）"
    st["通过_r2061"] = ("竞争探针 rc=3 CONTENTION（2 宿主·13 张共享面别宿主写过·重叠窗不可归因 0）→ 只落新增文件面；"
                        "冒烟/ S6 连续第 10 轮未跑（本轮跑的是 2026-11-24T20:12:28 的旧读数）")
    assert len(st) == keys_before + 2, f"state key drift {keys_before} -> {len(st)}"
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # --- heartbeat ---
    with io.open(HB, "r", encoding="utf-8") as fh:
        hb = json.load(fh)
    hb_keys_before = len(hb)
    hb["last_seen"] = clock_read
    hb["clock_read"] = clock_read
    hb["ts"] = clock_read
    hb["heartbeat_epoch_utc"] = epoch
    hb["round_no"] = st["round_no"]
    hb["当前任务"] = "r2061 CONTENTION 退避轮：冒烟红项分类器（smoke_red_triage）+ 新增件落地"
    hb["verdict"] = "CONTENTION_RETREAT_ONLY_NEW_FILES"
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    with io.open(HB, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    # --- round report ---
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(REPORT_LINE)

    # --- self proof (the three faces must parse back and carry the right types) ---
    with io.open(HB, "r", encoding="utf-8") as fh:
        back = json.load(fh)
    assert isinstance(back["heartbeat_epoch_utc"], int), type(back["heartbeat_epoch_utc"])
    assert "T" in back["clock_read"], back["clock_read"]
    with io.open(STATE, "r", encoding="utf-8") as fh:
        st2 = json.load(fh)
    print(json.dumps({
        "round_no": st2["round_no"],
        "state_keys": [keys_before, len(st2)],
        "hb_keys": [hb_keys_before, len(back)],
        "hb_epoch_is_int": True,
        "clock_read": back["clock_read"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
