# -*- coding: utf-8 -*-
"""r341 bm-b round-close: state.json + round report line + heartbeat,
fresh-timestamp law (r96: epoch & clock_read derived from ONE time read,
JSON int epoch, T-separator ISO), self-verify on write."""
import json
import subprocess
import time

T0 = time.time()
EPOCH = int(T0)  # single fresh read, both fields derive from it
CLOCK = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime(T0))
TS = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(T0))

# ---- resource sample (fresh at write) ----
cpu_pct, free_gb, total_gb = None, None, None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / 2**30, 1)
    total_gb = round(vm.total / 2**30, 1)
except Exception as e:  # keep prior heartbeat values, honest carry
    print("psutil unavailable:", e)
gpu_free_mb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    gpu_free_mb = int(r.stdout.strip().splitlines()[0])
except Exception as e:
    print("nvidia-smi unavailable:", e)

# ---- round text ----
DID = ("r341-A predecessor legacy adoption + network-dead local mode: killed "
       "r341-A session (20:20 fire, died 20:36-20:40, fetch-hang same death "
       "family, inferred) had already delivered census_fusion_s2.py UNC "
       "incremental-flush mirror fix (r340 pitlaw W2-B mirror item) + full "
       "S6 chain 30/30 rc=0 (20:34:53-20:36:22) -- adopted not rebuilt "
       "(anti-dup law): hermetic verify _r341bmb_unc_flush_verify.py 3/3 "
       "PASS then targeted commit b2a36f94 (21 files: fix+verify+driver+S6 "
       "products+tick tails); this session then hit live fetch 5-min "
       "zero-output hang -> auto-cancel (zero orphan git/lock residue) + "
       "proxy 7897->github probe FAIL -> S0 network-dead local mode (r340 "
       "precedent): pull --rebase / escape-fold infeasible this round, push "
       "skipped, local-ahead chain carries to r342 S0 fold; S0.5 dual-scan "
       "orders 96/96 zero-diff + P-32 decisions 3-path probe absent honest "
       "no-op (r104/r107) + MSG-2010 (bm-b->bm-a) unread inbox = addressed "
       "to bm-a, left for its consumption; S1 smoke 25/25; S2 dual boards 0 "
       "open (python rescan; PS ConvertFrom-Json GBK misdecode on T-83 = "
       "display artifact not corruption); S6 = adopted predecessor chain run "
       "30/30 rc=0 + 3 new-bar-gated legal skips (Sunday cutoff 09-24, next "
       "bar Mon 09-28 15:30); S4 zero append (fetch-hang = r340-recorded "
       "precedent, no new pitlaw); S7: schtasks both tasks in-register "
       "(Loop Running=this session / Watchdog Ready) + pre-commit claw "
       "CR-normalized identical + state r341 + heartbeat self-verified; "
       "W2-A burn healthy: 4 workers ~17.5k CPUsec each (~89%/core, RAM "
       "1.9-4.5GB), ETA window to ~21:40")
VERDICT = "green"
NEXT = ("r342 S0 fold mainline (fetch -> pull --rebase -> canonical resolve, "
        "autofill_state UU expected -> push main -> GC escape branch "
        "machine/bm-b-r340 -> verify origin/main contains ce11fad7+b2a36f94 "
        "chain); W2-A finalize harvest window ~21:40+ -> r312 done-flip pool "
        "face + T-86 bm-a ticket receipt; Mon 09-28: 09:15 T-91 s3 auto-fire "
        "(SIG/BARS-09-28 replay) + 15:30 T-87 astock first increment + "
        "new-bar full chain (preflight 8/8 green); 10-01 monthly trio + "
        "REGIME_GUARD v3 date gate")

REPORT = (
    CLOCK + " | round 341 bm-b | dept:工程+舰队 | "
    "水位=绿：red=false@20:30:20 lane healthy（py 28-30%=W2-A census burn "
    "合法占用·verdict 面如实） | did: " + DID +
    " | 验证证据=b2a36f94 + _r341bmb_unc_flush_verify.py 3/3 PASS 断言面 + "
    "_r341bmb_s6.log 30x rc=0 + smoke 25/25 | 下轮: " + NEXT)

# ---- state.json (bm-b file, indent=1, LF) ----
with open("logs/iteration-loop/state.json", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 341
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["last_round_ts"] = CLOCK
st["last_result"] = "ok"
st["current_task"] = ("r341 closed: r341-A legacy adoption (UNC mirror fix "
                      "3/3 PASS) + S6 30/30 adopted + network-dead local "
                      "mode, local-ahead for r342 fold")
st["updated_at"] = CLOCK
st["last_seen"] = CLOCK
st["ts"] = TS
st["last_task"] = "r341: UNC runner incremental-flush mirror fix adopted + S6 chain adopted + local mode"
with open("logs/iteration-loop/state.json", "w", encoding="utf-8",
          newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---- round report line (append, match existing EOL) ----
raw = open("logs/iteration-loop/round_reports.md", "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
with open("logs/iteration-loop/round_reports.md", "ab") as fh:
    fh.write(REPORT.encode("utf-8") + eol)

# ---- heartbeat fleet/machines/bm-b.json (preserve keys, update values) ----
with open("fleet/machines/bm-b.json", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH          # JSON int, smoke F7
hb["clock_read"] = CLOCK                   # T-separator, smoke F7
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 16
if total_gb:
    hb["total_ram_gb"] = total_gb
if free_gb:
    hb["free_ram_gb"] = free_gb
    hb["idle_ram_gb"] = free_gb
    hb["idle_ram_mb"] = int(free_gb * 1024)
    hb["free_ram_mb"] = int(free_gb * 1024)
if gpu_free_mb:
    hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
    hb["gpu_free_vram_mb"] = gpu_free_mb
    hb["gpu_idle_vram_mb"] = gpu_free_mb
if cpu_pct:
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_pct"] = cpu_pct
hb["round_no"] = 341
hb["round"] = 341
hb["loop_round"] = 341
hb["verdict"] = "healthy"
# orders_ack unchanged (96, zero new orders this round) -- carried as-is
with open("fleet/machines/bm-b.json", "w", encoding="utf-8",
          newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---- self-verify (R170/R178/R262 law) ----
hb2 = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"], \
    "clock_read must be T-separated ISO"
st2 = json.load(open("logs/iteration-loop/state.json", encoding="utf-8"))
assert st2["round_no"] == 341
print("r341 close OK | epoch=%d clock=%s cpu=%s free_ram=%s gpu_free=%s"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], cpu_pct, free_gb,
         gpu_free_mb))
