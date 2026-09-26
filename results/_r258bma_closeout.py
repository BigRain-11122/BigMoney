# -*- coding: utf-8 -*-
"""R258 closeout: heartbeat update (epoch int law R170/R178) + round-report
addendum line + T-82 window note. Faces: LF, indent 1, no BOM, no end-newline
(heartbeat); round report CRLF."""
import io
import json
import subprocess
import time

# ---- CPU/RAM/GPU sample (best-effort, zero popups) ----
cpu = 8.0
free_ram_gb = 55.0
gpu_free = 5.5
try:
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object -Property "
         "LoadPercentage -Average).Average; "
         "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        capture_output=True, timeout=20).stdout.decode()
    parts = out.strip().split("\n")
    cpu = float(parts[0])
    free_ram_gb = float(parts[1])
except Exception:
    pass

epoch = int(time.time())
clock = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

PATH = r"fleet\machines\bm-a.json"
d = json.load(io.open(PATH, encoding="utf-8"))
d["machine_id"] = "bm-a"
d["last_seen"] = time.strftime("%Y-%m-%d %H:%M:%S")
d["current_task"] = "T-73 s2 slice-E style-rotation next + T-82 deep-shard window + fleet maintenance"
d["cpu_cores"] = 32
d["cpu_pct"] = cpu
d["free_ram_gb"] = free_ram_gb
d["gpu_free_vram_gb"] = gpu_free
d["verdict"] = ("GREEN R258 slice-D closed: lowvol all-era law + size "
                "regime-map (2017-2020 flip) + dividend defensive face; "
                "osh-provenance defect self-caught at sidecar stage "
                "(snapshot-ffilled-back); push-collision 13-UU resolved per "
                "skill zero-loss; no fabricated busywork O-1137")
d["orders_ack"] = d.get("orders_ack", "")
d["heartbeat_epoch_utc"] = epoch          # python int -> JSON int (R170/R178)
d["clock_read"] = clock
d["task"] = ("R258 done: slice-D SIZE/LOWVOL/DIVIDEND factor-history closed "
             "(digest+artifact+ticket r258); next = s2 slice-E style-rotation "
             "= last empirical s2 topic; 09-28 new-bar chain; 10-01 trio; "
             "T-70 verdict 10-09")
d["round_no"] = 258
io.open(PATH, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1))

# self-verify epoch is JSON int (smoke F7 face)
chk = json.load(io.open(PATH, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written: epoch", epoch, "int-verified, clock", clock)

# ---- round report addendum (collision record per skill leave-trace law) ----
LINE = (
    "2026-09-26 17:1x | R258 addendum | S7 push rejected same-window (bm-b 43b88ac8 16:51:18 < bm-a 17:01 per fleet/README SS4 = bm-a yields) -> pull --rebase -> 13 UU (11 classified + 2 UNKNOWN daily_report pair): resolver results/_r258bma_resolve{,2}.py per skill recipes = compute_audit history union 204|201 -> 205 ts-asc zero-loss + latest take-new by nested latest.ts (mine 16:59:00 > bm-b 16:45:44; pass-1 root-ts-absent face self-caught, fields initially took stale ours, fixed in pass-2 before continue); regime_state history union 2|2->2 identity-dedupe + fields take ts 16:59:21 mine; autofill launches union 50|50->50 asc cap50 (bm-b CN-REGIME-POLICY-P1 relaunch row preserved via ours-first union) + last_tick take mine 17:00:02 > 16:40:01; 7 snapshots + dashboard pair (meta.generated_at probe, R257 face) + daily_report pair (r242 generated_at governs, md same-side whole bytes) all take-theirs = my 16:59-17:00 S6 runs fresher than bm-b 16:46-47; parse-verify before every add (r185); rebase landed d8fb04d4 -> amended 98a54985 with resolvers -> pushed clean"
)
with io.open(r"logs\iteration-loop\round_reports-bm-a.md", "a",
             encoding="utf-8", newline="") as f:
    f.write(LINE + "\r\n")
print("addendum line appended")
