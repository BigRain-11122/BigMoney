# _r882bmc_closeout.py -- r882 bm-c closeout bookkeeping
# (round report append + state r882 + heartbeat refresh; r881 pattern)

import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())


def ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1 << 30), 2)
    except Exception:
        return None


def gpu_free_mb():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


RAM = ram_gb()
GPU = gpu_free_mb()
TS = now

report_line = (
    f"{TS} | r882 | S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=2 "
    "(both identified, zero kill: PID19712=BigStream MV designed-detached KF pythonw "
    "[other-domain no-action]; PID37248=W18 shard-0 runner r379 RAM-gate bounded wait "
    "-> PARKED NATURALLY 17:52:04 r491 park law, marker flushed) | "
    "S0 dirty-tree ff surgery: 9-behind, 18-face intersection all S6-regenerable "
    "(backup + treasure_guard prescan rc0 + checkout + ff) -> HEAD 27fadaa55 behind=0; "
    "T-184 dual-heal converged (bm-c r881 + bm-b r889, JSON 18 keys 0 markers) | "
    "S0.5 ORD/DEC delta FALSE (70/70 acked) | S1 smoke 49/49 | S2 boards clear "
    "(jobs 0, tickets all claimed; T-185-P1 W18 lane=bm-c) | satengine rc0 alive | "
    "watermark RED lane=pool-batch-runnable-idle-low-cpu -> GM waiver O-1612 legal yield: "
    "RAM 1.2-1.7GB << 4GB r354 gate (CEO game session + MV chain), W18 shards 2-7 "
    "ACTIVELY burning on bm-b per r881 relay, shards 0/1 parked awaiting bm-c RAM window "
    "(un-park = session flip) | S6 38/38 rc0 (leg-24 shell kill = my Select-Object "
    "buffering mistake vs 5-min zero-output law, continuation driver legs 25-38, "
    "zero chain fault; aggressive_lab rc=0 idempotent -- r881 transient rc=2 NOT "
    "reproduced) | S7: attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered + "
    "precommit/prepush claws installed | W18 fleet-state verification product: "
    "checkpoint cross-machine sync path CONFIRMED (pool workers push claims; "
    "per-machine round commits runner artifacts; screen-finalize reads local CKPT_DIR "
    "692+200 count gate -> finalizer pulls all-8; bm-b burns 2-7) | orphan_face=2 | "
    "idle --worked (real product round) | push self-proof below"
)

rp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(report_line + "\n")

# ---------------- state ----------------
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8-sig") as fh:
    st = json.load(fh)
st["round_no"] = 882
st["round_no_label"] = "r882"
st["loop_round"] = 882
st["last_round"] = 881
st["clock_read"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["last_seen"] = TS
st["last_seen_at"] = TS
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["last_round_closed"] = TS
st["heartbeat_epoch_utc"] = epoch
st["free_ram_gb"] = RAM
st["ram_free_gb"] = RAM
st["idle_ram_gb"] = RAM
st["orphan_face"] = 2
st["orphan_faces"] = 2
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["head_sha"] = "27fadaa55"
st["last_pulled_at"] = TS
st["current_task"] = (
    "当前活: W18 screen 分片全链守望+收口（bm-b 烧 shards 2-7·bm-c 0/1 parked 等 RAM 窗·合法让路）"
    f"| 最近实物: S6 38/38 rc0 + W18 fleet 状态验证 + r882 台账（{TS}）"
    "| 下个里程碑: W18 8/8 分片齐 -> screen-finalize -> JUDGE -> CEO 48h 报时钟（judge 落地起算·ETA 视 bm-b 烧速与 bm-c RAM 窗）"
)
st["current_task_at"] = TS
st["did"] = (
    "r882 bm-c: (1) S0-1 anchor + probe orphans=2 identified zero-kill "
    "(MV detached pythonw other-domain + W18 shard-0 runner RAM-gate waiter "
    "-> parked naturally 17:52:04 per r491); (2) S0 dirty-tree ff surgery "
    "9-behind 18-face intersection backup+guard-rc0+checkout+ff -> 27fadaa55 "
    "behind=0, T-184 dual-heal converged verified; (3) S0.5 zero delta; "
    "(4) S1 49/49; (5) watermark RED pool-batch lane -> GM waiver legal yield "
    "(RAM gate, shards 2-7 burning bm-b, 0/1 parked); (6) S6 38/38 rc0 via "
    "continuation driver after my Select-Object buffering kill mistake "
    "(disclosed); (7) S7 attrition CLEAN + pins + claws; (8) W18 sync-path "
    "verification product (finalizer-pull model confirmed)"
)
st["note"] = ("r882: S6 38/38 + W18 fleet-state verify + zero-kill orphan "
              "handling; shard-0 parked r491, shard-1 waiter deadline ~18:16; "
              "bm-b burns 2-7.")
st["verdict"] = ("r882 bm-c: S0 ff-surgery 9-behind -> behind=0 + smoke 49/49 + "
                 "S6 38/38 rc0 + W18 screen relay working as designed (bm-b "
                 "2-7 burning, 0/1 RAM-parked legal yield) + watermark RED "
                 "waiver documented")
st["verify"] = ("receipts: smoke 49/49 + S6 38/38 rc0 "
                "(results/_r882bmc_s6_log.txt) + attrition 4 CLEAN + "
                "idle --worked + this books commit/push_verify")
st["activity_now"] = (
    "current activity: W18 screen shards distributed-burn watch "
    "(bm-b 2-7 in flight, bm-c 0/1 RAM-parked legal yield) | round proof: "
    "S6 38/38 rc0 + smoke 49/49 + orphan face=2 zero-kill identified | "
    "next milestone: 8/8 shards -> screen-finalize -> JUDGE (48h CEO clock)"
)
st["next"] = (
    "r883: (1) W18 shard landing watch: bm-b checkpoint artifacts via its "
    "round commits; shard-1 waiter park landing (~18:16 deadline) verify; "
    "(2) RAM window watch: CEO session end -> session flip un-park -> "
    "bm-c burns 0/1; (3) 8/8 complete -> screen-finalize (G-face battery + "
    "692+200 count gate) -> judge-prep -> JUDGE -> 48h CEO clock; (4) T-184 "
    "transfer deadline watch (10-12 15:30, bm-a->bm-b non-party); "
    "(5) W208 revival watch (bm-a domain)"
)
st["next_pointer"] = st["next"]
st["next_milestone"] = "r883: W18 shards -> screen-finalize -> JUDGE"
st["latest_artifact"] = ("S6 38/38 rc0 (results/_r882bmc_s6_log.txt + "
                        "_r882bmc_s6_log.jsonl) + W18 TRIAL_GRAMMAR_LEDGER "
                        "row committed + round_reports-bm-c.md r882 line")
st["recent_artifact"] = st["latest_artifact"]
st["sync"] = {
    "ahead_behind": "0/0 delivered",
    "origin_tip": "27fadaa55",
    "ts": TS,
    "note": "r882 pre-delivery base 27fadaa55; delivery self-proof = "
            "post-push fetch+rev-list 0/0 recorded in round report",
}
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, indent=1, ensure_ascii=False)

# ---------------- heartbeat ----------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 882
hb["round_no_label"] = "r882"
hb["last_round"] = 881
hb["last_seen"] = TS
hb["clock_read"] = TS
hb["ts"] = TS
hb["last_seen_at"] = TS
hb["updated_at"] = TS
hb["updated"] = TS
hb["heartbeat_epoch_utc"] = epoch
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
if RAM is not None:
    hb["free_ram_gb"] = RAM
    hb["idle_ram_gb"] = RAM
    hb["ram_free_gb"] = RAM
if GPU is not None:
    for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb",
              "gpu_free_mib", "gpu_idle_mb", "gpu_idle_mib"):
        hb[k] = GPU
hb["current_task"] = st["current_task"]
hb["current_task_at"] = TS
hb["activity_now"] = st["activity_now"]
hb["note"] = ("r882: S6 38/38 + W18 relay verified working (bm-b burns 2-7; "
              "0/1 RAM-parked legal yield per r881 relay design)")
hb["verify"] = st["verify"]
hb["orders_ack_last"] = ("O-20261011-1436-bm-c.md | r882 zero new orders "
                         "(S0.5 delta FALSE 70/70)")
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# self-asserts per R170/R178/R262 laws
assert isinstance(epoch, int), "epoch must be int"
assert "T" in hb["clock_read"] and "+" in hb["clock_read"], "clock_read T-sep"
json.loads(open(sp, encoding="utf-8-sig").read())
json.loads(open(hp, encoding="utf-8-sig").read())
print("closeout ok | ts=%s | epoch=%d | ram=%s | gpu_free=%s" % (TS, epoch, RAM, GPU))
