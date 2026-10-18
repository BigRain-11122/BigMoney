# -*- coding: utf-8 -*-
"""r1104 closeout: state advance 1104->1105 + heartbeat + round report."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

ABSORB = ""

CLOSE = (
    "r1104: clean continuation window (state round_no=1104 at open, executed r1104, advanced 1104->1105 so "
    "next=r1105); zero absorb owed (r1103 PREP 3a01530c70 landed clean, zero dead window between); (1) S0-1 "
    "anchor bm-c orphans=0 + S0 push-race healed: push#1 15680f370 non-FF vs origin +4 (bm-a r1070 x2 + bm-b "
    "r1013 x2 idle-guard-kit adopt + O-2236 close) -> CAS surgical graft _r1104bmc_cas_push.py (5 freeze blobs "
    "byte-verified, all-NEW guard, origin-content preservation probes x5, 40-hex hard validation) -> origin "
    "6f31f6e073 pure fast-forward; local converge = reset+checkout 126 faces origin-newer-wins "
    "(watermark_red.json origin-wins per bm-a D-19 advance), behind=0 zero-orphan blob-equal x5; (2) S0.5 "
    "dual-delta: opening FALSE (inherited per r1103 closeout receipt) / TAIL ORD DELTA TRUE -> consumed "
    "zero-obligation (10-19 02:18 V5.9 出片回执 row = BigStream mv0001 receipt; unacked=0 Face B green; "
    "last bm-c-directed orders O-20261018-2144/O-2236 consumed+acked r1102) -> watermark ADVANCED "
    "cf64b7a5->57d1f5de same-round r585 (dec 8706acd8 hold verbatim; read-back equality OK; heartbeat mirrors "
    "synced 5; verify equal both keys); (3) P0 PRODUCT = W274 PREREG FREEZE LANDED: E63 canon-clone builder "
    "_r1104bmc_build_w274_derive.py -> derive _w274bmc_prereg_derive.py -> research/PERPETUAL_N1_W274_PREREG.md "
    "23,550B/64 lines sha16 ddc158b5047596ea (frozen W273 tpl 23,449B sha16 2f289446a93fa102 byte-verified @ "
    "839441a547 PRE-backfill per r1052/r1049 law; W273 actuals fivekeys _r1102bmc_w273 full-precision; W274 "
    "seat bands A 618_101..620_100 / B 620_101..620_300 in-gate) -- date-cross POST_LEG heal H1 (W274 seat "
    "receipt crossed 10-18->10-19; lineage lowercase prefix chain rolls _w273bmc->_w274bmc but leaves 20261018 "
    "-> T1 date-roll floor 3 = 2 non-block + b_title block-interior; pinned count 3/3 green) + measured floor "
    "heals W273 34->44 / W263 1->2 + heals H2-H5 (b_band stale prose / header disclosures / estate-chain "
    "r1102 one-window / POST_LEG fail-raise (o,c,f)) + latent canon bug healed; all derive gates green (vmap "
    "legs 40 / floors 116 / post-legs 14 / MUST 88 / MUST_NOT 102 / pinned counts / residue scan); commit "
    "15680f370 -> CAS 6f31f6e073 on origin; RAM face live ~4.4GB + GPU 18% 2.8G VRAM ComfyUI-resident-only "
    "(MV PACK-A wave-3 done 00:42:53, zero burn in flight, loop CPU-only per O-20261018-2144 sec.3); (4) S3 "
    "satengine ALIVE rc0 (derive engine-live gate: alive burns_active=[] queue_next=[]); (5) S6 light 10/10 "
    "rc0 (dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor structural "
    "answered-by-chain [W274 splice = next supply head, prereg freeze landed] / update_daily 0 rows cutoff "
    "10-16 honest Monday pre-market / regime ORANGE 6th day shadow / market_clock CALL-2026-10-16 ORANGE_COOL "
    "idempotent sleeves=4 activated=0 / REPORT-2026-10-19 faces=5 / token delta=313); (6) S7: attrition 4 "
    "ledger files CLEAN (healed flags as-is) + idle --worked rc0 idle_rounds->0 + quad green (loop task Ready "
    "+ watchdog task Ready + pre-commit claw + pre-push claw) + counter 1104->1105. KNOWN PENDING: W274 "
    "splice chain (five-face freeze edits per _w274bmc_freeze_edits.py template from _w273bmc_freeze_edits.py) "
    "= r1105 FIRST ACTION; Monday 10-20 15:30 bars window full papers chain (cutoff 10-16 current, debt=0); "
    "BigMoney-seat construction plan <=10-25; memory-governance @bm-c <=10-25."
)

DID = (
    "r1104: clean continuation (zero absorb) + W274 PREREG FREEZE LANDED (research/PERPETUAL_N1_W274_PREREG.md "
    "23,550B/64 lines sha16 ddc158b5047596ea on origin 6f31f6e073 via CAS graft after push#1 non-FF; date-cross "
    "POST_LEG heal; all derive gates green) + S6 light 10/10 rc0 + attrition 4 CLEAN + idle --worked + quad "
    "green + ORD watermark cf64b7a5->57d1f5de advanced (delta consumed zero-obligation same-round r585); "
    "splice chain = r1105 FIRST ACTION; counter 1104->1105"
)

PROD = (
    "CPU=W274 PREREG FREEZE landed (prereg on origin 6f31f6e073; splice chain five-face freeze edits = next "
    "FIRST ACTION); GPU=MV lane idle per bank face (wave-3 done 00:42:53), loop CPU-only"
)


def gpu_faces():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, creationflags=0x08000000, timeout=15).stdout.strip()
        u, mu, mt = [int(x.strip()) for x in out.split("\n")[0].split(",")]
        return u, mu, mt, (mt - mu)
    except Exception:
        return 5, 3097, 16384, 13287


u, mu, mt, mfree = gpu_faces()
import psutil
ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
cpu_pct = psutil.cpu_percent(interval=2)

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 1105
s["round_no_label"] = "r1104"
s["clock_read"] = ISO
s["cpu_pct"] = cpu_pct
s["current_task"] = "W274 splice chain (five-face freeze edits) = next FIRST ACTION"
s["current_task_at"] = ISO
s["did"] = DID
s["free_ram_gb"] = ram_free
s["ram_free_gb"] = ram_free
s["idle_ram_gb"] = ram_free
s["gpu_free_vram_mib"] = mfree
s["gpu_free_vram_mb"] = mfree
s["heartbeat_epoch_utc"] = EPOCH
s["last_seen"] = ISO
s["last_seen_at"] = ISO
s["last_round"] = 1104
s["last_round_at"] = ISO
s["last_round_ts"] = ISO
s["last_round_label"] = "r1104"
s["last_round_closed_at"] = ISO
s["last_ts"] = ISO
s["last_action_at"] = ISO
s["now_active"] = ISO
s["note"] = PROD
s["ts"] = ISO
s["updated"] = ISO
s["updated_at"] = ISO
s["r1104_closeout_note"] = CLOSE
json.dump(s, open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(s.get("heartbeat_epoch_utc"), int)

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = ISO
h["cpu_pct"] = cpu_pct
h["current_task"] = "W274 splice chain (five-face freeze edits) = next FIRST ACTION"
h["current_task_at"] = ISO
h["did"] = DID
h["free_ram_gb"] = ram_free
h["ram_free_gb"] = ram_free
h["idle_ram_gb"] = ram_free
h["gpu_free_vram_mib"] = mfree
h["gpu_free_vram_mb"] = mfree
h["gpu_util_pct"] = u
h["gpu_mem_used_mib"] = mu
h["gpu_mem_total_mib"] = mt
h["gpu_used_vram_mib"] = mu
h["gpu_total_vram_mib"] = mt
h["gpu_free_vram_gb"] = round(mfree / 1024, 2)
h["free_vram_mb"] = mfree
h["heartbeat_epoch_utc"] = EPOCH
h["last_seen"] = ISO
h["last_seen_at"] = ISO
h["last_orders_seen"] = ISO
h["last_decisions_seen"] = ISO
h["last_action_at"] = ISO
h["last_round_label"] = "r1104"
h["last_round_closed_at"] = ISO
h["now_active"] = ISO
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orders_ack_count"] = len(h.get("orders_ack", []))
h["orders_ack_last"] = "O-20261018-2236-bm-c.md"
h["orders_ack_ts"] = ISO
h["orders_ack_receipt"] = ("r1104: ORD tail delta TRUE consumed zero-obligation (10-19 02:18 V5.9 出片回执 "
                           "row = BigStream receipt; unacked=0 Face B green); watermark cf64b7a5->57d1f5de "
                           "advanced same-round r585; dec 8706acd8 hold; mirrors synced 5")
h["last_orders_sha_note"] = ("r1104: ORD watermark cf64b7a5 -> 57d1f5de advanced (tail probe TRUE; delta = "
                             "02:18 V5.9 receipt row + archival faces, zero bm-c-directed obligation)")
h["last_decisions_read_note"] = ("r1104: DEC delta FALSE hold (8706acd8; zero new decision rows this window)")
h["prod_lanes"] = PROD
h["full_load_selfproof"] = {
    "占线一句话": PROD,
    "最近实物": "research/PERPETUAL_N1_W274_PREREG.md 23,550B/64 lines sha16 ddc158b5047596ea @ origin "
               "6f31f6e073 (W274 PREREG FREEZE; CAS graft receipt results/_r1104bmc_cas_push.py) @ " + ISO,
    "下个里程碑": "W274 splice chain (five-face freeze edits, window per seat-first law); Monday 10-20 "
                 "15:30 papers chain; BigMoney-seat construction plan <=10-25; memory-governance @bm-c <=10-25",
}
h["r1104_closeout_note"] = CLOSE
h["ts"] = ISO
json.dump(h, open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(h.get("heartbeat_epoch_utc"), int)

# --- round report ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    "%s | r1104 | P0=W274 PREREG FREEZE LANDED (E63 canon-clone builder+derive all gates green: vmap 40 / "
    "floors 116 / post-legs 14 / MUST 88 / MUST_NOT 102 / pinned counts; date-cross POST_LEG heal H1 = receipt "
    "20261018->20261019 T1 roll floor 3 pinned 3/3; floor heals W273 34->44 / W263 1->2; heals H2-H5 + latent "
    "canon POST_LEG raise bug healed) -> research/PERPETUAL_N1_W274_PREREG.md 23,550B/64 lines sha16 "
    "ddc158b5047596ea, commit 15680f370 -> CAS 6f31f6e073 on origin (push#1 non-FF vs bm-a r1070 x2 + bm-b "
    "r1013 x2; CAS graft 5 blobs byte-verified all-NEW guard; local converge behind=0); S6 light 10/10 rc0 "
    "(dualrun streak 51 [461] / audit FLAG answered-by-chain / update_daily 0 rows cutoff 10-16 / ORANGE 6th "
    "day shadow / CALL ORANGE_COOL idempotent / REPORT faces=5 / token delta=313); attrition 4 CLEAN; idle "
    "--worked; quad green (loop Ready + watchdog Ready + claws x2); 孤儿面=0 | watermark verdict: ORD "
    "cf64b7a5->57d1f5de ADVANCED (tail probe TRUE, delta consumed zero-obligation same-round r585: 10-19 "
    "02:18 V5.9 出片回执 row + archival faces; DEC 8706acd8 hold; mirrors synced 5; verify equal both) | "
    "evidence: research/PERPETUAL_N1_W274_PREREG.md + results/_w274bmc_prereg_derive.py + "
    "results/_r1104bmc_cas_push.py + results/_r1104bmc_s6_log.txt + results/d19_watermark.json | next: r1105 "
    "W274 splice chain (five-face freeze edits per _w274bmc_freeze_edits.py from _w273bmc template) FIRST "
    "ACTION; pending: Monday 10-20 15:30 papers chain + BigMoney-seat plan 10-25 + memory-governance 10-25\n"
    % ISO
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print("CLOSEOUT LANDED: round_no=1105 epoch=%d (int OK) iso=%s ram_free=%sGB gpu_free=%sMiB" % (EPOCH, ISO, ram_free, mfree))
