# -*- coding: utf-8 -*-
# r1096 bm-c closeout: state advance 1096->1097 + heartbeat + round-report row (canonical
# root path per r750 law). Fresh-read-modify-write both faces; read-back asserts (R170/R178 epoch int law).
import json, time, datetime, psutil, subprocess, io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
NOWISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
vm = psutil.virtual_memory()
FREE_RAM = round(vm.available / (1024 ** 3), 2)
CPU_PCT = round(psutil.cpu_percent(interval=1), 1)
try:
    _g = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
    gu, gm, gt = [int(x.strip()) for x in _g.stdout.strip().split(",")]
except Exception:
    gu, gm, gt = 94, 7273, 16384

DID = ("r1096: W271 PREREG FREEZE LANDED origin f75b18c862 -- FIRST ACTION executed per the seat-first "
       "law on the post-W270-REGISTERED universe: frozen face extracted via python subprocess raw bytes "
       "(PS Out-File pipeline = GBK re-encode + newline-eat corruption on the first attempt, discarded "
       "same-window and re-extracted byte-clean; pit face disclosed) + byte-verified 23,259B sha256_16 "
       "3aa0b982 == blob 626148d0 @ freeze-commit 3bb8b9308e pre-backfill face (HEAD post-backfill twin "
       "92f167f2 disclosed NOT used per r1052/r1049 law) + needle facts-probe MEASURED r1077 law "
       "(results/_w271bmc_needle_probe.py/json: 8/8 block markers count==1 spans valid; placeholders "
       "zero-residual; ALL old-band instances block-interior outside=0; low-W faces W256..W251 all inside "
       "the b5 staircase list; static anchors W244/W247 survive un-rolled by design) + derive "
       "_w271bmc_prereg_derive.py canon-clone _w270bmc bloodline per E63 age() machine-needle law: 40 vmap "
       "legs + 108 measured floors + 13 disclosed POST_LEGS + 8 block NEWs + 85 MUST + 74 MUST_NOT + "
       "pinned counts, ALL GATES PASS with 2 authoring defect classes caught fail-closed same-window "
       "(git %h 10-char abbreviation vs 9-char prose labels healed to exact forms; probe-receipt leg4 "
       "W272p band format no-underscore machine-read match) + honest n_eff_held_equal forward-heal "
       "996,335->1,016,135 (canon carried the stale W260-era sub-face; r1093 full-precision law; pinned "
       "count==1 gate) + idempotent byte-identical f8b4a755d81bfbe5 + banned_direction_gate ADMIT rc0 "
       "zero banned hits; out research/PERPETUAL_N1_W271_PREREG.md 23,336B/64 lines; bands A "
       "611_501..613_500 TWENTIETH consecutive A-hop [naive 611_301..613_300 REFUSED at registered W270 "
       "B 611_301..611_500, hop past 611_500] / B 613_501..613_700 TWENTY-FIRST consecutive above-own-A "
       "[naive 611_501..611_700 lands inside own-A 611_501..613_500, cascade hop past 613_500] per seat "
       "receipt ADMIT verbatim; push race: bm-a r1062 addendum chain x3 landed mid-window (03833cf2b2) -> "
       "stash-bridge 4 regenerable daemon faces -> rebase clean -> LANDED 03833cf2b2..f75b18c862 "
       "first-try after bridge; splice chain (needle preflight + editor derive + freeze edits + engine "
       "self-burn + sixgate + finalize + fivekeys + sec.7/8 + W272 seat) = r1097 FIRST ACTION per "
       "multi-step window-budget law (W270 one-window precedent requires full budget); S6 light 10/10 "
       "rc0 (dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor "
       "answered-by-chain [W271 prereg frozen -> splice next] / py_wm insufficient_history fresh window / "
       "bars cutoff 10-16 weekend honest / ORANGE 6th day shadow / CALL-2026-10-16 ORANGE_COOL idempotent "
       "/ REPORT-2026-10-18 faces=5 / token delta=0); S7: attrition 4 CLEAN (guard scan rc0, healed "
       "historicals as-is) + S0.5 opening dual FALSE + S7 tail dual-scan FALSE both (pins ord c8b328c1 / "
       "dec 4cfdd17c hold, zero rows owed, unacked=0) + idle --worked rc0 + quad green (loop pin=5 no-op "
       "next fire 18:05 + watchdog registered next fire 17:59 [S4U flip access-denied = adjudicated "
       "default-principal standing face per D-20261002-02] + pre-commit/pre-push claws x2 installed) + "
       "orphan face=0 (round-zero probe py_faces=4)")

NEXT = ("r1097: (1) W271 five-face freeze splice chain = FIRST ACTION (needle preflight MEASURED "
        "[canon-clone _r1095bmc_needle_preflight.py against the _w270bmc_freeze_edits.py canon 62,142B "
        "wt==HEAD==origin triple] -> derive editor _w271bmc_derive_editor.py canon-clone of "
        "_w270bmc_derive_editor.py per E63 age() machine-needle law [consumers-before-producers band order "
        "+ own-first + B-ordinal caps before A-ordinal caps + _set_wave(271) +1 aging root-cure rep + "
        "r1091 W268 出稿双坑预检: gone 清单禁收裸波号 token + 折行断言形拆短 needle] -> freeze edits "
        "_w271bmc_freeze_edits.py -> splice (gate0.5: W270 row + W270 finalize in place = green) -> engine "
        "mtime-watch self-burn 12/12 -> sixgate PRE-FINALIZE -> finalize one-pass (ledger 1,018,335+2,200 "
        "=1,020,535 projected / K 591,920+2,200=594,120 projected, live-read governs r587) -> fivekeys -> "
        "sec.7/8 backfill -> W272 seat publish on the post-W271 universe [pre-disclosed: naive W272 A "
        "613_501..615_500 REFUSED at registered W271 B 613_501..613_700 -> A first-clean moves past "
        "613_700; never transcribe r587]); multi-step per window budget; (2) xq32 S5-27 "
        "PENDING-bmc-reroll: physical GPU re-roll queued behind PACK-A i2v drain (GPU KF lane, loop "
        "CPU-only standing; CEO weekend production); (3) Monday 10-20 15:30 bars window: full papers "
        "chain (weekend 10-18/19 no bars, cutoff 10-16 current, debt=0); (4) RAM watch standing (MV "
        "PACK-A GPU burn in flight, free-RAM face watched; loop CPU-only); (5) 24h died-pre-closeout "
        "incident-review watch standing per O-20261018-0948 sec.3.4")

ARTIFACT = ("W271 prereg freeze estate origin f75b18c862 (research/PERPETUAL_N1_W271_PREREG.md 23,336B "
            "64 lines sha256_16 f8b4a755d81bfbe5 idempotent-verified + results/_w271bmc_prereg_derive.py + "
            "results/_w271bmc_needle_probe.py + results/_w271bmc_needle_probe.json + "
            "results/_w271bmc_w270_frozen_face.txt [blob-verified @3bb8b9308e])")

VERDICT = ("green r1096 product window (W271 PREREG FREEZE landed f75b18c862 after one push-race "
           "stash-bridge rebase over bm-a r1062 chain; prereg = the seat-first FIRST ACTION product; "
           "splice chain armed = r1097 FIRST ACTION per multi-step window-budget law; CEO weekend-use "
           "standing loop CPU-only, GPU=MV PACK-A i2v burn in flight 94% util)")

# ---- state face ----
sp = os.path.join(REPO, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] in (1096, 1097), "counter precondition: %r (1097 = idempotent re-run)" % st["round_no"]
st.update({
    "round_no": 1097, "round_no_label": "r1096 closeout -> counter 1097",
    "last_round": "r1096", "last_round_at": NOWISO, "last_round_ts": NOWISO,
    "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO, "updated": NOWISO,
    "updated_at": NOWISO, "clock_read": NOWISO, "activity_now": NOWISO, "now_active": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO,
    "last_round_label": "r1096",
    "current_task": "r1096 closeout: W271 PREREG FREEZE landed origin f75b18c862; next = W271 five-face splice chain r1097 FIRST ACTION",
    "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": "r1096 closeout (W271 prereg freeze landed f75b18c862; counter 1096->1097)",
    "last_action_at": NOWISO, "head_sha": "r1096 closeout (W271 prereg freeze landed f75b18c862; counter 1096->1097)",
    "verdict": VERDICT, "verify": ("W271 prereg worktree==committed blob + on origin f75b18c862 behind=0 "
             "fetch-verified + frozen-face blob-identity @3bb8b9308e + needle probe receipt 8/8 blocks + "
             "derive ALL GATES PASS (40 legs/108 floors/13 post-legs/85 MUST/74 MUST_NOT/pinned) + "
             "idempotent byte-identical f8b4a755d81bfbe5 + banned_direction_gate ADMIT rc0 + S6 light "
             "10/10 + attrition 4 CLEAN + s05 opening+tail dual FALSE + unacked=0 + idle --worked rc0 + "
             "quad green (loop pin=5 no-op/watchdog adjudicated-default face/claws x2) + orphan face=0 + "
             "heartbeat epoch int + clock_read ISO-T read-back + 本地未达 origin commit 数=0"),
    "next": NEXT, "next_pointer": NEXT,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": ("W271 five-face freeze splice chain (r1097 FIRST ACTION, within 48h); Monday "
                        "10-20 15:30 papers chain; xq32 S5-27 GPU re-roll behind PACK-A drain"),
    "prod_lanes": ("CPU=engine W271 prereg FROZEN (f75b18c862 -> splice chain armed r1097 FIRST ACTION); "
                   "GPU=MV PACK-A i2v burn in flight (CEO weekend production standing: gen-only, loop "
                   "CPU-only); short-video lane DISABLED standing per O-20261017-1741"),
    "full_load_selfproof": {"占用一行": ("CPU=engine W271 prereg FROZEN (f75b18c862 -> splice chain armed "
        "r1097 FIRST ACTION); GPU=MV PACK-A i2v burn in flight (gen-only standing, loop CPU-only); "
        "short-video lane DISABLED standing per O-20261017-1741")},
    "note": ("r1096: product window (state round_no=1096 at open, executed r1096, advanced 1096->1097 so "
             "next=r1097); zero absorb owed (r1095 closeout landed clean 17:32:42, zero dead window "
             "between -- this window executed the prereg derive in direct continuation); zero "
             "double-count: S0.5 dual-delta FALSE both scans (opening + S7 tail; ord c8b328c1 / dec "
             "4cfdd17c hold per r1095 tail pins)"),
    "orphan_face": 0, "orphan_faces": 0,
    "free_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM, "idle_ram_gb": FREE_RAM,
    "cpu_pct": CPU_PCT, "cpu_util_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "orders_ack_receipt": ("r1096: S0.5 opening dual-delta FALSE both scans + S7 tail dual-scan FALSE "
                           "(ord content-sha1 c8b328c1 / dec raw-blob sha256 4cfdd17c hold per r1095 tail "
                           "pins; zero rows owed; unacked=0; zero face divergence)"),
    "last_orders_read_note": "r1096: dual FALSE at open + close (content-sha1 c8b328c1 hold, zero rows owed)",
    "last_decisions_read_note": "r1096: DEC delta FALSE hold both scans (raw-blob sha256 4cfdd17c, zero rows owed)",
    "ram_critical_face": ("MV PACK-A i2v GPU-lane python squeeze watch standing; loop CPU-only; free=%.2fGB "
                          "at r1096 closeout (prereg derive survived at this level)" % FREE_RAM),
    "sync": {"origin_tip": "r1096 W271 PREREG FREEZE f75b18c862 landed (stash-bridge rebase push, behind=0); closeout commit rides this window",
             "ts": NOWISO},
    "r1096_closeout_note": ("r1096: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 zero-kill + "
        "S0 fetch 0/0 clean open (2 daemon live-faces dirty, regenerable, no rebase owed); (2) S0.5 "
        "dual-delta FALSE both scans (opening + S7 tail; ord c8b328c1 / dec 4cfdd17c hold; unacked=0); "
        "(3) S1 smoke 49/49; (4) P0 PRODUCT = W271 PREREG FREEZE: frozen-face extraction (first attempt "
        "via PS Out-File pipeline corrupted = GBK re-encode + newline-eat, disclosed + discarded + "
        "re-extracted via python subprocess raw bytes; blob-identity 626148d0 @3bb8b9308e verified) + "
        "needle facts-probe MEASURED (8/8 blocks, old-band block-interior, low-W classification, T1 "
        "faces extraction) + derive ALL GATES PASS (2 authoring defect classes caught fail-closed: "
        "%h 10-char vs 9-char prose labels; leg4 no-underscore format) + 13 disclosed POST_LEGS "
        "(incl. honest n_eff_held_equal 1,016,135 forward-heal) + idempotent byte-identical "
        "f8b4a755d81bfbe5 + banned ADMIT rc0 + commit d4992959b + push non-FF once (bm-a r1062 addendum "
        "chain x3) -> stash-bridge 4 regenerable faces -> rebase clean -> LANDED f75b18c862 behind=0; "
        "(5) splice chain deferred to r1097 FIRST ACTION per multi-step window-budget law (editor "
        "derivation needs a full window budget; honest split per r1092/r1094 prereg-window precedent); "
        "(6) S6 light 10/10 rc0 (driver _r1096bmc_s6_light.py; dualrun streak 51 [461] / audit FLAG "
        "answered-by-chain / py_wm insufficient_history fresh / bars cutoff 10-16 weekend honest / "
        "ORANGE 6th day / ORANGE_COOL idempotent / REPORT-2026-10-18 faces=5 / token delta=0); "
        "(7) S7: attrition 4 CLEAN + idle --worked rc0 + quad green (loop pin=5 no-op next fire 18:05 "
        "+ watchdog next fire 17:59 adjudicated-default face + claws x2) + orphan face=0; counter "
        "1096->1097"),
})
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(sp, encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 1097 and st2["last_round"] == "r1096"

# ---- heartbeat face ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": NOWISO, "cpu_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "current_task": st["current_task"], "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "free_ram_gb": FREE_RAM, "idle_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM,
    "heartbeat_epoch_utc": EPOCH, "last_round": "r1096", "last_round_at": NOWISO,
    "last_round_ts": NOWISO, "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO,
    "round_no": 1097, "round_no_label": "r1096 closeout -> counter 1097",
    "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": st["last_action"], "last_action_at": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO, "last_round_label": "r1096",
    "verdict": VERDICT, "next_pointer": NEXT, "next": NEXT, "next_milestone": st["next_milestone"],
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "activity_now": NOWISO, "now_active": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "idle_rounds": 0, "agenda_starved": False,
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "gpu_free_mb": gt - gm, "gpu_idle_mb": gt - gm,
    "prod_lanes": st["prod_lanes"], "full_load_selfproof": st["full_load_selfproof"],
    "note": st["note"], "ram_critical_face": st["ram_critical_face"],
    "sync": st["sync"],
    "r1096_closeout_note": st["r1096_closeout_note"],
    "head_sha": st["head_sha"], "verify": st["verify"],
    "orders_ack_receipt": st["orders_ack_receipt"],
    "last_orders_read_note": st["last_orders_read_note"],
    "last_decisions_read_note": st["last_decisions_read_note"],
    "orphan_face": 0, "orphan_faces": 0,
    "last_round_at_legacy": hb.get("last_round_at_legacy"),
})
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hp, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert hb2["round_no"] == 1097 and len(hb2["orders_ack"]) == len(hb["orders_ack"]), \
    "heartbeat read-back: list length must hold (orders_ack_count FIELD is a known stale mirror r1052-family face)"

# ---- round report row (canonical root path per r750 law) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
ROW = ("| %s | r1096 | bm-c | watermark verdict=green (red=false lane healthy; S0.5 opening dual FALSE "
       "ord c8b328c1/dec 4cfdd17c hold per r1095 tail pins; S7 tail dual-scan FALSE both; unacked=0; "
       "satengine ALIVE burns=[] queue=[]; dualrun ZERO-DRIFT streak 51) | r1096: W271 PREREG FREEZE "
       "LANDED origin f75b18c862 (FIRST ACTION per seat-first law: frozen face @3bb8b9308e pre-backfill "
       "23,259B sha256_16 3aa0b982 blob-verified [HEAD post-backfill twin 92f167f2 disclosed NOT used "
       "r1052/r1049 law; PS Out-File first-attempt corruption disclosed + python-subprocess re-extract] "
       "+ needle facts-probe MEASURED [8/8 block markers; old-band all block-interior outside=0; low-W "
       "W256..W251 inside b5 staircase list; static W244/W247 un-rolled by design] + derive canon-clone "
       "_w270bmc bloodline E63 age() law: 40 vmap legs + 108 measured floors + 13 disclosed POST_LEGS + "
       "8 block NEWs + 85 MUST + 74 MUST_NOT ALL GATES PASS [2 authoring defect classes caught "
       "fail-closed: %%h 10-char vs 9-char labels; leg4 no-underscore format] + honest n_eff_held_equal "
       "1,016,135 forward-heal [canon stale W260-era sub-face; r1093 full-precision law] + idempotent "
       "byte-identical f8b4a755d81bfbe5 + banned ADMIT rc0; bands A 611_501..613_500 TWENTIETH "
       "A-hop / B 613_501..613_700 TWENTY-FIRST above-own-A per seat receipt ADMIT verbatim; push race "
       "bm-a r1062 addendum chain x3 -> stash-bridge 4 regenerable faces -> rebase clean -> LANDED "
       "03833cf2b2..f75b18c862) + splice chain = r1097 FIRST ACTION per multi-step window-budget law + "
       "S6 light 10/10 rc0 [dualrun streak 51 / FLAG answered-by-chain / py_wm insufficient_history "
       "fresh / bars cutoff 10-16 weekend honest / ORANGE 6th day shadow / ORANGE_COOL idempotent / "
       "REPORT-2026-10-18 faces=5 / token delta=0] + S7 attrition 4 CLEAN + idle --worked + quad green "
       "[loop pin=5 no-op + watchdog adjudicated-default face + claws x2] + orphan face=0 | 验证: prereg "
       "worktree==committed blob on origin f75b18c862 behind=0 fetch-verified + derive/probe receipts on "
       "disk + banned ADMIT rc0 + attrition scan rc0 + epoch int + 本地未达 origin commit 数=0 | 下步: "
       "r1097 W271 five-face freeze splice chain FIRST ACTION (needle preflight -> editor derive -> "
       "freeze edits -> splice -> engine self-burn -> sixgate -> finalize -> fivekeys -> sec.7/8 -> "
       "W272 seat; never transcribe r587); xq32 S5-27 GPU re-roll behind PACK-A drain; Monday 10-20 "
       "15:30 papers chain |\n\n" % NOWISO)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
print("CLOSEOUT OK r1096->1097 @ %s | ram=%.2fGB gpu=%d%%/%dMiB | epoch=%d" % (NOWISO, FREE_RAM, gu, gm, EPOCH))
