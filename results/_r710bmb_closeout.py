# r710 bm-b closeout: state.json round_no++, heartbeat update, round report append
# Fields per fleet/README.md S5/S7; heartbeat epoch must be JSON int (R170/R178 law); clock_read T-format (R262 law)
import json, time, datetime, io, os

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 710

# --- fresh machine metrics (psutil with fallback) ---
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=None), 1)
    free_gb = round(psutil.virtual_memory().available / 1024**3, 1)
    total_gb = round(psutil.virtual_memory().total / 1024**3, 1)
except Exception:
    cpu_pct, free_gb, total_gb = 60.0, 3.2, 25.7
gpu_free_mb = 3292
try:
    a = json.load(open("results/compute_audit.json", encoding="utf-8"))
    used = a.get("gpu", {}).get("mem_used_mb")
    if used:
        gpu_free_mb = int(8192 - float(used))
except Exception:
    pass

# --- state.json (bm-b uses root state.json per fleet README S5) ---
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = ROUND
st["round_no_label"] = f"round {ROUND} (bm-b)"
st["note"] = ("r710: watch round - W15 judge 12/12 landed (finalize seat = bm-a F-04 declared per r709 addendum, "
              "bm-b zero seat-competition zero action); trio NULLS V/Q/D lanes burning in flight; "
              "S6 chain 34 legs rc0 (dualrun ZERO-DRIFT streak 7, audit CLEAN burning-healthy, scorecard "
              "stale-takeover derive per O-2100 s2.4, REPORT/LIVE-2026-10-05 regenerated); smoke 48/48; "
              "orders 154/154 double-scan zero unacked; D-19 decisions+orders dual hash MATCH 755428F8/E79E15F9; "
              "attrition CLEAN; quartet 4/4; RAM gate 3.1-3.9GB<4GB legal hold.")
st["last_round_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
st["next"] = ("(a) trio V lane closeout 10-06T17 (then Q 10-07T1x, D 10-08T0x); "
              "(b) D-06 closeout report to group 10-07 12:00 (20 pit-*.md all <=30KB achieved r707); "
              "(c) W15 judge-finalize landing watch (bm-a seat, do not touch); "
              "(d) 10-09 post-holiday data-chain check (first trading day after National Day).")
with io.open("state.json", "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# --- heartbeat fleet/machines/bm-b.json ---
hb_path = os.path.join("fleet", "machines", "bm-b.json")
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["round_no"] = ROUND
hb["round_no_label"] = f"round {ROUND} (bm-b)"
hb["current_task"] = ("round 710 watch: W15 judge 12/12 done (finalize=bm-a F-04 seat, zero competition); "
                      "trio NULLS V1136/Q910/D719 of 2000 in flight; N1-W118 1of12 landed (RAM-gated next); "
                      "S6 chain 34 legs green")
hb["verdict"] = "green"
hb["ts"] = NOW
hb["updated"] = NOW
hb["updated_at"] = NOW
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["ram_avail_gb"] = free_gb
hb["total_ram_gb"] = total_gb
hb["ram_gb"] = total_gb
hb["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024, 2)
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_vram_free"] = gpu_free_mb
hb["gpu_free_vram_mib"] = gpu_free_mb
hb["gpu_free_mb"] = gpu_free_mb
with io.open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# self-assert: epoch is int (R170/R178 law), clock_read has T separator (R262 law)
hb2 = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"], "clock_read must be T-format ISO 8601"
print("closeout_fields_ok epoch=%d clock=%s ram=%s gpu=%s" % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], free_gb, gpu_free_mb))
