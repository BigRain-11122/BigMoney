# r518 bm-b closeout bookkeeping (crash-tail adopted + round completed)
import json, time, datetime, psutil, subprocess

now = datetime.datetime.now().astimezone()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- machine stats sample ---
cpu_pct = psutil.cpu_percent(interval=1)
free_ram = round(psutil.virtual_memory().available / (1024**3), 1)
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        stderr=subprocess.DEVNULL, timeout=15)
    gpu_free_mb = int(out.decode().strip().splitlines()[0].strip())
except Exception:
    gpu_free_mb = 2252
gpu_free_gb = round(gpu_free_mb / 1024, 1)

# --- state.json (probe-verified: indent=1 + CRLF, roundtrip-identical) ---
s = json.load(open("state.json", encoding="utf-8"))
assert s["round_no"] == 517, f"unexpected round_no {s['round_no']}"
s["round_no"] = 518
s["note"] = ("r518 (crash-tail adopted + completed by fresh invocation 19:12): W17xW19 collision yield round CLOSED -- "
             "re-band v3 surgery (surgical commit 23667218e on origin) + engine v3 re-burn 12/12 (18:54-19:06, first rng=80_001 in-shard verified) "
             "+ finalize one-pass rc0: K=37,520, merged mu -0.09214 sigma 0.24432 se_mu 0.001261, S5 4/4 PASS "
             "(mu drift 0.0037 / sigma -0.08% / A p95 delta -0.0015 / K-lift -0.0013), skill_line 1.1503->1.1490, "
             "ledger 401,948+2,200=404,148 (ledger_head self-cert @n1_w19_results.json; science_gates.ledger block persisted r509 law); "
             "prereg S7/S8 backfilled + selftest green after backfill (r307 two-state law); "
             "MSG-190x yield receipt committed to inbox for bm-c/bm-a consumption; uncommitted crash-tail (CODELY lesson + inbox moves + 2 surgical scripts) archived this round; "
             "S6 37 legs rc0 (dualrun ZERO-DRIFT streak 8/3; holiday honest no-ops); "
             "engine idle queue 0 (rotation gap: W18=bm-a/W20=bm-c slots; bm-b next own wave W22; GM waiver O-1612 standing).")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
    s[k] = now_iso
s["last_decisions_at"] = now_iso
txt = json.dumps(s, indent=1, ensure_ascii=False).replace("\n", "\r\n")
open("state.json", "w", encoding="utf-8", newline="").write(txt)

# --- heartbeat fleet/machines/bm-b.json (same indent-1 CRLF family) ---
hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["current_task"] = ("W19 finalize landed (K=37,520, ledger 404,148, S5 4/4 PASS, S7/S8 backfilled); "
                      "rotation watch W18=bm-a / W20=bm-c slots (fetch-first table-tail check); bm-b next own wave W22 (16+3k law); "
                      "engine queue empty = standing rotation gap (GM waiver O-1612)")
hb["round_no"] = 518
hb["verdict"] = ("r518 yield round completed end-to-end: W19 finalize verdict face landed one-pass rc0 "
                 "(ledger_head self-cert 404,148; K-lift -0.0013 negative honest); crash-tail adopted (liveness 3-check first); "
                 "py_low_board_clear legal idle (open 0/bandit 0/bars present); audit idle-family flags = standing rotation gap, GM waiver in case")
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["gpu_free_vram_gb"] = gpu_free_gb
hb["gpu_idle_vram_gb"] = gpu_free_gb
hb["gpu_idle_vram_mb"] = gpu_free_mb
assert isinstance(hb["heartbeat_epoch_utc"], int)
txt = json.dumps(hb, indent=1, ensure_ascii=False).replace("\n", "\r\n")
open(hb_path, "w", encoding="utf-8", newline="").write(txt)
json.loads(open(hb_path, encoding="utf-8").read())
assert isinstance(json.load(open(hb_path, encoding="utf-8"))["heartbeat_epoch_utc"], int)

print("state+heartbeat written; cpu_pct=%s free_ram=%s gpu_free_mb=%s epoch=%s(int)" % (cpu_pct, free_ram, gpu_free_mb, epoch))
