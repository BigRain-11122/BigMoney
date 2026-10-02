"""r374 bm-c S7 bookkeeping: state round bump 373->374, heartbeat refresh
(epoch int + T-separated clock, R170/R178/R262 laws), round report append.
Hardware sampled live: psutil (prime first per r319 law), nvidia-smi silent."""
import datetime
import json
import os
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
NO_WIN = 0x08000000

# --- hardware sample (r319 law: prime both faces before reading) ---
try:
    import psutil
    psutil.cpu_percent(interval=None)
    _ = [p.info.get("cpu_percent") for p in psutil.process_iter(["cpu_percent"])]
    time.sleep(0.5)
    machine_cpu = round(psutil.cpu_percent(interval=0.4), 1)
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / (1024 ** 3), 1)
except Exception:
    machine_cpu, free_ram_gb = None, None
gpu_free_mib = None
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=NO_WIN, timeout=10)
    if r.returncode == 0 and r.stdout.decode("utf-8", "replace").strip():
        gpu_free_mib = int(r.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:
    gpu_free_mib = None

# --- W99 burn progress (product growth face, r325 law) ---
w99_dir = os.path.join(REPO, "results", "p2cal_ext", "n1_w99")
w99_shards = len([f for f in os.listdir(w99_dir) if f.endswith(".json")]) \
    if os.path.isdir(w99_dir) else 0

# --- state-bm-c.json (preserve keys, update round faces) ---
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 374
st["last_round_at"] = "r374"
st["last_round_ts"] = now.strftime("%m/%d/%Y %H:%M:%S")
st["updated"] = iso
st["cpu_pct"] = machine_cpu
st["idle_ram_gb"] = free_ram_gb
if gpu_free_mib is not None:
    st["gpu_free_vram_mib"] = gpu_free_mib
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = iso
st["last_decisions_read_at"] = now.strftime("%m/%d/%Y %H:%M:%S")
st["verify"] = (
    "r374: W99 FREEZE five-face delivered (EIGHTY-NINTH engine wave by "
    "machine-derive engine_owner rows 88+candidate, bm-c 29th owned; bands "
    "A 241_004..243_003 arithmetic CLEAN hops 0 + B 58_551..58_750 "
    "D-20261002-05 pinned-skip hops 2 past SEED_REGISTRY in-band hits "
    "[58_500 mf_ic_p1, 58_550 sina_construct_p1]; seat MSG-20261002-1625-bmc "
    "pre-pushed fed0b4054 per r565; anchor=W94 finalize chain head 571,348 "
    "K=204,720 per r576 anchor-roll; banned gate ADMIT 0 matched; freeze "
    "f2191688c FIX-A/B/C pure insertion +29/+187/+2 + AST gate; pf selftest "
    "9/9 + n1 default-wave selftest PASS W99 leg live) + engine v0.4 "
    "mtime-reload self-ignition (W99 %d/12 shards burned, burns_active, "
    "product growth proof r325; D-20261002-03 no-restart face live) + S6 "
    "37/37 rc0 (dualrun streak 50/3 zero-drift, WM green holiday-legal, "
    "attrition CLEAN, daily report + CEO live page written) + smoke 47/47 "
    "+ orders 143/0 double-scan + D-19 937A373D MATCH + self-heal 4/4 "
    "(loop pin=5, watchdog, both claws MATCH)"
) % w99_shards
st["did"] = ("r374: W99 freeze (five faces + gate ADMIT + seat MSG + prereg "
             "anchor W94) + engine self-ignited W99 burn + S6 all-green + "
             "seat-MSG archive-scope pit appended")
st["current_task"] = (
    "W99 burn in flight on local engine (finalize gated: upstream W95 bm-b "
    "+ W96 bm-a + W97 bm-b + W98 bm-a finalizes pending, FAIL-CLOSED r307); "
    "T-144(c) engine/data/protocol + flow-sinking due 10-07; T-143 "
    "month-exam prep 10-29; month-boundary first exam 10-31")
st["next"] = (
    "(r375)(a) watch W99 12/12 burn completion (engine autonomous; "
    "finalizer waits upstream W95..W98 finalize landings -- chain order "
    "prev derive at run time, one-pass r538 law); (b) T-144(c) "
    "engine-domain split (r369/r373 split-tool paradigm, content-anchored, "
    "LF-blob accounting); (c) T-143 month-exam prep (10-29); (d) T-131 "
    "follow-up slices; (e) month-boundary first exam 10-31")
st["note"] = (
    "r374 pit: seat MSG lifecycle = inbox (published) -> processed/ "
    "(archived after consumption); gate leg0c upstream-seat checks must "
    "scan inbox+processed UNION (bm-a W98 gate template leg0c was "
    "inbox-only -- passed only because the upstream seat MSG was not yet "
    "archived at its run; r374 W99 gate hit the archived case, fixed "
    "in-place). Seat MSG filename timestamps must come from Get-Date, not "
    "estimation (this round's MSG-...-1625- was actually pushed ~16:08; "
    "unique-ID face only, zero science impact, honestly disclosed).")
st["last_ts"] = iso
st["last_round"] = (
    "2026-10-02 r374 bm-c: W99 FREEZE (five faces, A arithmetic + B "
    "D-20261002-05 pinned-skip 58_551..58_750, gate ADMIT rc0, banned "
    "ADMIT 0, seat pre-push r565) + engine self-ignition + S6 all-green + "
    "smoke 47/47 + orders 143/0")
st["last_seen"] = iso
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- fleet/machines/bm-c.json heartbeat (preserve ack list) ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "last_seen": iso,
    "updated_at": iso,
    "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "round_no": 374,
    "cpu_util_pct": machine_cpu,
    "cpu_pct": machine_cpu,
    "cores": 32,
    "cpu_cores": 32,
    "free_ram_gb": free_ram_gb,
    "ram_free_gb": free_ram_gb,
    "idle_ram_gb": free_ram_gb,
    "gpu_free_vram_mib": gpu_free_mib if gpu_free_mib is not None
    else hb.get("gpu_free_vram_mib"),
    "gpu_idle_vram_mib": gpu_free_mib if gpu_free_mib is not None
    else hb.get("gpu_idle_vram_mib"),
    "health": "ok",
    "current_task": ("r374 done: W99 frozen (five faces) + engine "
                     "self-ignited, burn in flight; T-144(c) engine split "
                     "due 10-07"),
    "verdict": ("healthy: W99 freeze full pre-flight (seat pre-push r565, "
                "gate ADMIT rc0 A hops 0 / B pinned-skip hops 2, banned "
                "ADMIT 0, FIX-A/B/C pure insertion, AST gate, pf 9/9 + n1 "
                "default-wave PASS) + engine v0.4 mtime-reload "
                "self-ignition live (product growth) + S6 37/37 rc0 + "
                "smoke 47/47 + orders 143/0 + attrition CLEAN"),
    "activity_now": ("r374: W99 FREEZE five-face + engine self-ignited "
                     "(%d/12 shards) + S6 37/37 rc0 + smoke 47/47 + orders "
                     "143/0 double-scan + D-19 MATCH + self-heal 4/4"
                     % w99_shards),
    "latest_artifact": ("W99 freeze package (commit f2191688c, "
                        "2026-10-02T16:12: research/PERPETUAL_N1_W99_PREREG.md "
                        "+ canon W99 row + pf N1_BANDS[99] + n1 "
                        "WAVE_CONFIGS[99] + selftest W99 leg; bands A "
                        "241_004..243_003 + B 58_551..58_750) + "
                        "results/p2cal_ext/n1_w99/ shards %d/12"
                        % w99_shards),
    "next_milestone": ("W99 finalize one-pass once upstream W95..W98 "
                       "finalizes land (window <=48h; FAIL-CLOSED r307 "
                       "chain order); T-144(c) engine-domain split 10-07; "
                       "month-boundary first exam 10-31"),
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report append (fixed-field line) ---
rp = os.path.join(REPO, "round_reports-bm-c.md")
line = (
    "%s | r374 | W99 FREEZE five-face delivered (EIGHTY-NINTH wave, bm-c "
    "29th owned; A 241_004..243_003 arithmetic CLEAN + B 58_551..58_750 "
    "D-20261002-05 pinned-skip hops 2 past SEED_REGISTRY [58_500 mf_ic_p1, "
    "58_550 sina_construct_p1]; seat MSG-20261002-1625-bmc pre-pushed "
    "fed0b4054 r565; anchor=W94 finalize 571,348/K=204,720 r576; banned "
    "ADMIT 0; FIX-A/B/C pure insertion; pf 9/9 + n1 default-wave PASS) + "
    "engine mtime-reload self-ignition (%d/12 shards, product growth r325) "
    "+ S6 37/37 rc0 + smoke 47/47 + orders 143/0 both scans + D-19 MATCH "
    "+ self-heal 4/4 | 未达 origin commit 数=0 (post-push fetch verify); "
    "next: (r375) W99 burn watch + finalize gate (upstream W95..W98 "
    "pending), T-144(c) engine split 10-07, T-143 prep 10-29, month exam "
    "10-31\n" % (iso, w99_shards))
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)

# --- int-epoch + clock self-verify (R170/R178/R262 laws) ---
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
st2 = json.load(open(sp, encoding="utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"
assert isinstance(json.loads(json.dumps(hb2["heartbeat_epoch_utc"])), int)
print("STATE_OK round_no=374 epoch=%d clock=%s cpu=%s ram=%s gpu=%s w99=%d/12"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], machine_cpu,
         free_ram_gb, gpu_free_mib, w99_shards))
