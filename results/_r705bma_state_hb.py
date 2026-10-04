"""r705 bm-a S7: state-bm-a.json round 704->705 + heartbeat write
(fleet/machines/bm-a.json). Typing laws: heartbeat_epoch_utc must be a
JSON int (python int(time.time())); clock_read ISO8601 with T
separator; per-machine file only (bm-a)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- machine stats (best-effort, honest) ----
cpu = ram_free = None
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1 << 30), 1)
    total_ram = round(psutil.virtual_memory().total / (1 << 30), 1)
    gpu_free = None
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                             "--format=csv,noheader,nounits"],
                            capture_output=True, text=True, timeout=10)
        gpu_free = int(r.stdout.strip().splitlines()[0]) // 1024
    except Exception:
        gpu_free = None
except Exception:
    total_ram = None

# ---- state ----
sp = os.path.join(ROOT, "state-bm-a.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 705
state["round"] = "r705"
state["loop_round"] = int(state.get("loop_round", 0)) + 1
state["updated"] = now_iso
state["last_round"] = "r705"
state["last_round_at"] = now_iso
state["heartbeat_epoch_utc"] = str(epoch)
state["last_heartbeat_epoch_utc"] = epoch
state["current_task"] = ("r705 N2-W15 judge chain step-1: judge-prep "
                         "landed (N_judge=281) + 12 JUDGE-SHARD pool "
                         "entries enrolled; burn window open")
state["did"] = ("r705: orders 154/154 zero-unacked + D-19 decisions "
                "UNCHANGED (755428F8 r704-consumed window) + smoke 48/48 "
                "+ satengine alive rc0 + judge-prep claim/spawn/land "
                "(canon _claim_shard r199 + detached r324, 188s PASS) + "
                "pool flip r489 double-layer + 12-shard enrollment r497 "
                "pattern (391->403) + S6 38/38 rc0 + self-heal 4/4 + "
                "attrition CLEAN 4 ledgers + claw-blocked stale-base push "
                "healed via r501/r507 rebase netpath (18 UU derive "
                "take-fresh + x2 union zero-loss)")
state["last_action"] = ("r705: first push claw-caught (stale base missing "
                        "bm-c r505 4 commits) -> rebase integrate -> push "
                        "DELIVERED 603109d0e; origin pool 403 with 12 "
                        "judge shards; MSG-0125 receipt landed")
state["last_round_ts"] = now_iso
state["next"] = ("r706: 12 judge shard burns watch (autofill "
                "claim-to-saturation in flight; checkpoint resume "
                "faces) -> judge-finalize when 12/12 done (ledger "
                "PERPETUAL-N2-W15-JUDGE + prereg sec.7/8 backfill + "
                "r668 pool double-flip same window); W3 judge bm-c probe "
                "verify (ETA 02:00 passed-check); trio NULLS finalize "
                "watch 10-05..09 (bm-b canonical); tailscale bm-c CEO "
                "one-click pending (roster flip = bm-a window)")
state["verify"] = ("smoke 48/48; push_verify DELIVERED 603109d0e "
                   "(behind=0 ahead=0 post-push fetch; origin ls-tree "
                   "judge_state+enroll 2/2); attrition CLEAN 4 ledgers; "
                   "claws parity PASS; dual run scheduled tasks rc0")
json.dump(state, open(sp, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)

# ---- heartbeat ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["last_heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cores"] = 32
hb["cpu_cores"] = 32
if ram_free is not None:
    hb["free_ram_gb"] = ram_free
    hb["ram_free_gb"] = ram_free
    hb["idle_ram_gb"] = ram_free
if total_ram:
    hb["total_ram_gb"] = total_ram
if gpu_free is not None:
    hb["gpu_free_vram_mb"] = gpu_free * 1024
    hb["gpu_idle_vram_mb"] = gpu_free * 1024
    hb["gpu_idle_vram_gb"] = gpu_free
hb["last_round"] = "r705"
hb["round_no"] = 705
hb["loop_round"] = "705"
hb["current_task"] = state["current_task"]
hb["verdict"] = ("GREEN: N2-W15 judge chain step-1 landed (N_judge=281, "
                 "12 shards enrolled, burn window open); engine alive; "
                 "board clear; golden-week judge-burn phase")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)

# ---- typing self-verify (R170/R178/R262 laws) ----
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), \
    "F7: epoch must be JSON int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], \
    "F5: clock_read must use T separator"
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 705
print(f"state r705 + heartbeat written; epoch={epoch} int-proof OK; "
      f"clock={now_iso}; cpu={cpu}% ram_free={ram_free}GB")
