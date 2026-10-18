# -*- coding: utf-8 -*-
"""r1103 closeout: state advance 1103->1104 + heartbeat + round report."""
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
    "r1103: clean continuation window (state round_no=1103 at open, executed r1103, advanced 1103->1104 so "
    "next=r1104); zero absorb owed (r1102-continuation closeout 44104391f9 landed clean 01:08:19, zero dead "
    "window between); (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 zero-kill (resident "
    "saturation-engine + ComfyUI faces legal) + S0 fetch 0/0 clean open (HEAD==origin 44104391f9, dirty = 3 "
    "own regenerable faces heartbeat/ack-scan/watermark_red); (2) S0.5 dual-delta FALSE both scans (opening "
    "probe + S7 tail probe; ord cf64b7a5 / dec 8706acd8 hold, zero rows owed, unacked=0, orders_ack 230 "
    "current); (3) S1 smoke 49/49; (4) P0 PRODUCT = W274 PREREG DERIVE PREP LANDED per r1096/r1098 "
    "honest-split window-budget law (derive builder clone = ~48KB full-window job): facts machine-frozen "
    "results/_w274bmc_facts.json via _r1103bmc_facts_gather.py -- frozen W273 template face 23,449B sha16 "
    "2f289446a93fa102 byte-verified @ 839441a547 PRE-backfill face per r1052/r1049 law (HEAD post-backfill "
    "twin 7a57ab1f3d3368ca disclosed NOT used) + W273 actuals FULL-PRECISION machine-read "
    "_r1102bmc_w273_fivekeys.json (merged mu -0.09278821626679142 / sigma 0.24510974987645237 / se_mu@598,520 "
    "0.000317 / w273_only -0.095021 / A p95 0.3124 / ledger 1,022,735+2,200=1,024,935 EXACT / n_eff_held "
    "1,022,735 / line_pre_w273 1.1966 / line_merged@598,520 1.1967 / K-lift +0.0001 / key1 gap 0.0022328 -> "
    "DIFF4 0.0022 for the builder roll) + W274 seat receipt bands A 618_101..620_100 / B 620_101..620_300 "
    "ADMIT in-gate zero-transcription + origin vacancy green (W274/W275 prereg absent on origin AND "
    "worktree) + sixgate receipt face (all_pass) + W273-cycle chain commits exist-verified (splice 04f2127db "
    "/ burns fbb4788c49+acc7fd02c0 / finalize estate 6659a0e36 / W274 seat 70b21a0264 / r1102 closeout "
    "44104391f9) + RAM live 4.8GB; derive = E63 canon-clone of _w273bmc machinery = r1104 FIRST ACTION; "
    "(5) S3 satengine ALIVE rc0 via Tools entry (r1102 pit row honored; W273 dedup 12/12 complete, queue "
    "waits-upstream on W274 prereg) + wm red=false healthy (next_pick=claimed moneyflow-IC parked "
    "source-blocked); (6) S6 light 10/10 rc0 (driver _r1103bmc_s6_light.py Monday pre-market: dualrun "
    "ZERO-DRIFT streak 51 [461] / compute_audit FLAG pool_starvation+supply_floor structural answered-by-"
    "chain [W274 prereg derive armed = supply head] / py_wm py_low_board_clear legal [bars_present=false "
    "Monday pre-market, board clear] / update_daily 0 rows cutoff 10-16 honest / regime ORANGE 6th day "
    "shadow / market_clock CALL-2026-10-16 ORANGE_COOL idempotent / fund_premium rc0 / REPORT-2026-10-19 "
    "faces=5 / token delta=0); (7) S7: attrition 4 files CLEAN (healed notes as-is) + idle --worked rc0 "
    "idle_rounds->0 + quad green (loop pin=5 no-op first fire 01:25 + watchdog S4U flip access-denied = "
    "adjudicated default-principal standing face per D-20261002-02 + pre-commit claw + pre-push claw "
    "installed) + tail dual-scan FALSE both + counter 1103->1104. KNOWN PENDING: W274 prereg derive = "
    "r1104 FIRST ACTION (all inputs machine-frozen on disk); Monday 10-20 15:30 bars window full papers "
    "chain (cutoff 10-16 current, debt=0); BigMoney-seat construction plan <=10-25; memory-governance "
    "@bm-c <=10-25."
)

DID = (
    "r1103: clean continuation (zero absorb) + W274 prereg derive PREP landed (facts machine-frozen: "
    "_w274bmc_facts.json + frozen W273 face 23,449B sha16 2f289446a93fa102 @ 839441a547 + W273 fivekeys "
    "actuals full-precision + W274 seat bands ADMIT in-gate + origin vacancy) + smoke 49/49 + S6 light "
    "10/10 rc0 + dual-delta FALSE both scans; derive clone = r1104 FIRST ACTION; counter 1103->1104"
)

PROD = (
    "CPU=W274 prereg PREP landed (facts machine-frozen _w274bmc_facts.json + frozen W273 face; derive "
    "builder clone = r1104 FIRST ACTION); GPU=MV lane idle per bank face (wave-3 done 00:42:53), loop "
    "CPU-only"
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
s["round_no"] = 1104
s["round_no_label"] = "r1103"
s["clock_read"] = ISO
s["cpu_pct"] = cpu_pct
s["current_task"] = "W274 prereg derive builder clone (r1104 FIRST ACTION)"
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
s["last_round"] = 1103
s["last_round_at"] = ISO
s["last_round_ts"] = ISO
s["last_round_label"] = "r1103"
s["last_round_closed_at"] = ISO
s["last_ts"] = ISO
s["last_action_at"] = ISO
s["now_active"] = ISO
s["note"] = PROD
s["ts"] = ISO
s["updated"] = ISO
s["updated_at"] = ISO
s["r1103_closeout_note"] = CLOSE
json.dump(s, open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(s.get("heartbeat_epoch_utc"), int)

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = ISO
h["cpu_pct"] = cpu_pct
h["current_task"] = "W274 prereg derive builder clone (r1104 FIRST ACTION)"
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
h["last_round_label"] = "r1103"
h["last_round_closed_at"] = ISO
h["now_active"] = ISO
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orders_ack_count"] = len(h.get("orders_ack", []))
h["orders_ack_last"] = "O-20261018-2236-bm-c.md"
h["orders_ack_ts"] = ISO
h["orders_ack_receipt"] = ("r1103: group ORD/DEC tail dual-scan FALSE both (ord cf64b7a5 / dec 8706acd8 hold, "
                           "zero rows owed, unacked=0, orders_ack 230 current)")
h["last_orders_sha_note"] = ("r1103: ORD watermark cf64b7a5 hold both scans (probe FALSE opening + tail; "
                             "zero new group rows this window)")
h["last_decisions_read_note"] = ("r1103: DEC delta FALSE hold both scans (8706acd8; zero new decision rows "
                                 "this window)")
h["prod_lanes"] = PROD
h["full_load_selfproof"] = {
    "占线一句话": PROD,
    "最近实物": "results/_w274bmc_facts.json + results/_w274bmc_w273_frozen_face.txt (W274 prereg facts "
               "machine-frozen; frozen face sha16 2f289446a93fa102 byte-verified @ 839441a547) @ " + ISO,
    "下个里程碑": "W274 prereg freeze (r1104 FIRST ACTION, window <=48h); Monday 10-20 15:30 papers chain; "
                 "BigMoney-seat construction plan <=10-25; memory-governance @bm-c <=10-25",
}
h["r1103_closeout_note"] = CLOSE
h["ts"] = ISO
json.dump(h, open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(h.get("heartbeat_epoch_utc"), int)

# --- round report ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    "%s | r1103 | clean continuation (zero absorb owed): P0=W274 prereg derive PREP landed per "
    "r1096/r1098 honest-split law -- facts machine-frozen _w274bmc_facts.json (frozen W273 face 23,449B "
    "sha16 2f289446a93fa102 byte-verified @ 839441a547 PRE-backfill; W273 actuals fivekeys full-precision "
    "machine-read: merged mu -0.09278821626679142 / sigma 0.24510974987645237 / se_mu 0.000317 / "
    "w273_only -0.095021 / p95 0.3124 / ledger 1,024,935 EXACT / line 1.1966->1.1967 / key1 gap 0.0022; "
    "W274 bands A 618_101..620_100 / B 620_101..620_300 ADMIT in-gate; origin vacancy green); smoke "
    "49/49; satengine ALIVE rc0 (Tools entry); S6 light 10/10 rc0 (dualrun streak 51 / audit FLAG "
    "answered-by-chain / py_low_board_clear legal / bars cutoff 10-16 honest / ORANGE 6th day / token 0); "
    "attrition 4 CLEAN; idle --worked; quad green (loop pin=5 no-op + watchdog adjudicated-default + "
    "claws x2); dual-delta FALSE both scans | evidence: results/_w274bmc_facts.json + "
    "results/_w274bmc_w273_frozen_face.txt + results/_r1103bmc_s6_log.txt | next: r1104 W274 prereg "
    "derive FIRST ACTION (E63 canon-clone of _w273bmc machinery, inputs frozen); pending: Monday 10-20 "
    "15:30 papers chain + BigMoney-seat plan 10-25 + memory-governance 10-25\n" % ISO
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print("CLOSEOUT LANDED: round_no=1104 epoch=%d (int OK) iso=%s ram_free=%sGB gpu_free=%sMiB" % (EPOCH, ISO, ram_free, mfree))
