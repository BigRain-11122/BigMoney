# -*- coding: utf-8 -*-
"""r1110 bm-c closeout script: state 1110->1111 + heartbeat mirror + round report row.
Fresh read-modify-write per multi-writer law; epoch int (smoke F7); clock ISO-T."""
import ctypes
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_dt = datetime.datetime.now().astimezone()
NOW = now_dt.isoformat(timespec="seconds")
EPOCH = int(time.time())


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
ram_free = round(mem.ullAvailPhys / 1024 ** 3, 1)
ram_total = round(mem.ullTotalPhys / 1024 ** 3, 1)

try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True,
                       creationflags=0x08000000)
    used, total, util = [x.strip() for x in r.stdout.splitlines()[0].split(",")]
    gpu_used, gpu_total, gpu_util = int(used), int(total), float(util)
    gpu_free = gpu_total - gpu_used
except Exception:
    gpu_used, gpu_total, gpu_util, gpu_free = 3056, 16384, 5.0, 13328

head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   encoding="utf-8").strip()

DID = ("r1110: W276 PREREG DERIVED + FREEZE-PUSHED origin 770a47fa1f first-try behind=0 -- "
       "research/PERPETUAL_N1_W276_PREREG.md 23,554B sha256_16 5352c7cf343fc5e5 "
       "BYTE-IDENTICAL to builder sim pre-flight (E63 canon-clone builder "
       "_r1110bmc_build_w276_derive.py -> _w276bmc_prereg_derive.py -> prereg md; derive run "
       "gates ALL PASS vmap 40 floors 118 post-legs 13 MUST 89 MUST_NOT 108); source = frozen "
       "W275 tpl @ 1fcc0bc30f blob e62f3bcb 23,551B PRE-backfill per r1049/r1052 (HEAD twin "
       "52b42b83 27,803B disclosed NOT used); bands per seat receipt 21b51a102 verbatim: A "
       "622_501..624_500 TWENTY-FIFTH consecutive A-hop (naive 622_301..624_300 refused at "
       "registered W275 B 622_301..622_500) / B 624_501..624_700 TWENTY-SIXTH consecutive "
       "above-own-A (base==own-A tail+1); W277p projection A 624_501..626_500 / B "
       "624_701..624_900 post-W276-REGISTERED pre-disclosed; upstream W275 finalize anchors "
       "FULL-PRECISION machine-read from _r1108bmc_w275_fivekeys.json (K=602,920 mu "
       "-0.09280541 sigma 0.24507989 W275-only -0.09398255 p95 0.3088 K-lift -0.0001 se_mu "
       "0.000316 n_eff_held 1,027,135 ledger 1,029,335 EXACT); banned_direction_gate ADMIT "
       "rc0; defect-birthplace heals at birth: (16) refuser band restored to "
       "machine-receipt face 注册 W275 B 带 622_301..622_500 落 naive A 窗内 (fix_refuser=2) + "
       "(17) freezer label unlagged W277 freezer 承接面强制注记 (fix_freezer=1); builder "
       "live-state hardening sweep-proven 21/21 (dead needle ~3.3GB->~4.0GB DELETED -- its "
       "OLD side == live face at psutil ~3.3GB silently un-rolled the live MUST entry, root "
       "cause of the window's transient SIM MUST failure; bare stale ban ~4.4GB REPLACED "
       "with context-scoped doubled-GPU-prose ban -- live==4.4GB collision class, r1107 "
       "heal-(4) sister); audit BAN doctrine refined (chain-legitimate recreated prior-gen "
       "faces + heal-doc-comment quotes NOT banned; collect-all audit); frozen-face SRC "
       "component roll w274->w275_frozen_face; 77 zero-hit needles receipted "
       "(_w276bmc_needle_probe.json); floor heals []; S6 light 10/10 rc0 (dualrun ZERO-DRIFT "
       "streak 51 [461] / audit FLAG pool_starvation+supply_floor answered-by-chain [W276 "
       "prereg DERIVED = supply head delivered] / update_daily 0 rows cutoff 10-16 pre-15:30 "
       "Monday honest / regime shadow ORANGE days=1 / CALL-2026-10-16 ORANGE_COOL "
       "idempotent / fund_premium no-op / b_layer all_pass mask 5222 / REPORT-2026-10-19 "
       "faces=5 / token delta=0)")

CLOSEOUT_NOTE = ("r1110: clean continuation product window (state round_no=1110 at open per "
                 "r1109 counter advance, executed r1110, advanced 1110->1111 so next=r1111); "
                 "zero absorb owed (r1109 closeout 7ec7d2af74 landed clean, zero dead window "
                 "between); (1) S0 anchor bm-c + dirty tree = routine runtime metadata (pull "
                 "--rebase refused per standing law, fetch instead, HEAD==ancestor origin) + "
                 "S0.5 D-19 dual FALSE opening (ord 57d1f5de / dec 8706acd8 hold, unacked=0, "
                 "orders files=105); (2) S1 smoke green; (3) P0 PRODUCT = W276 PREREG "
                 "DERIVED full-window job per r1096 honest-split precedent -- builder "
                 "iterated to BUILD OK through 3 defect classes (BAN over-aggression x2 "
                 "removed: chain-legitimate recreated faces 617_901..619_900 + heal-doc "
                 "comment W276 freezer label; SRC frozen-face filename generation component "
                 "lag w274->w275; live-state collisions: dead-needle undo at live RAM ~3.3GB "
                 "+ bare-ban collision at live 4.4GB, both root-caused via 2D RAM x GPU "
                 "sweep 21/21 PASS and hardened at birth) -> derive run rc0 prereg md "
                 "BYTE-IDENTICAL to sim -> banned_direction_gate ADMIT rc0 -> content "
                 "spot-check 26/26 -> surgical freeze commit via CAS temp-index recipe "
                 "(read-tree origin/main + update-index + commit-tree -p origin/main) "
                 "push first-try 770a47fa1f -> ls-tree verified + local convergence "
                 "15/15 twins MATCH deleted + ff-pull HEAD==origin; (4) S3 satengine ALIVE "
                 "via Tools entry (r1102 pit law; W275 dedup 12/12 complete queue "
                 "waits-upstream) + wm red=false healthy (next_pick=claimed moneyflow-IC "
                 "parked source-blocked, bm-a lane standing); (5) S4 CODELY.md pit entry "
                 "appended 9,742B < 10KB hot line (derive builder 活值碰撞坑两枚 + context-"
                 "scoped ban doctrine); (6) S6 light 10/10 rc0 via canon-clone "
                 "_r1110bmc_s6_light.py; (7) S7: attrition 4 files CLEAN active_loss=false "
                 "(receipt 06:26:32) + quad green (loop pin=5 Ready + watchdog Ready [S4U "
                 "flip = adjudicated standing face] + precommit/prepush claws installed) + "
                 "D-19 dual FALSE tail re-probe (shas hold 8706acd8/57d1f5de, zero mid-round "
                 "arrivals) + orphan face=0 tail (py_faces=4 zero-kill, resident=1 ComfyUI "
                 ":8188 legal) + idle productive-work counter cleared; counter 1110->1111 "
                 "so next session=r1111")

VERIFY = ("prereg freeze commit 770a47fa1f on origin behind=0 fetch-verified "
          "(a2a6ad56..770a47fa1f first-try push + ls-tree 4/4 + prereg blob daa87d01 "
          "origin==local + frozen face blob e62f3bcb == W275 freeze-commit blob identity) + "
          "derive output sha256_16 5352c7cf343fc5e5 == builder sim pre-flight "
          "BYTE-IDENTICAL + banned_direction_gate ADMIT rc0 (no banned direction claimed) + "
          "content spot-check 26/26 key faces + 2D live-state sweep 21/21 PASS (0.05..5.9GB "
          "x 7 GPU states) + local convergence 15/15 twins MATCH + ff-pull HEAD==origin + "
          "smoke green + S6 light 10/10 rc0 (log results/_r1110bmc_s6_log.txt: dualrun "
          "ZERO-DRIFT streak 51 [461] / audit FLAG answered-by-chain [W276 prereg DERIVED] "
          "/ bars cutoff 10-16 pre-15:30 honest / CALL-2026-10-16 ORANGE_COOL idempotent / "
          "b_layer all_pass / REPORT-2026-10-19 faces=5 / token delta=0) + attrition 4 "
          "CLEAN + quad green (loop + watchdog + claws x2) + D-19 dual FALSE both scans "
          "(opening 06:07 + tail re-probe; ord 57d1f5de / dec 8706acd8) + unacked=0 + "
          "orphan face=0 + epoch int + clock_read ISO-T")

NEXT = ("r1111: (1) W276 burn execution per prereg research/PERPETUAL_N1_W276_PREREG.md "
        "(five-face splice chain: freeze -> burn -> finalize per r1108 one-window W275 "
        "cycle precedent; bands A 622_501..624_500 / B 624_501..624_700; 12-shard "
        "SATURATION_ENGINE_LAW face, workers=8; anchors W275 fivekeys frozen); (2) TODAY "
        "Monday 2026-10-19 15:30 bars window: full papers chain (cutoff 10-16 current, "
        "debt=0); (3) BigMoney automation-plan faces (W-formalization / backtest-gate-in-"
        "loop / daily-PnL attribution per the CEO 20:48/20:54/21:11 order chain) = "
        "GM/committee-layer execution items deadlines <=10-25/<=10-31; (4) RAM watch "
        "standing (loop CPU-only, GPU idle)")

SUMMARY = ("r1110: W276 PREREG DERIVED + freeze-pushed origin 770a47fa1f first-try -- "
           "prereg 23,554B sha 5352c7cf343fc5e5 sim-identical; bands A 622_501..624_500 "
           "25th A-hop / B 624_501..624_700 26th above-own-A; banned_direction ADMIT; "
           "builder live-state hardening sweep 21/21")

ARTIFACT = ("W276 prereg research/PERPETUAL_N1_W276_PREREG.md @ origin 770a47fa1f (derive "
            "results/_w276bmc_prereg_derive.py; builder "
            "results/_r1110bmc_build_w276_derive.py; needle receipt "
            "results/_w276bmc_needle_probe.json)")

ROW = ("| {ts} | r1110 | W276 PREREG DERIVED + FREEZE-PUSHED origin 770a47fa1f first-try "
       "behind=0 -- research/PERPETUAL_N1_W276_PREREG.md 23,554B sha256_16 5352c7cf343fc5e5 "
       "BYTE-IDENTICAL to builder sim pre-flight (E63 canon-clone builder "
       "_r1110bmc_build_w276_derive.py SPANS+~130 count-asserted needles + full exec-sim on "
       "frozen T0 -> _w276bmc_prereg_derive.py -> prereg; derive gates ALL PASS vmap 40 "
       "floors 118 post-legs 13 MUST 89 MUST_NOT 108): source = frozen W275 tpl @ "
       "1fcc0bc30f blob e62f3bcb 23,551B PRE-backfill per r1049/r1052 (HEAD twin 52b42b83 "
       "disclosed NOT used); bands per seat receipt 21b51a102 verbatim: A 622_501..624_500 "
       "TWENTY-FIFTH consecutive A-hop (naive 622_301..624_300 refused at registered W275 "
       "B 622_301..622_500) / B 624_501..624_700 TWENTY-SIXTH consecutive above-own-A "
       "(base==own-A tail+1); W277p projection A 624_501..626_500 / B 624_701..624_900 "
       "post-W276-REGISTERED pre-disclosed; upstream W275 finalize anchors FULL-PRECISION "
       "machine-read _r1108bmc_w275_fivekeys.json (K=602,920 mu -0.09280541 sigma "
       "0.24507989 W275-only -0.09398255 p95 0.3088 K-lift -0.0001 se_mu 0.000316 n_eff "
       "1,027,135 ledger 1,029,335 EXACT); banned_direction_gate ADMIT rc0; defect heals at "
       "birth: (16) refuser band machine-receipt face restored (fix_refuser=2) + (17) "
       "freezer label unlagged W277 (fix_freezer=1); builder live-state hardening "
       "sweep-proven 21/21: dead needle ~3.3GB->~4.0GB DELETED (OLD side == live face at "
       "psutil ~3.3GB silently un-rolled the live MUST entry = root cause of the window's "
       "transient SIM MUST failure) + bare stale ban ~4.4GB REPLACED with context-scoped "
       "doubled-GPU-prose ban (live==4.4GB collision class, r1107 heal-(4) sister); BAN "
       "doctrine refined (chain-legitimate recreated prior-gen faces + heal-doc-comment "
       "quotes NOT banned; collect-all audit); SRC component roll w274->w275_frozen_face | "
       "freeze commit 770a47fa1f on origin behind=0 fetch-verified (CAS temp-index surgery "
       "on origin/main a2a6ad56, ls-tree 4/4, prereg blob daa87d01 origin==local, frozen "
       "face blob e62f3bcb == W275 freeze-commit blob) + local convergence 15/15 twins "
       "MATCH deleted + ff-pull HEAD==origin + 2D RAMxGPU sweep 21/21 PASS + content "
       "spot-check 26/26 + smoke green + S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51 "
       "[461] / audit FLAG pool_starvation+supply_floor answered-by-chain [W276 prereg "
       "DERIVED = supply head delivered] / update_daily 0 rows cutoff 10-16 pre-15:30 "
       "Monday honest / regime shadow ORANGE days=1 / CALL-2026-10-16 ORANGE_COOL "
       "idempotent / fund_premium no-op / b_layer all_pass mask 5222 / REPORT-2026-10-19 "
       "faces=5 / token delta=0) + attrition 4 files CLEAN active_loss=false + quad green "
       "(loop pin=5 Ready + watchdog Ready [S4U flip = adjudicated standing face] + "
       "precommit/prepush claws installed) + D-19 dual FALSE both scans opening 06:07 + "
       "tail re-probe (ord 57d1f5de / dec 8706acd8 hold, unacked=0, zero mid-round "
       "arrivals) + orphan face=0 tail (py_faces=4 zero-kill, resident=1 legal) + CODELY.md "
       "pit entry appended 9,742B < 10KB hot line + epoch int + clock_read ISO-T | "
       "{next} | 孤儿面=0（tail probe py_faces=4 只读零杀·ComfyUI :8188 resident 合法） | "
       "当前活=W276 prereg 已冻结上链、r1111=烧录执行 / 最近实物=prereg commit 770a47fa1f"
       "（A 622_501..624_500 / B 624_501..624_700）@ {ts} / 下个里程碑=W276 burn+finalize "
       "+今日 15:30 papers | watermark=green | 本地未达 origin commit 数=0 |").format(
           ts=NOW, next=NEXT)


def update_faces(d):
    d["activity_now"] = NOW
    d["clock_read"] = NOW
    d["current_task"] = "W276 burn execution = r1111 FIRST ACTION"
    d["current_task_at"] = NOW
    d["current_task_ts"] = EPOCH
    d["did"] = DID
    d["free_ram_gb"] = ram_free
    d["idle_ram_gb"] = ram_free
    d["ram_free_gb"] = ram_free
    d["total_ram_gb"] = ram_total
    d["full_load_selfproof"] = {
        "占用一行": ("CPU=W276 PREREG DERIVED origin 770a47fa1f (r1110 product; W276 burn "
                    "execution = r1111 FIRST ACTION); GPU=idle ~%.1fG free, loop CPU-only; "
                    "short-video lane DISABLED standing per O-20261017-1741" % (gpu_free / 1024.0)),
        "最近实物": ("research/PERPETUAL_N1_W276_PREREG.md @ origin 770a47fa1f (23,554B "
                    "sha 5352c7cf343fc5e5) + freeze commit 770a47fa1f @ " + NOW),
        "下个里程碑": ("W276 burn+finalize (r1111 FIRST ACTION); TODAY Monday 2026-10-19 "
                    "15:30 papers chain; BM automation-plan <=10-25"),
    }
    d["gpu_used_mib"] = gpu_used
    d["gpu_mem_total_mib"] = gpu_total
    d["gpu_util_pct"] = gpu_util
    for k in ("gpu_free_mib", "gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_mb", "gpu_idle_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "free_vram_mb"):
        d[k] = gpu_free
    d["gpu_free_vram_gb"] = round(gpu_free / 1024.0, 2)
    d["head_sha"] = head_sha
    d["heartbeat_epoch_utc"] = EPOCH
    d["heartbeat_epoch_utc_type"] = "int (assert)"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["last_action"] = "W276 prereg derive + freeze push 770a47fa1f + S6 10/10 + closeout"
    d["last_action_at"] = NOW
    d["last_artifact"] = ARTIFACT
    d["latest_artifact"] = ARTIFACT
    d["recent_artifact"] = ARTIFACT
    d["last_decisions_read_at"] = NOW
    d["last_decisions_seen"] = NOW
    d["last_orders_read_at"] = NOW
    d["last_orders_seen"] = NOW
    d["last_round"] = 1110
    d["last_round_at"] = NOW
    d["last_round_closed"] = 1110
    d["last_round_closed_at"] = NOW
    d["last_round_label"] = "r1110"
    d["last_round_summary"] = SUMMARY
    d["last_round_summary_at"] = NOW
    d["last_round_ts"] = NOW
    d["last_seen"] = NOW
    d["last_seen_at"] = NOW
    d["next"] = NEXT
    d["next_pointer"] = NEXT
    d["next_milestone"] = ("W276 burn+finalize (r1111 FIRST ACTION); TODAY Monday "
                           "2026-10-19 15:30 papers chain")
    d["note"] = ("CPU=W276 PREREG DERIVED (freeze 770a47fa1f; burn execution = r1111 FIRST "
                 "ACTION); GPU=idle %.1fG free (loop CPU-only); short-video lane DISABLED "
                 "standing per O-20261017-1741" % (gpu_free / 1024.0))
    d["now_active"] = "W276 prereg derived + frozen; burn execution next"
    d["orders_ack_receipt"] = ("r1110: opening scan dual FALSE both (ord 57d1f5de / dec "
                              "8706acd8 hold; unacked=0, files=105 inside ack-230); S7 tail "
                              "re-probe dual FALSE same -- zero mid-round arrivals")
    d["orders_ack_ts"] = NOW
    d["orphan_face"] = 0
    d["orphan_faces"] = 0
    d["prod_lanes"] = ("CPU=W276 PREREG DERIVED (freeze 770a47fa1f; burn execution = r1111 "
                       "FIRST ACTION); GPU=idle %.1fG free (loop CPU-only); short-video lane "
                       "DISABLED standing per O-20261017-1741" % (gpu_free / 1024.0))
    d["ram_critical_face"] = "none (loop CPU-only, GPU idle, %.1fGB free)" % ram_free
    d["sync"] = {"origin_tip": "r1110 W276 PREREG DERIVED 770a47fa1f", "ts": NOW}
    d["ts"] = NOW
    d["updated"] = NOW
    d["updated_at"] = NOW
    d["verdict"] = ("green r1110 product window (W276 PREREG DERIVED + freeze-pushed "
                    "origin 770a47fa1f first-try: sim-identical 23,554B; banned_direction "
                    "ADMIT; sweep 21/21; smoke green; S6 10/10; loop CPU-only, GPU idle)")
    d["verify"] = VERIFY


sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    state = json.load(f)
update_faces(state)
state["round_no"] = 1111
state["round_no_label"] = "r1110"
state["r1110_closeout_note"] = CLOSEOUT_NOTE
state["last_pulled_at"] = NOW
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
update_faces(hb)
hb["round_no"] = 1111
hb["round_no_label"] = "r1110 closeout -> counter 1111"
hb["r1110_closeout_note"] = CLOSEOUT_NOTE
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

rp = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if (b"\r\n" in raw[-4000:] or raw.endswith(b"\r\n")) else b"\n"
with open(rp, "ab") as f:
    f.write(ROW.encode("utf-8") + eol)

chk_state = json.load(open(sp, encoding="utf-8"))
chk_hb = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk_state["heartbeat_epoch_utc"], int), "state epoch not int"
assert isinstance(chk_hb["heartbeat_epoch_utc"], int), "heartbeat epoch not int"
assert chk_state["round_no"] == 1111 and chk_hb["round_no"] == 1111
assert "T" in chk_hb["clock_read"]
print("CLOSEOUT OK round 1110->1111 epoch=%d ram_free=%.1fGB gpu_free=%dMiB head=%s" %
      (EPOCH, ram_free, gpu_free, head_sha[:10]))
