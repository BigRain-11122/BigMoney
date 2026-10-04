"""r706 bm-a S7: state-bm-a.json round 705->706 + heartbeat write
(fleet/machines/bm-a.json) + round report line append + CODELY pitlaw
row append. Typing laws: heartbeat_epoch_utc JSON int; clock_read
ISO8601 T separator; per-machine files only (bm-a)."""
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
cpu = ram_free = total_ram = gpu_free = None
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1 << 30), 1)
    total_ram = round(psutil.virtual_memory().total / (1 << 30), 1)
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        gpu_free = int(r.stdout.strip().splitlines()[0]) // 1024
    except Exception:
        gpu_free = None
except Exception:
    pass

# ---- state ----
sp = os.path.join(ROOT, "state-bm-a.json")
state = json.load(open(sp, encoding="utf-8"))
state["round_no"] = 706
state["round"] = "r706"
state["loop_round"] = int(state.get("loop_round", 0)) + 1
state["updated"] = now_iso
state["last_round"] = "r705"
state["last_round_at"] = now_iso
state["heartbeat_epoch_utc"] = str(epoch)
state["last_heartbeat_epoch_utc"] = epoch
state["current_task"] = ("r706 salvage-adoption closeout + judge burn "
                         "watch: r705 dead-session S7 bookkeeping adopted "
                         "and pushed (dd0f33078); N2-W15 judge 12-shard "
                         "pool burn in flight via autofill (claims "
                         "0-4of12, runners alive); W3 judge bm-c probe "
                         "ETA 02:00 watch")
state["did"] = ("r706: S0 adoption commit dd0f33078 DELIVERED (r705 "
                "predecessor died post-bookkeeping pre-commit; targeted "
                "add, zero daemon faces swallowed) + orders 154/154 "
                "zero-unacked dual sweep + D-19 MATCH via canon "
                "d19_check.py (755428F8; hand-rolled PS hash false-"
                "CHANGED caught in-round, canon tool re-check) + smoke "
                "48/48 + satengine alive rc0 idle + board 0 open + "
                "S6 38/38 rc0 (CEO panels REPORT/LIVE-2026-10-05 "
                "regenerated) + self-heal 4/4 + attrition CLEAN 4 "
                "ledgers (healed 4+1)")
state["last_action"] = ("r706: adoption commit dd0f33078 pushed over "
                        "daemon tick waves (origin advanced under us, "
                        "push fast-forwarded cleanly); judge shard "
                        "checkpoint lands watched next round")
state["last_round_ts"] = now_iso
state["next"] = ("r707: judge 12-shard burn watch -> judge-finalize when "
                "12/12 (ledger PERPETUAL-N2-W15-JUDGE + prereg sec.7/8 "
                "backfill + r668 pool double-flip same window); W3 "
                "judge bm-c --live probe -> ADOPTION_READY -> closeout "
                "commit + CEO 48h pendulum; moneyflow fuse self-heal "
                "watch -> panel -> IC prereg; trio NULLS finalize watch "
                "10-05..09 (bm-b canonical); tailscale bm-c CEO "
                "one-click pending")
state["verify"] = ("smoke 48/48; push DELIVERED dd0f33078 (behind=0 "
                   "post-push fetch verify next commit); D-19 MATCH "
                   "canon; attrition CLEAN; claws parity installed; "
                   "loop pin8 no-op + watchdog re-registered")
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
hb["last_round"] = "r706"
hb["round_no"] = 706
hb["loop_round"] = "706"
hb["current_task"] = state["current_task"]
hb["verdict"] = ("GREEN: judge 12-shard burn in flight (daemon "
                 "claim-to-saturation), board clear, S6 38/38, engine "
                 "alive; golden-week judge-burn phase")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False,
          indent=1)

# ---- typing self-verify (R170/R178/R262 laws) ----
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), \
    "F7: epoch must be JSON int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], \
    "F5: clock_read must use T separator"
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 706
print(f"state r706 + heartbeat written; epoch={epoch} int-proof OK; "
      f"clock={now_iso}; cpu={cpu}% ram_free={ram_free}GB gpu={gpu_free}GB")
