# -*- coding: utf-8 -*-
# r1085 bm-c closeout: canonical report row + HANDOVER 5x row + state advance + heartbeat faces + inbox sweep.
# Canon: _r1084 closeout lineage. All writes UTF-8 via io (PS GBK hazard law).

import datetime
import io
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-18T09:2x:xx+08:00
EPOCH = int(time.time())

ROW = (
    " | ".join([
        TS, "r1085", "bm-c",
        "watermark verdict=green (red=false / satengine ALIVE rc0 W265 dedup 12/12 complete + W266 prereg frozen / jobs 0 / post_review today 0 X in 200)",
        ("r1085 (clean continuation window, counter at open 1085, advanced 1085->1086 so next=r1086): "
         "(1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 zero-kill (resident ComfyUI 8188 + satengine daemon PID 38392 + resident_dispatcher = legal faces); "
         "process census = sole Bigmoney executor (08:39-08:58 W266-derive dead window confirmed dead, no codely residue; minigame tick 09:06 foreign lane); "
         "S0 rebase over bm-a r1049 (ad940c0ec6+af5d9afe80) with 1 UU conflict results/watermark_red.json resolved live-wins "
         "(mine=09:04-09:06 fresh local probe face vs bm-a 08:47 stale-copy; pre-existing '<<<<<<< HEAD' marker hits in CODELY.md/_r505bmc_merge_resolve.py "
         "verified pre-existing at af5d9afe80, zero introduced) -> W266 PREREG FREEZE 595433d63c + checkpoint 63b7140d2a PUSHED behind=0 ahead=0; "
         "(2) S0.5 pinned-probe dual-delta FALSE both (ord 8f6162d9 content-sha1 / dec 1d4741e4 raw-blob sha256, zero rows owed, unacked=0 -- 101 repo order files all in 226-ack set); "
         "inbox 3 MSGs: 0725 voicegen-pickup=@bm-b zero bm-c debt / 0753 memory-gov-fourpiece=@bm-a zero bm-c debt (its 2 origin-gap findings consistent with own MSG-0831 3rd-gap) / "
         "0831 own outbound swept processed; "
         "(3) S1 smoke 49/49; "
         "(4) P0 PRODUCT = W266 PREREG FREEZE origin 595433d63c: dead-window estate absorbed verbatim per absorb lineage "
         "(frozen-face extract results/_w266bmc_w265_frozen_face.txt byte-identical 22,927B sha256_16 d36c29cf048d299d == blob @ e57215a2c pre-backfill face per r1052/r1049 law "
         "+ needle probe re-run 209 lines rc0 + derive script machine-gated), derive ALL GATES PASS; "
         "SAME-WINDOW HEAL#8 disclosed: count-gate '600_301..602_300' expect 3->4 -- dead-window gate pattern-assumed b_band x2, MEASURED T0 source needle "
         "'598_101..600_100' x4 (line5 x3: 算术续带+A_hop_chain leg1 机证+投影兑现注记 + line31 x1: §3 A档) per r1077 measured-counts-not-assumed law, "
         "all 4 contexts verified legitimate naive-A faces zero stale residue, dbg evidence results/_w266bmc_dbg_derive.py+dbg_t2 committed; "
         "banned_direction_gate ADMIT rc0; out 22,970B/64 lines sha256_16 a273485226cbeefa; bands A 600_501..602_500 FIFTEENTH consecutive A-hop "
         "(naive 600_301..602_300 REFUSED at registered W265 B 600_301..600_500 per W265 prereg sec.5 item5 pre-disclosure fulfilled) / "
         "B 602_501..602_700 SIXTEENTH consecutive above-own-A (own-A reservation cascade); upstream W265 finalize anchors machine-verified "
         "(ledger 1,007,335 EXACT / K=580,920 EXACT / mu -0.09271568 / sigma 0.24504118 / se_mu 0.000321 / W265-only -0.08956582 / A p95 0.3149 / K-lift 0.0000 held-flat); "
         "sec.7/8 placeholders intact; 8 same-window needle heals total disclosed in-script header; "
         "(5) S6 43/43 rc=0 (driver Tools/_r1085bmc_s6.py canon-clone r1084, log results/_r1085bmc_s6_log.txt 09:15:04): "
         "dualrun ZERO-DRIFT streak 43 (461 entries) / compute_audit cpu 73% py 2.1% ok / py_watermark probe fresh / update_daily 0 rows cutoff 10-16 weekend honest "
         "(Monday 10-19 15:30 bars window) / lane no-ops honest per R31 (zt/heat/futures/repo/options-retired/moneyflow/sina_mf/astock/etf/minute_feed/ths/ah/fund_statements) / "
         "fund_premium weekend no-op (bm-c own lane, NAV trading days only) / r701 third-signal veto faces on scorecard+market_clock+papers legs "
         "(host=bm-a origin commit 1-2min fresh + heartbeats stale) honest skip / regime_gate evidence no-op content-hash / daily_report REPORT-2026-10-18 faces=5 / "
         "ceo_live_usage ORANGE cap 50% heat COOL 6 members / token delta=0; "
         "(6) S7: attrition 4 CLEAN (healed notes as-is) + loop pin=5 no-op (first fire 09:25) + watchdog registered (S4U XML flip access-denied = adjudicated "
         "default-principal standing face) + claws x2 installed + idle_trigger --worked rc0 (window has actual work) + HANDOVER 5x row r1085 on-time (window r1084-r1085); "
         "counter 1085->1086")
    ])
)

HB_ROW = (
    "> bm-c round 1085 周报核对（2026-10-18T09:2x 核对·窗口覆盖 r1084-r1085 两枚。5x 印记=r1085 准点无缺。"
    "核对权威面=round_reports-bm-c.md 全文在档+state-bm-c.json closeout/absorb notes。"
    "执行总结（r1084-r1085）=bm-c 席【CEO 记忆治理四件套本机腿+W265 全周期+W266 席位→prereg 冻结全链】："
    "r1084=gate v2 首跑 377,015B/324→97,121B/104+L0 手术 87,547B/95+union REPLACE-DOWN 回灌事故止血（fleet-memory-sync 盘上 no-op 化）"
    "+LEDGER 回执 @group origin cd06053+MSG-0831+W265 周期吸收验证（finalize 1,007,335/K=580,920）+W266 席位 ace19ba85b；"
    "r1085=W266 PREREG FREEZE origin 595433d63c（08:39-08:58 死窗 estate verbatim 吸收：冻结面字节恒等+needle probe 复跑 209 行+derive 全闸 PASS；"
    "heal#8 计数闸 3→4=r1077 实测律执法·dbg 证据入档）+banned ADMIT+S6 43/43+双探针 FALSE hold+S7 四查绿。"
)

DID = (
    "r1085: W266 PREREG FREEZE LANDED origin 595433d63c (bm-c 85th own-wave window, 256th candidate chain): "
    "dead-window estate (08:39-08:58) absorbed verbatim -- frozen W265 face extract byte-identical 22,927B d36c29cf @ e57215a2c pre-backfill + "
    "needle probe re-run 209 lines + derive 38,894B machine-gated; derive ALL GATES PASS out 22,970B/64 lines sha256_16 a273485226cbeefa; "
    "bands A 600_501..602_500 FIFTEENTH consecutive A-hop / B 602_501..602_700 SIXTEENTH consecutive above-own-A per seat receipt ADMIT; "
    "upstream W265 finalize anchors machine-verified (ledger 1,007,335/K=580,920/mu -0.09271568/sigma 0.24504118/se_mu 0.000321); "
    "heal#8 same-window count-gate 3->4 (T0 measured source needle x4, r1077 measured-counts law, dbg committed); banned_direction_gate ADMIT rc0; "
    "smoke 49/49 + S0 rebase over bm-a r1049 (1 UU watermark_red live-wins, behind=0) + S0.5 pinned-probe dual FALSE (ord 8f6162d9/dec 1d4741e4, unacked=0) + "
    "S6 43/43 rc0 (dualrun streak 43 zero-drift, bars cutoff 10-16 weekend honest, fund_premium bm-c lane weekend no-op, token delta=0) + "
    "S7 quad green (attrition 4 CLEAN, loop pin=5 no-op, watchdog adjudicated-S4U face, claws x2, idle --worked rc0, HANDOVER 5x row on-time)"
)

VERDICT = (
    "green: r1085 = clean continuation window (counter 1085 at open per state, executed r1085, advanced 1085->1086 so next=r1086; "
    "zero absorb owed by counter law -- the 08:39-08:58 W266-derive dead window left zero commits and was absorbed product-side THIS window "
    "as estate verbatim per absorb lineage: frozen-face byte-identity + probe re-run + derive re-run all-gates + banned ADMIT before freeze; "
    "zero double-count: S0.5 dual-delta FALSE both scans (ord 8f6162d9 / dec 1d4741e4 pinned-probe, zero rows owed); "
    "product = W266 PREREG FREEZE (P0 first-action law satisfied); engine daemon alive PID 38392 (O-20261018-0137 recovery lineage); "
    "CEO gaming yield standing (loop CPU-only, GPU gen-only); short-video lane DISABLED standing per O-20261017-1741"
)

NEXT = (
    "r1086: (1) W266 SPLICE = FIRST ACTION per W266 prereg 595433d63c: author needle preflight + editor derive canon-clone of the W265 editor "
    "(_w265bmc family, age() machine-needle law) with MEASURED counts not pattern-assumed (r1077 law; heal#8 this window is the fresh family instance -- "
    "the dead-window gate face pattern-assumed b_band x2 vs measured x3); band-order law (consume bands BEFORE producers) + ordinal-order law "
    "(SIXTEENTH->SEVENTEENTH before FIFTEENTH->SIXTEENTH) + kept/dropped split boundary MOVES per prereg sec.3 mandate verbatim in frozen face; "
    "phase-3 needles operate on POST-D-swap text; then freeze_edits run -> five-face splice -> engine mtime-watch self-burn 12/12 -> "
    "sixgate PRE-FINALIZE (29th consecutive target) -> finalize one-pass -> fivekeys 6/6 -> sec.7/8 backfill -> W267 seat publish; "
    "(2) Monday 10-19 15:30 bars window: full papers chain fires (weekend 10-17/18 no bars, debt=0 cutoff 10-16); "
    "(3) short-video lane DISABLED standing per O-20261017-1741; (4) GPU lane = gen-only (CEO gaming yield standing, loop CPU-only); "
    "(5) next 5x = bm-c r1090"
)

SUMMARY = (
    "r1085: clean continuation window: P0 = W266 PREREG FREEZE origin 595433d63c (dead-window estate absorbed verbatim: frozen-face byte-identical @ e57215a2c "
    "pre-backfill face + needle probe re-run + derive ALL GATES PASS; heal#8 count-gate 3->4 per r1077 measured-counts law with dbg evidence committed; "
    "banned ADMIT rc0; out 22,970B sha256_16 a273485226cbeefa; bands A 600_501..602_500 15th A-hop / B 602_501..602_700 16th above-own-A; "
    "W265 finalize anchors machine-verified) + S0 rebase over bm-a r1049 (1 UU watermark live-wins, zero marker introduced) + "
    "S0.5 dual FALSE both scans + unacked=0 + smoke 49/49 + S6 43/43 rc0 (dualrun streak 43, weekend honest, fund_premium no-op, token 0) + "
    "S7 quad green + attrition 4 CLEAN + HANDOVER 5x row r1085 on-time; counter 1085->1086"
)

ARTIFACT = (
    "research/PERPETUAL_N1_W266_PREREG.md (22,970B/64 lines, sha256_16 a273485226cbeefa, origin 595433d63c, frozen 2026-10-18 09:0x) "
    "+ estate evidence results/_w266bmc_{needle_probe.py,needle_counts.txt,w265_frozen_face.txt,prereg_derive.py,dbg_derive.py,dbg_t2.txt}"
)

MILESTONE = (
    "W266 five-face splice -> engine self-burn -> sixgate PRE-FINALIZE -> finalize (r1086-r1087, within 48h); Monday 10-19 15:30 bars papers chain"
)


def main():
    # --- guard: counter expectation ---
    state_path = os.path.join(ROOT, "state-bm-c.json")
    state = json.load(io.open(state_path, encoding="utf-8"))
    assert state["round_no"] == 1085, "counter drift: %r" % state["round_no"]

    # --- 1. canonical round report row (ROOT file, r750 law) ---
    rpt_path = os.path.join(ROOT, "round_reports-bm-c.md")
    rpt_lines = io.open(rpt_path, encoding="utf-8").read().splitlines()
    base = len(rpt_lines)
    with io.open(rpt_path, "a", encoding="utf-8", newline="") as f:
        f.write(ROW + "\n")
    after = len(io.open(rpt_path, encoding="utf-8").read().splitlines())
    assert after == base + 1, "report line assert: %d -> %d" % (base, after)

    # --- 2. HANDOVER 5x row ---
    ho_path = os.path.join(ROOT, "research", "HANDOVER.md")
    with io.open(ho_path, "a", encoding="utf-8", newline="") as f:
        f.write(HB_ROW + "\n")

    # --- 3. state faces ---
    state["round_no"] = 1086
    state["round_no_label"] = "r1085 closeout -> counter 1086"
    state["last_round"] = "r1085"
    state["last_round_at"] = TS
    state["last_round_ts"] = TS
    state["last_round_closed"] = TS
    state["last_round_summary"] = SUMMARY
    state["last_round_summary_at"] = TS
    state["did"] = DID
    state["verdict"] = VERDICT
    state["next"] = NEXT
    state["next_pointer"] = NEXT
    state["current_task"] = "r1085 closeout: W266 PREREG FREEZE landed 595433d63c; next = W266 splice derive r1086 FIRST ACTION"
    state["current_task_at"] = TS
    state["current_task_ts"] = EPOCH
    state["last_action"] = "r1085 closeout (W266 prereg freeze landed + dead-window estate absorbed + S6 43/43 + counter 1085->1086)"
    state["latest_artifact"] = ARTIFACT
    state["last_artifact"] = ARTIFACT
    state["recent_artifact"] = ARTIFACT
    state["next_milestone"] = MILESTONE
    state["now_active"] = TS
    state["ts"] = TS
    state["updated"] = TS
    state["updated_at"] = TS
    state["last_seen"] = TS
    state["last_seen_at"] = TS
    state["last_pulled_at"] = TS
    state["last_orders_read_at"] = TS
    state["last_decisions_read_at"] = TS
    state["last_orders_seen"] = TS
    state["last_decisions_seen"] = TS
    state["heartbeat_epoch_utc"] = EPOCH
    state["clock_read"] = TS
    state["orders_ack_ts"] = TS
    state["orders_ack_receipt"] = (
        "r1085: repo-order unacked=0 (101 files all in 226-ack set, last=O-20261018-0348-bm-a); "
        "group-tree ORD/DEC dual FALSE pinned-probe both scans (ord 8f6162d9 / dec 1d4741e4); "
        "inbox: MSG-0725 @bm-b + MSG-0753 @bm-a zero bm-c debt (left for addressees), MSG-0831 own outbound swept processed"
    )
    state["r1085_closeout_note"] = (
        "r1085: clean continuation window (state round_no=1085 at open, executed r1085, advanced 1085->1086 so next=r1086); "
        "zero absorb owed by counter law -- 08:39-08:58 W266-derive dead window left ZERO commits (estate = 4 untracked files), "
        "absorbed product-side THIS window verbatim per absorb lineage (frozen-face byte-identity + needle probe re-run rc0 + "
        "derive re-run ALL GATES PASS + banned ADMIT before freeze); heal#8 disclosed: count-gate '600_301..602_300' expect 3->4 "
        "(dead-window pattern-assumed b_band x2; MEASURED T0 source needle 598_101..600_100 x4 = line5 x3 + line31 x1; r1077 law; "
        "dbg evidence committed); zero double-count: S0.5 dual-delta FALSE both scans (ord 8f6162d9 / dec 1d4741e4 pinned-probe)"
    )
    state["verify"] = (
        "S6 log 43x rc=0 read-back + d19 pinned-probe dual FALSE at open (ord 8f6162d9 / dec 1d4741e4) + smoke 49/49 + "
        "satengine ALIVE rc0 (daemon PID 38362 00:53 recovery lineage; W265 dedup 12/12) + attrition 4 CLEAN + loop pin=5 no-op + "
        "watchdog registered (S4U flip access-denied adjudicated standing) + claws x2 installed + idle worked rc0 + "
        "epoch int readback + report line +1 asserted + HANDOVER 5x row r1085 on-time + W266 freeze receipt live-verifiable "
        "(origin 595433d63c sha256_16 a273485226cbeefa) + closeout commit rides this window"
    )
    io.open(state_path, "w", encoding="utf-8", newline="").write(
        json.dumps(state, ensure_ascii=False, indent=1) + "\n")

    # --- 4. heartbeat faces ---
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(io.open(hb_path, encoding="utf-8"))
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_ram = round(vm.available / (1024 ** 3), 2)
        cpu_pct = psutil.cpu_percent(interval=0.5)
    except Exception:
        free_ram, cpu_pct = hb.get("free_ram_gb", 0), hb.get("cpu_pct", 0)
    hb["ts"] = TS
    hb["last_seen"] = TS
    hb["clock_read"] = TS
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["did"] = DID
    hb["current_task"] = state["current_task"]
    hb["current_task_at"] = TS
    hb["current_task_ts"] = EPOCH
    hb["verdict"] = "green: " + VERDICT.split("green: ", 1)[1][:600]
    hb["now_active"] = TS
    hb["activity_now"] = TS
    hb["free_ram_gb"] = free_ram
    hb["idle_ram_gb"] = free_ram
    hb["ram_free_gb"] = free_ram
    hb["cpu_pct"] = cpu_pct
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_idle_pct"] = round(100 - cpu_pct, 1)
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["latest_artifact"] = ARTIFACT
    hb["last_artifact"] = ARTIFACT
    hb["recent_artifact"] = ARTIFACT
    hb["next_milestone"] = MILESTONE
    hb["next"] = NEXT
    hb["health"] = "ok"
    hb["orders_ack_ts"] = TS
    hb["last_orders_seen"] = TS
    hb["last_decisions_seen"] = TS
    io.open(hb_path, "w", encoding="utf-8", newline="").write(
        json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

    # --- 5. inbox sweep: own outbound MSG-0831 -> processed ---
    src = os.path.join(ROOT, "fleet", "inbox", "MSG-20261018-0831-bmc-memory-gov-fourpiece.md")
    dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20261018-0831-bmc-memory-gov-fourpiece.md")
    if os.path.exists(src):
        shutil.move(src, dst)
        print("inbox sweep: MSG-0831 -> processed")
    else:
        print("inbox sweep: MSG-0831 already moved")

    # --- 6. readback asserts ---
    s2 = json.load(io.open(state_path, encoding="utf-8"))
    h2 = json.load(io.open(hb_path, encoding="utf-8"))
    assert s2["round_no"] == 1086
    assert isinstance(h2["heartbeat_epoch_utc"], int) and isinstance(s2["heartbeat_epoch_utc"], int)
    assert h2["clock_read"] == s2["clock_read"] == TS and "T" in h2["clock_read"]
    print("closeout OK: round 1085->1086, epoch=%d (int), ts=%s, ram_free=%.2fGB, report %d->%d lines" %
          (EPOCH, TS, free_ram, base, after))


if __name__ == "__main__":
    main()
