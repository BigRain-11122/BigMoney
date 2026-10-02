"""r364 bm-c S7 bookkeeping: state round bump (skip dead 363 per r529 law),
heartbeat refresh (epoch int + T-separated clock), round report append."""
import datetime
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# --- state-bm-c.json (preserve keys, update round faces) ---
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 364
st["last_round_at"] = "r364"
st["last_round_ts"] = now.strftime("%m/%d/%Y %H:%M:%S")
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = iso
st["last_decisions_read_at"] = now.strftime("%m/%d/%Y %H:%M:%S")
st["last_round"] = (
    "2026-10-02 r364 bm-c: W78 FINALIZE one-pass (prev 533,948 + 2,200 = 536,148 "
    "net head, K=169,520, S5 4/4, se_mu 0.000594, r538 no-rerun; dead-r363 "
    "heritage closed, slot 363 burned per r529 law) + W80 FREEZE (SIXTY-NINTH "
    "wave, bm-c 25th owned, A 203_004..205_003 + B 53_601..53_800 both "
    "arithmetic continuation zero skip; seat MSG-20261002-1204-bmc pre-pushed "
    "r565; gate + banned ADMIT; FIX-A/B/C pure insertion; engine v0.4 "
    "self-ignited 12:07, 12/12 burned) + S6 38/38 rc0 + smoke 47/47 + orders "
    "EMPTY both scans + D-19 MATCH + engine alive rc0")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- fleet/machines/bm-c.json heartbeat (preserve ack list) ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "last_seen": iso,
    "updated_at": iso,
    "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "round_no": 364,
    "cpu_util_pct": 88.0,
    "cpu_pct": 88.0,
    "cpu_idle_pct": 12.0,
    "cores": 32,
    "cpu_cores": 32,
    "free_ram_gb": 1.0,
    "ram_free_gb": 1.0,
    "idle_ram_gb": 1.0,
    "total_ram_gb": 25.7,
    "gpu_free_vram_mb": 9851,
    "gpu_vram_free_mb": 9851,
    "gpu_idle_vram_mb": 9851,
    "gpu_idle_vram_mib": 9851,
    "gpu_free_vram_mib": 9851,
    "health": "ok",
    "current_task": "r364 done: W78 FINALIZE landed (536,148 head) + W80 frozen & burned 12/12; T-131 collector in flight",
    "prod_lanes": ("r364: W78 FINALIZE landed (head 536,148, K=169,520, S5 4/4); "
                   "chain W1..W78 ALL LANDED; W79 bm-b finalize unblocked; "
                   "W80 frozen+burned (finalize waits W79 landing)"),
    "verdict": ("healthy: W78 finalize one-pass landed (536,148 head, S5 4/4, "
                "prereg backfill + default-wave selftest W2..W79); dead-r363 "
                "heritage closed (slot 363 burned r529 law); W80 freeze full "
                "lifecycle (seat pre-pushed r565, gate+banned ADMIT, FIX-A/B/C "
                "pure insertion, engine v0.4 self-ignited 12/12 burned); "
                "T-131 collector alive"),
    "activity_now": ("r364: W78 FINALIZE one-pass (536,148 head) + W80 FREEZE+burn "
                     "12/12 + S6 38/38 rc0 + smoke 47/47 + orders EMPTY both "
                     "scans + D-19 MATCH + attrition CLEAN + engine alive"),
    "latest_artifact": ("results/perpetual_faces/n1_w78_results.json (chain head "
                        "536,148, K=169,520, commit 57b07b71e, 2026-10-02T12:02) "
                        "+ W80 freeze package (commit 7fbeadb2e, 12:12: "
                        "PERPETUAL_N1_W80_PREREG.md + canon/leg/bands 5 faces) "
                        "+ n1_w80 shards 12/12"),
    "next_milestone": ("W80 finalize one-pass after bm-b W79 lands (window "
                       "<=48h, chain-order prev derive); month-boundary first "
                       "exam 10-31 (T-143 prep deliverable 10-29)"),
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# round_no int-epoch self-verify (R170/R178 law)
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
st2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"
print("STATE_OK round_no=364 epoch=%d clock=%s" % (hb2["heartbeat_epoch_utc"],
                                                   hb2["clock_read"]))
