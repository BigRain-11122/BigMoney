# -*- coding: utf-8 -*-
# r1083 bm-c closeout: state + heartbeat + round report + HANDOVER 5x row.
# Absorb-continuation window (51st-gen; dead-claimed r1082 label skipped per
# r1015 scratch-namespace precedent; counter 1076->1084 absorbing r1076..r1083
# dead/landed labels). Zero double-count: ORD/DEC dual FALSE post-fetch both
# scans; unacked repo orders acked this window; S6 absorbed not rerun.
import io, json, time, subprocess, datetime

NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
R = "r1083"
NEXT = "r1084"

def ram_gpu():
    free_gb = cpu_pct = None
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb = round(vm.available / (1024 ** 3), 2)
        cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    except Exception:
        pass
    vram = None
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20).stdout.strip().split("\n")[0]
        vram = int(out.strip())
    except Exception:
        pass
    return free_gb, cpu_pct, vram

free_gb, cpu_pct, vram = ram_gpu()

# ---------- state-bm-c.json ----------
sp = "state-bm-c.json"
st = json.load(io.open(sp, encoding="utf-8"))
prev_round = st.get("round_no")
assert prev_round == 1076, f"round_no anchor mismatch: {prev_round}"
st["round_no"] = 1084
st["round_no_label"] = "r1083 closeout -> counter 1084"
st["last_round"] = R
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["last_round_label"] = R
st["clock_read"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["last_seen"] = TS
st["last_seen_at"] = TS
st["now_active"] = TS
st["activity_now"] = TS
st["last_round_closed"] = TS
st["last_pulled_at"] = TS
st["last_action"] = "r1083 closeout (51st-gen absorb continuation: r1082 estate landed f2a4b0255 + W265 splice prep preflight/counts + O-0137 receipt durable on origin + heartbeat healed per O-0137 sec.2.2; counter 1076->1084)"
st["last_round_summary"] = "r1083: 51st-gen absorb (r1082 estate landed+pushed f2a4b0255: O-0137 receipt trio + taskaudit 40-row + S6 43/43 absorbed) + W265 SPLICE PREP (preflight + 167-line counts, core needles all-match, divergent faces machine-disclosed) + smoke 49/49 + satengine ALIVE + dual-FALSE watermarks + unacked-3 acked + 5x HANDOVER row (r1080 stamp discharged)"
st["last_round_summary_at"] = TS
st["current_task"] = "r1083 closeout: W265 splice prep landed; next = W265 splice derive FIRST ACTION r1084"
st["current_task_at"] = TS
st["current_task_ts"] = EPOCH
st["next_milestone"] = "W265 splice derive (r1084 FIRST ACTION, authoring inputs = results/_w265bmc_splice_needle_counts.txt) -> splice -> engine self-burn -> sixgate -> finalize; Monday 10-19 15:30 bars papers chain (24-48h)"
st["latest_artifact"] = "results/_w265bmc_splice_needle_preflight.py + results/_w265bmc_splice_needle_counts.txt (167 lines) + fleet/inbox/MSG-20261018-0431-bmc-taskaudit.md (estate landed f2a4b0255)"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["verdict"] = ("green: r1083 = 51st-gen absorb continuation (recovery window per O-20261018-0137): r1082 dead-window estate "
                 "machine-verified then landed+pushed f2a4b0255 (O-20261018-0137 bm-c receipt trio + taskaudit 40-row MSG/JSON + "
                 "S6 43/43 rc0 log 04:09 absorbed per same-round law; rebase over bm-a db6871dc2/d70897134 with 11 shared same-day "
                 "idempotent faces resolved replay-side live-wins; behind=0) + S0.5 group-tree FETCH + pinned-probe dual FALSE "
                 "(ord 018ba8b2 / dec 1d4741e4 both == current content; bm-a eae5ac55 = its own method face, zero bm-c debt) + "
                 "3 unacked repo orders acked (O-20261017-2207 UU-remote bm-a receipted 22:16 zero action / O-20261018-0137 own "
                 "receipt landed / O-20261018-0348 bm-b-only zero action) + smoke 49/49 + satengine ALIVE rc0 (W264 dedup 12/12 "
                 "complete, W265 prereg frozen e57215a2c = chain head) + P0 PRODUCT = W265 SPLICE PREP (large-task split law "
                 "r971/r1066: preflight + 167-line measured counts; core needles ALL MATCH incl projections 13/13, bands "
                 "5/4/8/9/2/2/4/6, ledger 1,002,935/576,520 x5, MSG/seat-origin/prereg shas, receiptpath 11; DIVERGENT faces "
                 "machine-disclosed: W264 raw 92 (own-wave 81 + paths 11), W263 162, w263_ 93, THIRTEENTH 15, gate05/mirror text "
                 "moved -- canon carries r1077 spotcheck heal edits, derive author MUST use MEASURED counts not pattern-assumed, "
                 "r1066 heal#5 family law) + 5x DUTY HANDOVER row landed (window r1076-r1083, r1080 stamp missed-dead disclosed) "
                 "+ orphan face=0 + CEO gaming yield standing (loop CPU-only)")
st["next"] = (NEXT + ": (1) W265 SPLICE DERIVE = FIRST ACTION (per W265 prereg commit e57215a2c 'five-face splice = next window "
              "FIRST ACTION, E63 age() machine-needle law; kept/dropped split boundary MOVES 242->243): author derive script "
              "from _r1076bmc_derive_freeze.py template with needles from results/_w265bmc_splice_needle_counts.txt (measured, "
              "NOT pattern-assumed); phase-3 needles operate on POST-D-swap text (D-swaps: W264->W265 x81, W263->W264 x162 "
              "measured-raw-derived; r1076 preflight postD/preD law); band order law: consume 598_101->600_301, 598_300->600_500, "
              "596_101->598_301, 598_100->600_300, 596_300->598_500, 597_900->600_100 BEFORE producers 595_901->598_101, "
              "596_100->598_300; ordinal order law: FOURTEENTH->FIFTEENTH before THIRTEENTH->FOURTEENTH; W265 facts: A "
              "598_301..600_300 14th A-hop / B 600_301..600_500 15th above-own-A / W264 finalize 1,005,135 / K 578,720 / seat "
              "origin 7343e3650 / prereg e57215a2c / 255th candidate bm-c 84th own; then freeze_edits run -> five-face splice "
              "-> engine self-burn -> sixgate PRE-FINALIZE -> finalize -> fivekeys -> sec.7/8 -> W266 seat; (2) Monday 10-19 "
              "15:30 bars window: full papers chain fires (10-17/18 weekend no bars, debt=0 cutoff 10-16); (3) short-video lane "
              "DISABLED standing per O-20261017-1741; (4) GPU lane = gen-only (CEO gaming yield standing, loop CPU-only); "
              "(5) next 5x = bm-c r1085")
st["next_pointer"] = st["next"]
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = round(100 - (cpu_pct or 0), 1)
if vram is not None:
    st["gpu_free_vram_mb"] = vram
    st["gpu_free_vram_mib"] = vram
    st["free_vram_mb"] = vram
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["codely_live_count"] = 1
st["loop_round"] = 998
st["orders_ack_receipt"] = ("r1083: 3 unacked repo order files acked THIS window (O-20261017-2207-bm-c UU-remote = bm-a receipted "
                           "22:16 zero bm-c action / O-20261018-0137-bm-a recovery order = own receipt trio landed f2a4b0255 per "
                           "its sec.2 legs / O-20261018-0348-bm-a r998 git-face = bm-b-only leg zero bm-c action); group-tree "
                           "ORD/DEC dual FALSE post-fetch pinned-probe (ord 018ba8b2 / dec 1d4741e4); inbox=0 pending")
st["orders_ack_ts"] = TS
st["last_orders_read_at"] = TS
st["last_orders_seen"] = TS
st["last_decisions_read_at"] = TS
st["last_decisions_seen"] = TS
st["d19_watermark_guard"]["round_ref"] = 1083
st["d19_watermark_guard"]["ts"] = TS
st["r1083_absorb_note"] = ("r1083 absorb note: dead windows r1076/r1077 (W264 full cycle landed 7343e3650 per O-0137 audit) / "
                           "r1078 (taskaudit scratch, landed c3313769b) / r1079 (ord extract) / r1080 (taskaudit JSON 9e8084b54, "
                           "died pre-receipt, 5x stamp MISSED -- discharged by THIS window's HANDOVER row) / r1081 (W265 prereg "
                           "FREEZE e57215a2c + checkpoint 3917a974e, died pre-closeout) / r1082 (self-labeled: taskaudit 40-row + "
                           "O-0137 receipt written to order file + S6 43/43 at 04:09, died PRE-COMMIT, estate absorbed verbatim "
                           "by THIS window and landed f2a4b0255) -- THIS session executed as r1083 (next after highest committed "
                           "label r1081, skipping dead-claimed r1082 per r1015 precedent) and advanced counter 1076->1084 so "
                           "next session = r1084; zero double-count: S0.5 dual-delta FALSE post-fetch both scans, dead-window "
                           "consumption debts handled by their own commits (e57215a2c/3917a974e/9e8084b54) + this estate landing")
st["r1083_closeout_note"] = ("r1083: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 zero-kill; (2) S0 estate "
                             "commit-all + rebase over bm-a db6871dc2/d70897134 (11 conflicts = same-day idempotent shared faces, "
                             "resolved replay-side mine live-wins) + PUSH f2a4b0255 behind=0; (3) S0.5 group fetch + dual FALSE "
                             "(ord 018ba8b2 / dec 1d4741e4) + 3 orders acked; (4) smoke 49/49; (5) satengine ALIVE rc0; (6) P0 "
                             "PRODUCT = W265 splice preflight prep landed; (7) S6 43/43 absorbed (dead-window 04:09:54); (8) 5x "
                             "HANDOVER row r1083; (9) S7 quad + counter 1076->1084")
ack = st.setdefault("orders_ack", [])
for f in ("O-20261017-2207-bm-c.md", "O-20261018-0137-bm-a.md", "O-20261018-0348-bm-a.md"):
    if f not in ack:
        ack.append(f)
st["orders_ack_count"] = len(ack)
st["orders_ack_last"] = "O-20261018-0348-bm-a.md"
io.open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(st, indent=1, ensure_ascii=False) + "\n")
print("state written: round_no", st["round_no"], "ack", st["orders_ack_count"])

# ---------- heartbeat fleet/machines/bm-c.json ----------
hp = "fleet/machines/bm-c.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb.update({k: st[k] for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "now_active",
                              "current_task", "current_task_at", "did", "verdict", "next", "next_pointer", "next_milestone",
                              "latest_artifact", "last_artifact", "recent_artifact", "last_round_summary", "last_action",
                              "prod_lanes", "orders_ack_receipt", "orders_ack_ts") if k in st})
hb["machine_id"] = "bm-c"
hb["round_no"] = 1084
hb["round_no_label"] = "r1083 closeout -> counter 1084"
hb["last_round"] = R
hb["last_round_at"] = TS
hb["last_round_ts"] = TS
hb["last_round_label"] = R
hb["last_round_closed"] = TS
hb["last_pulled_at"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
assert isinstance(hb["heartbeat_epoch_utc"], int)
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
if vram is not None:
    hb["gpu_free_vram_mb"] = vram
    hb["gpu_free_vram_mib"] = vram
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["health"] = "ok"
hb["did"] = st["last_round_summary"]
hb["prod_lanes"] = ("CPU=engine W265 supply chain armed (prereg frozen e57215a2c on origin; splice preflight prep landed; "
                    "splice derive = r1084 FIRST ACTION) ; GPU=gen-only lane (CEO gaming yield window standing: GPU frozen, "
                    "loop CPU-only); short-video lane DISABLED standing per O-20261017-1741")
hback = hb.setdefault("orders_ack", [])
for f in ("O-20261017-2207-bm-c.md", "O-20261018-0137-bm-a.md", "O-20261018-0348-bm-a.md"):
    if f not in hback:
        hback.append(f)
hb["orders_ack_count"] = len(hback)
hb["orders_ack_last"] = "O-20261018-0348-bm-a.md"
io.open(hp, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, indent=1, ensure_ascii=False) + "\n")
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("heartbeat written: epoch int OK, ack", chk["orders_ack_count"])

# ---------- round report row ----------
rp = "round_reports-bm-c.md"
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
row = (TS + " | " + R + " | bm-c | watermark verdict=green (red=false / satengine ALIVE rc0 W264 dedup 12/12 complete / jobs 0 / "
       "tickets 0) | r1083 (51st-gen absorb continuation, recovery window per O-20261018-0137): (1) S0-1 anchor bm-c + round-zero "
       "probe py_faces=4 orphans=0 zero-kill; S0 estate landed+PUSHED origin f2a4b0255 (r1082 dead-window estate: O-20261018-0137 "
       "bm-c receipt trio + taskaudit 40-row MSG/JSON + S6 43/43 rc0 log 04:09 absorbed per same-round law) + rebase over bm-a "
       "db6871dc2/d70897134 (11 shared same-day idempotent face conflicts resolved replay-side live-wins) behind=0; (2) S0.5 "
       "group-tree FETCH + pinned-probe dual FALSE (ord 018ba8b2 / dec 1d4741e4 both == current content, zero rows owed; bm-a "
       "eae5ac55 = its own method face, zero bm-c debt) + 3 unacked repo orders acked (O-20261017-2207 UU-remote bm-a receipted "
       "22:16 / O-20261018-0137 own receipt landed / O-20261018-0348 bm-b-only); (3) S1 smoke 49/49; S3 satengine ALIVE rc0 (W264 "
       "dedup 12/12 complete; W265 prereg frozen e57215a2c = chain head, splice GATED-off prep); (4) P0 PRODUCT = W265 SPLICE PREP "
       "LANDED (large-task split law r971/r1066): results/_w265bmc_splice_needle_preflight.py + counts "
       "results/_w265bmc_splice_needle_counts.txt 167 lines -- core needles ALL MATCH (projections W265p/plain 13/13; bands "
       "598_101x5, 598_300x4, 596_101x8, 598_100x9, 596_300x2, 597_900x2, 595_901x4, 596_100x6; ledger 1,002,935/576,520 x5; "
       "code 1_002_935/576_520; n1/w-token family; MSG-20261017-1950-bmc-w264-seat x7; dd5fd438e x2; f499817fa x1; f4ffdb34e x1; "
       "receiptpath _w264bmc_ x11) + DIVERGENT faces machine-disclosed (W264 raw 92 = own-wave 81 + paths 11 not 87+11; W263 "
       "162 not 167; w263_ 93 not 89; THIRTEENTH 15 not 7; fourteenth x?; gate05/mirror owner text moved -- canon carries "
       "r1077-era spotcheck heal edits, derive author MUST use MEASURED counts not pattern-assumed, r1066 heal#5 family law) + "
       "ctxdumps (engine_owner lines, authored stamps, ordinal rows, 40-hex shas, UNBLOCKED narrative) for the derive author; "
       "W265 facts frozen in counts file header: A 598_301..600_300 14th A-hop / B 600_301..600_500 15th above-own-A / W264 "
       "finalize 1,005,135 / K 578,720 / seat origin 7343e3650 / prereg e57215a2c / 255th candidate bm-c 84th own; (5) S6 "
       "absorbed not rerun (dead-window 04:09:54 chain 43x rc0, same-round law; bars cutoff 10-16 weekend honest); (6) 5x DUTY "
       "= HANDOVER row r1083 landed (window r1076-r1083 eight frames; r1080 stamp missed-dead disclosed+discharged); (7) S7: "
       "attrition scan + claws x2 + loop pin=5 + watchdog checks + counter 1076->1084 | verify: smoke 49/49 + preflight core "
       "needles all-OK + estate on origin f2a4b0255 (push verified) + dual-FALSE probes post-fetch | behind-origin=0 (closeout "
       "push rides this window) | orphan face=0 | next " + NEXT + ": W265 SPLICE DERIVE FIRST ACTION (derive from "
       "_r1076bmc_derive_freeze.py template + counts-file needles + post-D-swap recomputation law; consume-before-produce band "
       "order; ordinal FOURTEENTH->FIFTEENTH before THIRTEENTH->FOURTEENTH; then freeze edits -> five-face splice -> engine "
       "self-burn -> sixgate PRE-FINALIZE -> finalize -> fivekeys -> sec.7/8 -> W266 seat); Monday 10-19 15:30 bars papers chain "
       "re-arm; next 5x=bm-c r1085")
with open(rp, "ab") as f:
    f.write(eol + row.encode("utf-8") + eol)
print("report row appended, EOL", repr(eol))

# ---------- HANDOVER 5x row ----------
hd = "research/HANDOVER.md"
rawh = open(hd, "rb").read()
eolh = b"\r\n" if rawh.endswith(b"\r\n") else b"\n"
hrow = ("> bm-c round 1083 层报核对：2026-10-18 05:1x 核对窗（窗口盖 r1076-r1083 八帧·5x 印章 r1080=死窗未盖·本窗补章披露）。真值权属="
        "round_reports-bm-c.md 全量在库+state-bm-c.json absorb/closeout notes。执行总结（r1076-r1083）=bm-c 席**误关事故恢复链+W264 全周期"
        "完成+W265 席+prereg 冻结+拼接预检**：事故链=CEO 22:49-23:02 全清令→00:3x 复工对齐令（36/36 任务恢复）→CEO 00:46 误关事故→"
        "bm-a O-20261018-0137 恢复令→r1078/r1080/r1081/r1082 吸收窗链（r1078 任务面板审计草件·r1080 taskaudit JSON 9e8084b54·r1081 W265 "
        "PREREG FREEZE e57215a2c+checkpoint 3917a974e·r1082 回执三件套 04:3x 死于 commit 前）+W264 全周期（r1076/r1077 死窗完成·finalize "
        "1,005,135/K=578,720·fivekeys 6/6·W265 席 7343e3650）+r1083 本窗=r1082 estate 落链 f2a4b0255（rebase bm-a 双 commit·11 同日幂等面"
        "冲突 live-wins·早推 behind=0）+W265 拼接预检（_w265bmc_splice_needle_preflight.py+counts 167 行·核心针全中·分歧面机器披露=canon 带 "
        "r1077 愈合痕·实测计数律）+3 仓令 ack（O-2207 UU 远控 bm-a 已回执/O-0137 own 回执落链/O-0348 bm-b 单腿零动作）+组树双水位 FALSE hold"
        "（ord 018ba8b2/dec 1d4741e4 post-fetch pinned-probe）。维护面全程：smoke 49/49 连续+S6 43/43 absorbed（04:09:54）+attrition CLEAN+"
        "quad green+孤儿面=0。最近实物清单指针：results/_w265bmc_splice_needle_counts.txt+research/PERPETUAL_N1_W265_PREREG.md+fleet/inbox/"
        "MSG-20261018-0431-bmc-taskaudit.md。指针：**W265 拼接 derive=r1084 FIRST ACTION（作者输入=counts 文件实测计数+post-D 重排律+consume-"
        "before-produce 带序律+序数序律）→freeze edits→五面拼接→引擎自烧→sixgate→finalize→W266 席；周一 10-19 15:30 bars papers 全链 re-arm**。"
        "下一个 5x=bm-c r1085。[via bm-c r1083]")
with open(hd, "ab") as f:
    f.write(eolh + hrow.encode("utf-8") + eolh)
print("HANDOVER row appended, EOL", repr(eolh))
print("CLOSEOUT WRITES DONE", TS, "epoch", EPOCH)
