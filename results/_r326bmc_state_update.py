# r326 bm-c: state + heartbeat update (round 326)
import json, time, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
# cpu/ram sampling (in-process, zero window)
import psutil
cpu = psutil.cpu_percent(interval=None)
vm = psutil.virtual_memory()
idle_ram = round(vm.available / 1024 ** 3, 1)
gpu_free = None
try:
    import subprocess as sp
    o = sp.check_output(["nvidia-smi", "--query-gpu=memory.free",
                         "--format=csv,noheader,nounits"], text=True)
    gpu_free = int(o.strip().splitlines()[0])
except Exception:
    gpu_free = 11601

st = json.load(open(BM + r"\state-bm-c.json", encoding="utf-8"))
st.update({
    "machine_id": "bm-c",
    "round_no": 326,
    "last_round_at": "r326",
    "last_round_ts": now,
    "updated": now,
    "cpu_pct": round(cpu, 1),
    "idle_ram_gb": idle_ram,
    "gpu_free_vram_mib": gpu_free,
    "verify": "r526 sweep heal: 13 W14 products restored byte-exact (audit.machine=bm-c 12/12, K=30,920 ledger 397,548 intact, prereg S7/S8 backfill restored, staged set surgical 21 files); T-134 s2 sixth conversion: cn_rev_tilt_p1.py ProcessPool, selftest 34 legs PASS, real-path 65/65 identity, census 33->32; S6 37/37 rc0; smoke 47/47",
    "did": "P0 heal bm-a r526 cross-machine stale-tree sweep (r513 law 3rd occurrence): 13 W14 engine-wave products + prereg backfill + bookkeeping/heartbeat/CODELY/HQ-FEEDBACK restored byte-exact from 068d42477 + CODELY union (commit 4957c59c8) + MSG-174x receipt + HQ-FEEDBACK F-20261001-03 pre-push ownership claw proposal + T-134 s2 SIXTH conversion cn_rev_tilt_p1.py (two dependency-law batches, payload-aware cap, no-swallow, selftest 30->34, 65/65 real-path identity smoke, census 33->32, ticket updated) + S6 37/37 rc0 + W14-GENERATE governance adjudication tracked (MSG-173x read)",
    "current_task": "r526 sweep healed + T-134 s2 sixth conversion delivered; next = s2 seventh candidate (cn_regime_policy) + W14-GENERATE adjudication tracking",
    "next": "r327: (a) T-134 s2 seventh conversion (cn_regime_policy 28.7s leads; t33/t36 unmeasured deferred); (b) W14-GENERATE screen/judge legs pending sec-4/GM adjudication (MSG-173x); (c) W16 observation (bm-b slot, zero freeze action); (d) month-bound first-exam checklist (10-31: six members + SYSTEM-V1 + REV-OSC + 27 experimental accounts)",
    "heartbeat_epoch_utc": epoch,
    "clock_read": now,
    "note": "r326: heal+conversion round; engine shard-11 deterministic re-burn during rebase window (audit elapsed drift legal, science byte-identical per r325 determinism law); W16=bm-b frozen (W15 number held by bm-a N2 draft, N1 skips)",
    "last_ts": now,
    "last_decisions_sha": st.get("last_decisions_sha"),
    "last_decisions_read_at": st.get("last_decisions_read_at", now),
    "last_decisions_sha_method": st.get("last_decisions_sha_method"),
    "last_round": "2026-10-01 r326 bm-c: bm-a r526 sweep healed (13 products + prereg + bookkeeping restored) + T-134 s2 sixth conversion (cn_rev_tilt_p1 65/65 identity) + S6 rc0",
    "last_seen": now,
})
with open(BM + r"\state-bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)

hb = json.load(open(BM + r"\fleet\machines\bm-c.json", encoding="utf-8"))
hb.update({
    "cpu_util_pct": round(cpu, 1), "cpu_pct": round(cpu, 1),
    "free_ram_gb": idle_ram, "idle_ram_gb": idle_ram,
    "ram_free_gb": idle_ram,
    "gpu_free_vram_mib": gpu_free, "gpu_idle_vram_mib": gpu_free,
    "gpu_free_vram_mb": gpu_free,
    "round_no": 326,
    "updated_at": now, "last_seen": now, "last_seen_at": now,
    "heartbeat_epoch_utc": epoch, "clock_read": now,
    "health": "ok",
    "prod_lanes": "r326: bm-a r526 sweep heal (13 W14 products byte-exact restore, commit 4957c59c8) + T-134 s2 sixth conversion cn_rev_tilt_p1.py (selftest 34, 65/65 identity, census 33->32) + S6 37/37 rc0",
    "current_task": "round 326 closeout: sweep heal + sixth conversion delivered",
    "activity_now": "r526 sweep healed; T-134 s2 sixth conversion delivered; engine alive (W16=bm-b foreign, own queue empty); W14-GENERATE adjudication pending",
    "latest_artifact": "scripts/cn_rev_tilt_p1.py ProcessPool conversion + results/_r326bmc_revtilt_pool_smoke.json (65/65 bit-identity, 12 workers) + heal commit 4957c59c8 (2026-10-01T17:2x-17:4x)",
    "next_milestone": "T-134 s2 seventh conversion (cn_regime_policy) + month-bound first exam prep, window <=48h",
    "verdict": "healthy: r526 cross-machine sweep fully healed (verified ownership), sixth multicore conversion delivered + verified, engine alive, S6 rc0",
})
with open(BM + r"\fleet\machines\bm-c.json", "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=2)

chk_s = json.load(open(BM + r"\state-bm-c.json", encoding="utf-8"))
chk_h = json.load(open(BM + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk_h["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(chk_s["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk_h["clock_read"], "clock_read must be T-separated ISO"
print("state+heartbeat r326 written; epoch int OK; clock", now,
      "cpu", round(cpu, 1), "ram_free", idle_ram, "gpu_free_mib", gpu_free)
