"""r862 bm-b books: state.json + heartbeat + round report line + MSG
consume. ASCII console only (r458 law). Idempotent by round_no guard.
"""
import json
import os
import shutil
import sys
import time
import datetime as dt

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state.json")
HEART = os.path.join(REPO, "fleet", "machines", "bm-b.json")
REPORTS = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
IDLE = os.path.join(REPO, "results", "idle_trigger.bm-b.json")
MSG = os.path.join(REPO, "fleet", "inbox",
                   "MSG-20261011-0532-bmb-n2w19-draft.md")
MSG_DONE = os.path.join(REPO, "fleet", "inbox", "processed",
                        "MSG-20261011-0532-bmb-n2w19-draft.md")

NOW_LOCAL = dt.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

DID = ("r862: S0 pre+pre2 absorb own daemon faces (rebase-race closeout) + "
       "pull --rebase onto origin 51b0ad271 (bm-c r852 pool-EOL close + "
       "pre3) + orders diff 0 (67/192/0, S7 rescan 0) + D19 dual "
       "watermark identical (dec caca0c6e/ord f90233c7 zero delta) + "
       "smoke 49/49 + orphan face=0 (round-zero probe 14 py faces) + "
       "boards clear (job 0, asks 0, 183 tickets 0 open) + SAT alive "
       "rc0 + collision probe CLEAR; PRIMARY PRODUCT = N2-W19 slice-1 "
       "DRAFT WINDOW: W18 frozen-gen-stream READ-ONLY replay "
       "decomposition = 8 T-84s3 ledger hits + 6 in-batch dups + 2 h1 "
       "skips -> 48 ok, 48x6=288 byte-reconciled with the W18 refuse "
       "stdout (exact decomposition, null blocks all valid) + census "
       "random arm same 48/64 -> 25% attrition double independent seed "
       "face -> B=6->7 (ceil(300/(62*0.75))), K=64->62 (R3 16->14 "
       "split [3,3,3,3,1,1], R1/R2 exploration core untouched), "
       "envelope 496<=500 + sufficiency line 300 explicit NON-LOWERING "
       "clause (post-refuse downward line adjustment = threshold-gaming "
       "prohibition face; attrition prices the BUDGET never the LINE) + "
       "panel pin-slice spec (census same-instant lockbox post-load "
       "truncation, burnable any day without anchor drift) + skip-only "
       "attrition guard (census law, empirical 4%) + refusal-receipt "
       "decomposition logging hardened into runner spec (W18 sec.8 "
       "lesson) + research/PERPETUAL_N2_W19_PREREG.md DRAFT "
       "(banned_direction_gate ADMIT after BAN-04 word-face reword) + "
       "probe results/_r862bmb_n2w19_draft_probe.py + receipt .json "
       "(band derive readonly candidate X=736000 walked past W18 "
       "family halo, 7 collision slots; closed-family open; grammar "
       "ledger zero alphagen rows; chain head 876731) + F-04 claim "
       "MSG-20261011-0532; S6 41 legs 40 rc0 + alloc rc2 known 510880 "
       "(P5 slot TRANSFER pending); dualrun streak 17; S7 quartet "
       "ALIVE + attrition guard scan CLEAN + idle --worked "
       "(idle_rounds=0) + orders rescan 0; bm-a heartbeat stale 455min "
       "-> bm-b stale-takeover derives on 8 single-writer faces "
       "(O-2100 s2.4 STALE_MIN law) honestly disclosed")

NEXT = ("r863 queue: N2-W19 slice-2 runner (alphagen_beam_w19.py = w18 "
        "clone with explicit param checklist r836 law: BAND_KEYS w19 / "
        "K=62 / R3 split [3,3,3,3,1,1] / B_NULLS=7 / N_TRIALS=496 / "
        "cutoff pin-slice post-load truncation / skip-only guard / "
        "refusal-receipt decomposition on every rc2; selftest hermetic "
        "+ FREEZE-GATE refuse live proof) -> slice-3 freeze window "
        "(band gate live derive + seed_admit_gate rc0 x3 + three-band "
        "registration + FROZEN flip, W15 r492/W18 r861 same-frame) -> "
        "slice-4 burn -> W210 freeze after W209 freeze+finalize lands "
        "(M9 chain, bm-c M10 automation armed on bm-a W208) -> "
        "moneyflow IC panel-ready watch (bm-a lane) -> O-20261011-0012 "
        "CPU-max maintained (pool-EOL watch CLOSED by bm-c r852)")

MILESTONE = ("N2-W19: runner+freeze+burn chain (slice-2 next round, "
             "burn <=10-14 with attrition-priced pooled sufficiency "
             "expectation 325.5>=300, 12% refuse risk instrumented by "
             "refusal receipts); W210 freeze after W209 lands (M9 "
             "chain); chain head 876,731 monotone; moneyflow IC burns "
             "when MF panel completes (bm-a lane)")

VERDICT = ("GREEN: r862 (W19 draft window landed with exact attrition "
           "decomposition replay -- 48x6=288 byte-reconciled, B=7/K=62 "
           "envelope 496<=500, line 300 held non-lowering; smoke 49/49; "
           "S6 41 legs 40 rc0 + alloc rc2 known 510880; dualrun streak "
           "17; watermark red=false board-clear lawful; attrition "
           "CLEAN; quartet ALIVE; orders diff 0; D19 identical; bm-a "
           "stale-takeover derives disclosed)")

ARTIFACT = ("r862: research/PERPETUAL_N2_W19_PREREG.md (DRAFT, "
            "attrition-priced B=7/K=62 design) + "
            "results/_r862bmb_n2w19_draft_probe.py + "
            "results/_r862bmb_n2w19_draft_probe.json (W18 replay "
            "decomposition + band derive readonly) + commits "
            "32b11c4b5/648086626")

REPORT_LINE = (
    NOW_LOCAL + " | r862 bm-b | dept:研究（N2-W19 slice-1 起草窗）+工程"
    "（S6 链·S7 收口）| 实况三行：当前活=N2-W19 起草窗落地（损耗分解重放"
    "定谳+B 重定价+草案件）/最近实物=research/PERPETUAL_N2_W19_PREREG.md "
    "DRAFT+results/_r862bmb_n2w19_draft_probe.json（commit 32b11c4b5·"
    "05:1x-05:2x）/下个里程碑=N2-W19 runner+冻结+烧录链（slice-2 r863·"
    "burn ≤10-14·期望 pooled 325.5≥300）| WM-VERDICT: green（red=false·"
    "py_low_board_clear 合法白名单·compute_audit pool_starvation+supply_"
    "floor 旗=已知供给位：W19 起草面即供给·本窗已交付）| S0: pre+pre2 吸收"
    " own daemon faces→pull --rebase 落 origin 51b0ad271（bm-c r852 "
    "pool-EOL 收口）·orders 差集 0（67/192/0·S7 复扫 0）·D19 双水位恒等"
    "（dec caca0c6e/ord f90233c7）·S1 smoke 49/49·孤儿面=0（14 py "
    "faces）·S2 双板净空（job 0/asks 0/183 tickets 0 open）·SAT 活 rc0·"
    "collision probe CLEAR | 主产出=N2-W19 slice-1：W18 冻结 gen 流只读"
    "重放 64 draws→损耗分解=8 T-84s3+6 批内重复+2 skip→48 ok（48×6=288 "
    "与 W18 拒烧 stdout 逐位对账=分解精确·null 块全有效）+census 随机臂"
    "同 48/64→25% 损耗双独立种子面→B=6→7（ceil(300/(62×0.75))）·K=64→62"
    "（R3 16→14 split [3,3,3,3,1,1]·R1/R2 探索核不动）包结 496≤500+充分"
    "线 300 不降明文条款（拒烧后下调线=跑后禁令违例面·损耗只定价预算永不"
    "定价线）+面板钉死切片（census 同刻锁盒·截断法防漂移）+skip-only 损耗"
    "守卫（census 律·实证 4%）+拒烧路径全分解落盘 runner 硬规格（W18 §8 "
    "欠账不再重演）+banned_direction_gate ADMIT（BAN-04 词面改词复检过）+"
    "带 derive 只读取数 X=736000（撞 W18 族带 halo 步进 7 槽·冻结窗活重导）"
    "+F-04 MSG-20261011-0532 | S6: 41 腿 40 rc0+alloc rc2 已知 510880"
    "（P5 slot TRANSFER 待件）·dualrun streak 17·ORANGE_COOL·REPORT/"
    "LIVE-2026-10-11 再生·thermo/dualarm(BEAR@09-30)/rev_osc no-op/"
    "minute 非工作日 | S7: 四件套 ALIVE（loop pin=2 no-op·watchdog 重注·"
    "pre-commit/pre-push 爪重装幂等）+attrition guard CLEAN（4 台账·历史"
    "缩行 healed 注记照录）+idle --worked（idle_rounds=0）+bm-a 心跳"
    "stale 455min→bm-b 依 O-2100 s2.4 STALE_MIN 律接 8 个单写面 stale-"
    "takeover derive（scorecard/paper/t35/prospect×2/build_status/"
    "daily_scorecard/dashboard）如实披露 | 账：commit 32b11c4b5（起草四"
    "件）+648086626（词面修）·push 送达自证见轮尾 | 下轮指针：r863=W19 "
    "slice-2 runner（r836 克隆律参数清单全显式+selftest hermetic+FREEZE-"
    "GATE 拒烧机证+refusal receipt 腿）")


def main():
    with open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    assert st["round_no"] == 861, f"unexpected round_no {st['round_no']}"
    st["round"] = st["round_no"] = 862
    st["round_no_label"] = "r862"
    st["clock_read"] = st["ts"] = st["updated"] = st["updated_at"] = \
        st["last_round_at"] = st["last_round_ts"] = st["last_seen"] = \
        NOW_LOCAL
    st["did"] = st["last_action"] = DID
    st["now_active"] = ("r862 closeout: N2-W19 slice-1 draft window "
                        "landed (attrition replay decomposition + B=7/"
                        "K=62 repriced design + DRAFT prereg); slice-2 "
                        "runner is r863 work")
    st["current_task"] = st["task"] = st["next"] = NEXT
    st["next_milestone"] = MILESTONE
    st["latest_artifact"] = ARTIFACT
    st["verdict"] = VERDICT
    st["orphan_face"] = st["orphan_faces"] = 0
    st["orphan_face_note"] = ("r862 closeout probe: py_faces=14 alive, "
                              "orphans=0 (round-zero probe 05:0x rc0; "
                              "draft-window replay work only, no "
                              "detached burns this round)")
    st["last_decisions_read_at"] = NOW_LOCAL
    st["last_orders_read_at"] = NOW_LOCAL
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1, ensure_ascii=False)

    with open(HEART, encoding="utf-8") as f:
        h = json.load(f)
    assert h.get("round_no") == 861, f"heart round {h.get('round_no')}"
    try:
        with open(IDLE, encoding="utf-8") as f:
            idl = json.load(f)
        ram_pct = idl.get("ram_free_pct")
        vram_gb = idl.get("vram_free_gb")
    except Exception:
        ram_pct = vram_gb = None
    h["clock_read"] = h["ts"] = h["last_seen"] = h["last_round_at"] = \
        h["updated"] = h["updated_at"] = NOW_LOCAL
    h["heartbeat_epoch_utc"] = EPOCH
    h["round"] = h["round_no"] = 862
    h["did"] = h["last_action"] = DID
    h["now_active"] = st["now_active"]
    h["current_task"] = h["task"] = h["next"] = NEXT
    h["next_milestone"] = MILESTONE
    h["latest_artifact"] = ARTIFACT
    h["verdict"] = VERDICT
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["orphan_face"] = h["orphan_faces"] = 0
    if ram_pct is not None:
        h["ram_free_pct"] = ram_pct
        h["free_ram_gb"] = round(ram_pct * 63.9 / 100.0, 1)
        h["ram_free_gb"] = h["free_ram_gb"]
    if vram_gb is not None:
        h["vram_free_gb"] = vram_gb
        h["gpu_free_vram_gb"] = vram_gb
        h["gpu_free_vram_mb"] = int(vram_gb * 1024)
    with open(HEART, "w", encoding="utf-8", newline="\n") as f:
        json.dump(h, f, indent=1, ensure_ascii=False)
    with open(HEART, encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"

    with open(REPORTS, "a", encoding="utf-8", newline="\n") as f:
        f.write(REPORT_LINE + "\n")

    if os.path.exists(MSG):
        os.makedirs(os.path.dirname(MSG_DONE), exist_ok=True)
        shutil.move(MSG, MSG_DONE)

    print(json.dumps({"books": "r862 written", "round": 862,
                      "epoch_type": type(
                          chk["heartbeat_epoch_utc"]).__name__,
                      "msg": "consumed->processed/"}))


if __name__ == "__main__":
    sys.exit(main())
