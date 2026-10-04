# -*- coding: utf-8 -*-
"""r683 bm-a S7 bookkeeping: state round_no 682->683 + heartbeat (epoch int,
clock T-format) + programmatic json.loads self-proof (r645 law)."""
import json
import time
import datetime
import subprocess

NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
CLOCK = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# --- system stats ---
cpu = ram = gpu = None
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    vm = psutil.virtual_memory()
    ram = round(vm.available / (1024 ** 3), 1)
except Exception:
    pass
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True,
                       text=True, timeout=10)
    gpu = round(int(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

# --- state-bm-a.json ---
SP = "state-bm-a.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 682, f"round_no drift: {st['round_no']}"
st["round_no"] = 683
st["round"] = "r683"
st["last_round"] = "r682"
st["last_round_at"] = CLOCK
st["last_round_ts"] = EPOCH
st["heartbeat_epoch_utc"] = EPOCH
st["current_task"] = ("r683 done: W117 frozen+ignited (107th engine wave, bm-a 34th owned, "
                      "A 277_004..279_003 hops=0 / B 65_050..65_249 hops=1 past-hit restart; "
                      "five faces + prereg DELIVERED 74ec531da; engine verdict=ignited:n1w117 "
                      "shards 6+/12 growing); next: W117 burn completion watch + finalize "
                      "window (W116 bm-b finalize lands first, chain-order FAIL-CLOSED) + "
                      "G2_SLOT_MON stage-2 shortlist prereg (old_032+best_016 per T-163)")
st["did"] = ("r683: S0 fetch+merge zero-UU twice (seat push-race + freeze push-race, r437 "
             "netpath, intersection-empty both) + S0.5 orders 154/154 double-scan zero-unacked "
             "+ D-19 dual MATCH (decisions 4e5be321 / group orders 82a0cef9, Desktop real-path "
             "fetch+git-show raw bytes _r683bma_d19_probe.py) + S1 smoke 48/48 + W117 full "
             "author chain (pre-seat probe rc0 ADMIT A 277_004..279_003/B 65_050..65_249 == "
             "W116 gate-tail projection re-derived + seat MSG-2026-10-04-1535-bma-w117-seat "
             "pushed 380167da7 pre-freeze r565 + prereg PERPETUAL_N1_W117_PREREG.md + banned "
             "gate ADMIT 0 + band gate rc0 dual-window parity + five faces + pf 9/9 + n1 "
             "selftest PASS incl W117 leg + AST PASS + freeze commit 74ec531da DELIVERED + "
             "engine ignition evidence = shards 6+/12 growth face r325 law) + S6 37/37 rc0 "
             "116.6s + self-heal 4/4 + attrition guard CLEAN 4 ledgers")
st["next"] = ("r684+: W117 burn completion watch (engine self-continues each tick) + W117 "
              "finalize window (W116 bm-b finalize lands first -- chain-order FAIL-CLOSED "
              "r307) + G2_SLOT_MON stage-2 shortlist prereg draft (old_032+best_016, T-163 "
              "consumers, banned/D6/seed chain) + fund trio NULLS finalize 10-05..09 watch "
              "(bm-b canonical in-flight V/Q/D of 2000) + 10-06+ next-wave candidate drafting")
st["verify"] = ("S1 smoke 48/48; W117 band gate rc0 legs 0-3 (dual-window derive parity, "
                "own-seat-on-origin, zero conflicts, W118+ projection); pf selftest 9/9 + n1 "
                "selftest PASS incl W117 materializer leg; banned gate ADMIT 0; S6 37/37 rc0 "
                "116.6s (_r683bma_s6_log.txt; dualrun streak face in log); attrition CLEAN "
                "4 ledgers; state strict json.loads proof + heartbeat epoch int/T-sep proof")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
_ = json.load(open(SP, encoding="utf-8"))
assert _["round_no"] == 683 and isinstance(_["heartbeat_epoch_utc"], int)
print("state ok: round_no 682->683, epoch", EPOCH)

# --- heartbeat fleet/machines/bm-a.json ---
HP = "fleet/machines/bm-a.json"
hb = json.load(open(HP, encoding="utf-8"))
hb["machine_id"] = "bm-a"
hb["last_seen"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = CLOCK
hb["last_round"] = "r683"
hb["last_run"] = CLOCK
if cpu is not None:
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
if ram is not None:
    hb["free_ram_gb"] = ram
    hb["idle_ram_mb"] = int(ram * 1024)
if gpu is not None:
    hb["gpu_free_vram_mb"] = int(gpu * 1024)
    hb["gpu_free_vram_mib"] = int(gpu * 1024)
    hb["gpu0_free_vram_gb"] = gpu
hb["health"] = "ok"
hb["verdict"] = ("r683 DONE: W117 frozen + ignited (107th engine wave, bm-a 34th owned, five "
                 "faces + prereg + selftest legs DELIVERED 74ec531da, engine "
                 "verdict=ignited:n1w117 6+/12 shards growing); D-19 dual MATCH, orders "
                 "154/154 double-scan, S6 37/37 rc0 116.6s, smoke 48/48, attrition CLEAN")
hb["current_task"] = ("r683: W117 engine wave author+freeze+ignite chain (A 277_004..279_003 "
                      "arith / B 65_050..65_249 past-hit restart over options actual + W12 A "
                      "band; seat pushed pre-freeze 380167da7; W116 bm-b in-flight upstream "
                      "seat honest note); next = burn watch + finalize after W116 + G2 "
                      "stage-2 prereg")
hb["current"] = ("r683 DONE: W117 frozen+ignited -- 107th engine wave, bm-a 34th owned, five "
                 "faces + PERPETUAL_N1_W117_PREREG + pf 9/9 + n1 selftest PASS incl W117 leg, "
                 "engine verdict=ignited:n1w117 6+/12 shards; D-19 dual MATCH, orders "
                 "154/154, S6 37/37 rc0, smoke 48/48")
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
_ = json.load(open(HP, encoding="utf-8"))
assert isinstance(_["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in _["clock_read"] and " " not in _["clock_read"].split("+")[0], \
    "clock_read must be T-separated (R262 law)"
print("heartbeat ok: epoch", EPOCH, "clock", CLOCK, "cpu", cpu, "ram", ram, "gpu", gpu)
