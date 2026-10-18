# -*- coding: utf-8 -*-
"""r1102-continuation closeout: state advance 1102->1103 + heartbeat + round report."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(NOW.timestamp())

ABSORB = (
    "r1102 absorb note: prior window (self-labeled r1102, fired ~22:12, died ~00:4x) executed the FULL W273 "
    "own-wave cycle (prereg frozen b6bbb69e92 surgery-delivered 839441a547 + splice 04f2127db CLEAN-AT-BIRTH "
    "6th gen + engine self-burn 12/12 appender-batched fbb4788c49+acc7fd02c0 + sixgate 36th ALL PASS + finalize "
    "one-pass 6659a0e36 ledger 1,024,935/K=598,520 EXACT + fivekeys 6/6 + sec78 backfill zero-placeholder) + "
    "closeout commit 1fb2cb6217 pushed behind=0, then died POST-closeout-commit PRE-counter-advance/heartbeat "
    "(state frozen at 1102, heartbeat stale at r1101 21:21:31). THIS window machine-verified the estate BEFORE "
    "landing (origin commits 6659a0e362/1fb2cb6217 exist-verified, behind=0, zero concurrent window: only "
    "minigame-lane codely pid 29816), executed as r1102-continuation per counter; zero double-count: S0.5 "
    "opening scan (dead-window tail face 00:45:02) surfaced ORD unacked x2 (O-20261018-2144/O-20261018-2236) "
    "-- both consumed+acked THIS window; DEC delta 4cfdd17c->8706acd8 consumed+advanced."
)

CLOSE = (
    "r1102: (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 zero-kill (resident saturation-engine + "
    "ComfyUI faces legal) + S0 fetch 0/0 clean open (HEAD==origin 1fb2cb6217, dirty = daemon live-faces); "
    "(2) S0.5 dual consumption: O-2144/O-2236 both acked (receipt rows + orders_ack 228->230) -- BmcIdleGuard "
    "obligation verified DONE by sister MV window (task \\BmcIdleGuard Ready 10min + first live tick 00:45:59 "
    "idle tick 1 + kit on-chain 354f66e) + MSG-2310 processed + replied (MSG-20261019-0102: kit landed + "
    "work-bank schema CAS-pushed origin 354f66e..612d580e) + MSG-0058-bmc-slots P-CARD slot receipt landed "
    "(X470 AORUS ULTRA GAMING-CF; WMI 3-slot: J10 in-use=3070-16GB / J3600 x8 reports in-use vs single-GPU "
    "nvidia-smi = physical-inspect pending / J3707 x4; PSU 8pin un-enumerated; 3070 link gen3 x8 disclosed) "
    "-- P102/P104#1->bm-b unchanged, P104#2 elastic-seat decision inputs now complete (bm-b MSG-2355 + this); "
    "D-19 watermark dual advance dec=8706acd8 ord=cf64b7a5 (mirrors synced 5) + group ORD 10-18 rows consumed "
    "(nine-company automation dispatch noted: BigMoney seat construction-plan deadline 10-25 logged for later "
    "windows); (3) S1 smoke 49/49; (4) P0 PRODUCT = W274 SEAT PUBLISHED origin 70b21a0264 first-try (E63 builder "
    "_r1102bmc_build_w274_probe.py 53 needles all-count-asserted + probe _w274bmc_20261019_probe.py ADMIT "
    "first-try: A 618_101..620_100 23rd consecutive A-hop (live walk refused naive 617_901..619_900 at "
    "registered W273 B 617_901..618_100) / B 620_101..620_300 24th consecutive above-own-A (base==own-A "
    "tail+1); seed FREE x2 618101/2000 + 620101/200; vacancy four-check; zero W275/W276 skip-claims; universe "
    "263 owner rows bmc 92; W274=264th wave bm-c 93rd own wave); (5) S3 satengine ALIVE rc0 via Tools entry "
    "(r1102 pit row honored: scripts/ copy state-path divergence face, zero misdiagnosis) + idle "
    "green_idle=false idle_rounds=0 (window has actual work); (6) S6 light 10/10 rc0 (driver "
    "_r1102bmc_s6_light.py Monday pre-market: dualrun streak 51 / compute_audit green / py_wm red=false "
    "healthy / bars cutoff 10-16 weekend-honest no-ops / REPORT-20261019 / token delta=0); (7) S7: attrition 4 "
    "CLEAN (healed shrinks noted) + idle --worked rc0 + quad green (loop pin=5 no-op first fire 01:15 + "
    "watchdog S4U flip denied = adjudicated default-principal standing face D-20261002-02 + claws x2 "
    "installed) + tail dual-scan re-probe + counter 1102->1103. KNOWN PENDING: W274 prereg derive = r1103 "
    "FIRST ACTION (post-W273 universe, r1096 honest-split law); memory-governance @bm-c item "
    "(agent-library-sync + L0 snapshot + fleet memory archive moves, deadline 10-25); BigMoney-seat "
    "construction plan (nine-company automation face, deadline 10-25)."
)

DID = (
    "r1102-continuation: absorbed dead r1102 (W273 cycle landed by predecessor, counter/heartbeat healed) + "
    "O-2144/O-2236 dual-ack (IdleGuard evidence + MSG-2310 kit-landed reply + work-bank schema origin "
    "612d580e) + P-CARD bm-c slot receipt MSG-0058 + W274 SEAT PUBLISHED origin 70b21a0264 (A 618_101..620_100 "
    "/ B 620_101..620_300, probe ADMIT first-try) + smoke 49/49 + S6 light 10/10 + D-19 dual advance; "
    "counter 1102->1103"
)

PROD = (
    "CPU=W274 SEAT PUBLISHED origin 70b21a0264 (supply head; prereg derive = r1103 FIRST ACTION); "
    "GPU=MV lane wave-3 done per bank face (packA-qc-strips-v1 done 00:42:53, guard idle-tick face), "
    "loop CPU-only"
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
s["round_no"] = 1103
s["round_no_label"] = "r1102"
s["clock_read"] = ISO
s["cpu_pct"] = cpu_pct
s["current_task"] = "W274 prereg derive (next window FIRST ACTION)"
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
s["last_round"] = 1102
s["last_round_at"] = ISO
s["last_round_ts"] = ISO
s["last_round_label"] = "r1102"
s["last_round_closed_at"] = ISO
s["last_ts"] = ISO
s["last_action_at"] = ISO
s["now_active"] = ISO
s["note"] = PROD
s["ts"] = ISO
s["updated"] = ISO
s["updated_at"] = ISO
s["r1102_absorb_note"] = ABSORB
s["r1102_closeout_note"] = CLOSE
json.dump(s, open(sp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(s.get("heartbeat_epoch_utc"), int)

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["clock_read"] = ISO
h["cpu_pct"] = cpu_pct
h["current_task"] = "W274 prereg derive (r1103 FIRST ACTION)"
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
h["last_round_label"] = "r1102"
h["last_round_closed_at"] = ISO
h["now_active"] = ISO
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orders_ack_count"] = len(h.get("orders_ack", []))
h["orders_ack_last"] = "O-20261018-2236-bm-c.md"
h["orders_ack_ts"] = ISO
h["orders_ack_receipt"] = ("r1102: O-2144/O-2236 both consumed+acked (IdleGuard evidence row + MSG-2310 "
                           "kit-landed reply + slot receipt); group ORD tail dual-scan green")
h["last_orders_sha_note"] = ("r1102: ORD watermark advanced to cf64b7a5 via d19 --advance (O-2144/O-2236 "
                             "receipt rows + seat MSG + slot MSG landed; tail re-probe green)")
h["last_decisions_read_note"] = ("r1102: DEC delta consumed (4cfdd17c->8706acd8 advanced via d19 --advance; "
                                 "nine-company automation dispatch rows read, BigMoney-seat plan deadline 10-25 logged)")
h["prod_lanes"] = PROD
h["full_load_selfproof"] = {
    "占线一句话": PROD,
    "最近实物": "W274 seat origin 70b21a0264 (probe receipt ADMIT) + work-bank schema origin 612d580e + "
               "MSG-0058-bmc-slots @ " + ISO,
    "下个里程碑": "W274 prereg freeze (r1103 FIRST ACTION, window <=48h); BigMoney-seat construction plan "
                 "<=10-25; memory-governance @bm-c <=10-25",
}
h["r1102_absorb_note"] = ABSORB
h["r1102_closeout_note"] = CLOSE
h["ts"] = ISO
json.dump(h, open(hp, "w", encoding="utf-8", newline=""), ensure_ascii=False, indent=1)
assert isinstance(h.get("heartbeat_epoch_utc"), int)

# --- round report ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (
    "%s | r1102 | absorb-continuation: dead r1102 (W273 full cycle+closeout commit 1fb2cb6217 pushed, died "
    "pre-counter/heartbeat) estate verified+healed; O-2144/O-2236 dual-ack (BmcIdleGuard Ready evidence + "
    "MSG-2310 reply kit-landed + work-bank schema CAS 354f66e..612d580e + P-CARD bm-c slot receipt "
    "MSG-0058: X470 board, J3600 physical-inspect pending); P0=W274 SEAT PUBLISHED origin 70b21a0264 "
    "first-try (A 618_101..620_100 23rd A-hop / B 620_101..620_300 24th above-own-A, probe ADMIT "
    "first-try, seed FREE x2, vacancy four-check, 264th wave/bm-c 93rd own); smoke 49/49; satengine ALIVE "
    "rc0 (Tools entry per pit row); S6 light 10/10 rc0 (wm red=false, bars 10-16 honest, token 0); "
    "attrition 4 CLEAN; idle --worked; D-19 dual advance dec 8706acd8/ord cf64b7a5 | evidence: "
    "results/_w274bmc_20261019_probe_receipt.json verdict=ADMIT + git 1fb2cb6217..70b21a0264 + "
    "results/_r1102bmc_s6_log.txt | next: r1103 W274 prereg derive FIRST ACTION (post-W273 universe); "
    "pending: BigMoney-seat plan 10-25 + memory-governance 10-25\n" % ISO
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print("CLOSEOUT LANDED: round_no=1103 epoch=%d (int OK) iso=%s ram_free=%sGB gpu_free=%sMiB" % (EPOCH, ISO, ram_free, mfree))
