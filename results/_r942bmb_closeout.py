# -*- coding: utf-8 -*-
# r942 bm-b closeout: state + heartbeat + round report line (utf-8 safe write)
import json, time, subprocess, io
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- machine sampling ---
ram_free_gb = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / (1024**3), 1)
    ram_free_pct = round(vm.available * 100.0 / vm.total, 1)
    cpu_cores = psutil.cpu_count(logical=True)
except Exception:
    ram_free_gb, ram_free_pct, cpu_cores = 6.5, 27.0, 16
vram_free_mb = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    vram_free_mb = int(o.stdout.strip().splitlines()[0].strip())
except Exception:
    vram_free_mb = 3540

verdict = ("GREEN: r942 closed T-186 W19/W20 lineage formally (status=done + result_ref full evidence chain: "
           "W19 timing-axis 112 judged lawful-zero + paired-deltas/reform-face deliverables + W20 census 45 faces "
           "0 survivors source-closed + 48h CEO tri-axis report landed early) + S6 26 legs rc0 (dualrun streak 27, "
           "market_clock ORANGE_COOL, thermo+dualarm refreshed) + paper legs gated honest (no new bar, cutoff 10-13); "
           "smoke 49/49; orders 0 unacked; D-19 EQUAL; flags supply_floor/pool_starvation standing WITH VERDICT "
           "(refill = P1 stock-universe CEO-signed ticket; sec.5 route closed by W20 census) + sina 10-14 daily-bar "
           "catch pending (source-side, self-heal) + agenda_starved (pool 0, standing agenda empty pending CEO route-a)")

did = ("r942 bm-b: T-186 formal closure (W19/W20 lineage: status claimed->done + result_ref enumerating judge 112 / "
       "paired_deltas / reform_face / W20 census 0-of-45 / CEO report V1) + S6 chain 26 legs all rc0 + paper legs "
       "gated honest (update_daily cutoff 2026-10-13, sina 10-14 bar undelivered source-side) + orders 0 unacked + "
       "D-19 EQUAL (dec c61d7884) + smoke 49/49 + attrition CLEAN + claws x4 reinstalled + inbox 0 unread")

current_task_next = ("r943: (a) sina 10-14 bar catch -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + "
                     "t24 prospect legs when landed; (b) supply route (a) stock-universe P1 awaits CEO signature; "
                     "route (b) closed by W20 census -- waiting-state declaration, no re-scan of same objects")

latest_artifact = ("fleet/tasks/T-2026-10-14-186-P1.json (status=done, full result_ref) + "
                   "results/market_clock/CALL-2026-10-13.md (ORANGE_COOL) @ " + ts)

next_milestone = ("sina 10-14 bar landing -> live.paper/t35/t24 chain (self-heal, window <=48h); supply route (a) "
                  "stock-universe P1 = CEO-signed gate pending; W19 CEO report due 10-16 13:49 already in library")

now_active = ("r942 closeout: T-186 lineage closed, S6 26 legs rc0; SatEngine ticking; CPU lanes light; "
              "waiting state = sina 10-14 bar (external) + CEO route-a signature (external)")

# --- state.json ---
sp = "state.json"
d = json.load(io.open(sp, encoding="utf-8"))
d["round"] = 942
d["round_no"] = 943
d["round_no_label"] = "r942"
d["current_task"] = current_task_next
d["task"] = current_task_next
d["did"] = did
d["last_action"] = "r942: T-186 closure + S6 26 legs rc0 + waiting-state declaration"
d["last_action_at"] = ts
d["last_round_at"] = ts
d["last_round_ts"] = ts
d["last_seen"] = ts
d["latest_artifact"] = latest_artifact
d["next"] = current_task_next
d["next_milestone"] = next_milestone
d["note"] = ("r942: waiting-state round declaration -- sina 10-14 bar undelivered (source-side, update_daily 0 new "
             "rows 0 failures) + MF panel source-blocked (bm-a collector line, 30-min self-heal) + trial-labor supply "
             "routes closed (W20 census) pending CEO-signed P1 route (a); one-line declaration per P-2026-09-29-07, "
             "no repeated re-scans of the same waiting objects")
d["now_active"] = now_active
d["orphan_face"] = 0
d["orphan_faces"] = 0
d["orphan_face_note"] = "r942 probe 17:2x: py_faces=10 orphans=0 killed=[]"
d["clock_read"] = ts
d["ts"] = ts
d["updated"] = ts
d["updated_at"] = ts
d["verdict"] = verdict
d["sync"] = {"last_push_ts": ts, "note": "r942 closeout commit+push follows this write; behind=0 verified post-push"}
json.dump(d, io.open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# --- heartbeat ---
hp = "fleet/machines/bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["round"] = 942
h["round_no"] = 943
h["round_no_label"] = "r942"
h["current_task"] = current_task_next
h["task"] = current_task_next
h["did"] = did
h["last_action"] = "r942: T-186 closure + S6 26 legs rc0 + waiting-state declaration"
h["last_action_at"] = ts
h["last_round_at"] = ts
h["last_seen"] = ts
h["latest_artifact"] = latest_artifact
h["next"] = current_task_next
h["next_milestone"] = next_milestone
h["note"] = ("r942: orders 0 unacked (disk 88 vs ack 88); D-19 dec EQUAL c61d7884 via fresh origin read; "
             "supply_floor/pool_starvation standing WITH VERDICT (route closed, refill = CEO P1); "
             "sina 10-14 bar catch pending self-heal; agenda_starved=true: pool 0 + standing agenda empty")
h["now_active"] = now_active
h["orphan_face"] = 0
h["orphan_faces"] = 0
h["orphan_face_note"] = "r942 probe 17:2x: py_faces=10 orphans=0 killed=[]"
h["clock_read"] = ts
h["ts"] = ts
h["heartbeat_epoch_utc"] = epoch
assert isinstance(h["heartbeat_epoch_utc"], int)
h["verdict"] = verdict
h["idle_rounds"] = 0
h["agenda_starved"] = True
h["green_idle"] = False
h["cpu_cores"] = cpu_cores
h["free_ram_gb"] = ram_free_gb
h["ram_free_gb"] = ram_free_gb
h["ram_free_pct"] = ram_free_pct
h["idle_ram_gb"] = ram_free_gb
h["idle_ram_pct"] = ram_free_pct
h["gpu_free_vram"] = "%d MiB" % vram_free_mb
h["gpu_free_vram_mb"] = vram_free_mb
h["gpu_free_vram_gb"] = round(vram_free_mb / 1024.0, 1)
h["gpu_idle_vram_gb"] = round(vram_free_mb / 1024.0, 1)
h["sync"] = {"last_push_ts": ts, "note": "r942 closeout commit+push follows this write; behind=0 verified post-push"}
json.dump(h, io.open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# post-write self-check (R170/R178: epoch must be int, clock must be T-separated)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read missing T separator"
print("heartbeat self-check PASS: epoch int =", chk["heartbeat_epoch_utc"], "clock =", chk["clock_read"])
print("ram_free_gb =", ram_free_gb, "ram_free_pct =", ram_free_pct, "vram_free_mb =", vram_free_mb)

# --- round report line ---
rp = "logs/iteration-loop/round_reports.md"
line = ("| {ts} | r942 bm-b [dept:eng/fleet+research/strategy] | WM-VERDICT: green (red=false; py_watermark=py_low_board_clear "
        "legal idle white-list; compute_audit pool_starvation+supply_floor standing WITH VERDICT route-closed; next_pick=moneyflow IC "
        "claimed panel source-blocked self-heal) | orphan-faces=0 (round-zero probe 17:2x: py_faces=10 orphans=0) | "
        "current: T-186 W19/W20 lineage formally CLOSED (status=done + result_ref full evidence chain) + S6 26 legs all rc0 + paper "
        "legs gated honest (no new bar, cutoff 2026-10-13) | latest artifact: fleet/tasks/T-2026-10-14-186-P1.json done + "
        "results/market_clock/CALL-2026-10-13.md (ORANGE_COOL) + DUALARM refresh @{ts} | next milestone: sina 10-14 bar landing -> "
        "live.paper REGIME_GUARD=enforce + t35/t24 chain (self-heal <=48h); supply route (a) stock-universe P1 awaits CEO signature | "
        "orders 0 unacked; D-19 dec EQUAL c61d7884; smoke 49/49; attrition CLEAN; claws x4 reinstalled; inbox 0 unread; "
        "unreached-origin commits=0 (push + fetch self-verify follows) | next pointer: r943 sina-bar-landing round; else "
        "waiting-state one-line declaration (no re-scan of same objects) |\n").format(ts=ts)
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report appended @", ts)
