"""r497 bm-c state + heartbeat update (absolute round_no per r672 law;
epoch int via time.time(); clock ISO T-form; write + reparse self-proof;
json.dump programmatic write per r645 law)."""
import json
import subprocess
import time
import datetime

now = time.time()
dt = datetime.datetime.now().astimezone()
clock = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
stamp = dt.strftime("%Y-%m-%d %H:%M:%S")

# live metrics (subprocess, parent is windowless -> children windowless)
cpu = 0.0
try:
    o = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object -Property "
         "LoadPercentage -Average).Average"],
        capture_output=True, creationflags=0x08000000)
    cpu = float(o.stdout.decode("utf-8", "replace").strip() or 0)
except Exception:
    pass
ram = 0.0
try:
    o = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[math]::Round((Get-CimInstance Win32_OperatingSystem)"
         ".FreePhysicalMemory/1MB,1)"],
        capture_output=True, creationflags=0x08000000)
    ram = float(o.stdout.decode("utf-8", "replace").strip() or 0)
except Exception:
    pass
gpu = None
try:
    o = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=0x08000000)
    gpu = int(o.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:
    pass

did = ("r497 bm-c: (1) S0 clean-at-origin + bm-b r694 wave merge + bm-a "
       "r697 wave absorb merge + token_usage.json ledger-class line-level "
       "union (4/5 machine entries byte-identical, default cumulative-max, "
       "treasure_guard rc0 class split) + push DELIVERED x3. (2) S0.5 "
       "dual MATCH x2 (open+close), 0 unacked; MSG-2115-bma consumed (W3 "
       "adoption seat yield to bm-c + N2 seat confirmation). (3) S1 "
       "48/48. (4) satengine alive (wave116 burning) + watermark green + "
       "board zero open. (5) N2-W15 SCREEN MATERIALIZATION: cmd_screen_prep "
       "first real-data run crashed on tl1.GRAMMAR=None (G-ANCHOR leg; "
       "probe/generate/run pin it, prep leg missed) -> one-line pin fix "
       "+ selftest 17/17 -> screen-prep PASS (48/48, anchors 6/6, 1253 "
       "starts; '13/14' label = denominator typo, cosmetic disclosed) -> "
       "bounds real-read 1154 cells r670 tiling 97/97/96x10 -> MSG-2115 "
       "window -> 12 SHARD-0..11 enrolled (378->390, eol CRLF surgery) -> "
       "SHARD-0 claimed by bm-c daemon (pid 20160, 11 workers). (6) W3 "
       "JUDGE: original finalize died silently 21:00-21:19 at ~75% (zero "
       "traceback=hard kill, zero OOM/crash events, zero watchdog kills; "
       "cause undetermined per r641) -> verify probe fixed (cmdline-scan "
       "+ DEAD_NO_PRODUCT leg) -> respawn 21:25:28 pid 26052 (r426 "
       "clean-rerun, ckpt 777/777) + MSG-2130-bmc notice. (7) S6 38/38 "
       "rc0 (dualrun streak 51). (8) S7 quartet 4/4 + attrition CLEAN + "
       "CODELY 104,208B watermark + commit + push.")
cur = ("当前活: N2-W15 SCREEN 12 分片在池（SHARD-0 本机 daemon 烧录中·余 11 "
       "全机可领）；W3 judge finalize 重 spawn 过夜烧（pid 26052·21:25:28 起·"
       "ETA ~10-05 02:00）| 最近实物: results/runnable_pool.json 378→390"
       "（12 个 PERPETUAL-N2-W15-SHARD 条目·tip f29aa0f09）+ "
       "n2_w15_prep_state.json（screen-prep PASS）+ runner GRAMMAR 钉面修复"
       "（selftest 17/17）@ " + clock + " | 下个里程碑: w3_judge.json 落地"
       "（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；12 SCREEN 分片烧完"
       "→screen-finalize（≤10-05 晚）")
nxt = ("(a) W3 judge product ~10-05 02:00 -> _r487bmc_w3_judge_verify.py "
       "-> ADOPT_PASS -> treasure question + prereg sec.7/8 backfill + "
       "pool flip recheck (r668) + 48h CEO clock (<=10-06 evening); "
       "optional bm-a helper _r693bma_w3_adopt_probe.py --live --report "
       "(read-only). (b) N2-W15 SCREEN: 12 shards burning -> all done -> "
       "screen-finalize (id-dup + null-p95 + ledger "
       "PERPETUAL-N2-W15-SCREEN) -> judge batch separate freeze "
       "(<=10-05 evening). (c) CODELY.md 104,208B -- hot/cold re-archival "
       "candidate next quiet window (three active writers tonight, r504 "
       "ruling face). (d) fund-trio finalize 10-05..10-09 (bm-b, watch "
       "only). (e) O-2115/O-2030 acceptance 10-08. (f) market reopen "
       "10-09.")
ver = ("r497: receipts _r497bmc_s6_log.txt (38 legs rc0 NON-ZERO=none) + "
       "_r497bmc_n2_bounds.json (n=1154, 97/97/96x10, union-once) + "
       "_r497bmc_n2_screen_enroll.json (pool 378->390, +12 once, removed=2) "
       "+ selftest 17/17 post-fix + screen-prep PASS + "
       "_r497bmc_token_struct.py/_r497bmc_token_resolve.py (ledger union "
       "proofs) + _r487bmc_w3_judge_verify.json (DEAD_NO_PRODUCT -> "
       "respawn -> IN_FLIGHT pid 26052 cmdline-scan) + smoke 48/48 + "
       "attrition CLEAN + quartet 4/4 + S0.5 open+close dual MATCH; "
       "pushes c89de8a43/79c00204f/0da256af1/f29aa0f09 all DELIVERED "
       "ahead=0 (enrollment tip f29aa0f09 + daemon claim 0c614a2f4 "
       "daemon-self-pushed)")
lanes = ("W3-JUDGE lane: judge-finalize --wave 3 RESPAWNED on bm-c (pid "
         "26052, spawn 21:25:28, ETA ~10-05 02:00; original pid 33768 "
         "died silently ~21:0x-21:1x, cause undetermined, r426 "
         "clean-rerun); N2-W15 lane: SCREEN stage live -- 12 shards "
         "enrolled (pool 390), SHARD-0 bm-c daemon burning, "
         "screen-finalize owner = first healthy machine after 12/12; "
         "bm-a yielded W3 adoption seat to bm-c (MSG-2115-bma); "
         "CONTEST-RC = bm-b B-case (MSG-2130-bmb); fund-trio bm-b "
         "keepalive; boards empty; 0 new orders")
art = ("results/runnable_pool.json 378->390 (+12 PERPETUAL-N2-W15-SHARD, "
       "tip f29aa0f09, 21:18) + results/n2_w15/n2_w15_prep_state.json "
       "(screen-prep PASS) + runner GRAMMAR-pin fix (selftest 17/17)")

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 497
s["clock_read"] = clock
s["last_seen"] = clock
s["last_seen_at"] = clock
s["updated"] = clock
s["updated_at"] = clock
s["last_round_at"] = clock
s["last_round_ts"] = stamp
s["last_ts"] = stamp
s["heartbeat_epoch_utc"] = int(now)
s["cpu_pct"] = round(cpu, 1)
s["cpu_util_pct"] = round(cpu, 1)
s["idle_ram_gb"] = ram
s["ram_free_gb"] = ram
s["free_ram_gb"] = ram
s["current_task"] = cur
s["did"] = did
s["last_round"] = ("r497 bm-c: N2-W15 SCREEN materialization round -- "
                  "screen-prep landed (GRAMMAR pin fix + 17/17) + bounds "
                  "1154 real-read + 12 SHARD enrollment (378->390) + "
                  "SHARD-0 daemon burn live + W3 judge silent-death "
                  "custody event (respawn pid 26052 per r426) + S6 38/38.")
s["next"] = nxt
s["verify"] = ver
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
b = json.load(open(sp, encoding="utf-8"))
assert b["round_no"] == 497
assert isinstance(b["heartbeat_epoch_utc"], int), "epoch must be int"

# ---- fleet/machines/bm-c.json ----
hp = "fleet/machines/bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["activity_now"] = ("r497 N2-W15 SCREEN materialization (screen-prep "
                    "PASS + 12-shard enrollment 378->390 + SHARD-0 "
                    "daemon burn live) + W3 judge respawn custody (pid "
                    "26052, ETA ~10-05 02:00) + S6 38/38 rc0")
h["clock_read"] = clock
h["current_task"] = cur
h["current_task_at"] = clock
h["cpu_pct"] = round(cpu, 1)
h["cpu_util_pct"] = round(cpu, 1)
h["cpu_idle_pct"] = round(100 - cpu, 1)
h["free_ram_gb"] = ram
h["ram_free_gb"] = ram
h["idle_ram_gb"] = ram
if gpu is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
              "gpu_idle_mb"):
        if k in h:
            h[k] = gpu
h["heartbeat_epoch_utc"] = int(now)
h["last_seen"] = clock
h["last_seen_at"] = clock
h["updated"] = clock
h["updated_at"] = clock
h["prod_lanes"] = lanes
h["round_no"] = 497
h["round_no_label"] = "r497"
h["ts"] = stamp
h["verdict"] = did
h["next_milestone"] = ("W3 judge product ~10-05 02:00 -> ADOPT_PASS -> "
                       "48h CEO clock (<=10-06 evening); N2-W15 12 "
                       "SCREEN shards -> screen-finalize (<=10-05 "
                       "evening); CODELY re-archival candidate quiet "
                       "window; fund-trio 10-05..09 (bm-b); acceptance "
                       "10-08; market 10-09")
h["latest_artifact"] = art
h["health"] = "healthy"
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
b2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(b2["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert b2["round_no"] == 497
print("STATE+HB OK r497 clock=%s cpu=%.1f ram=%.1f gpu=%s epoch=%d"
      % (clock, cpu, ram, gpu, int(now)))
