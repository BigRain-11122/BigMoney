# -*- coding: utf-8 -*-
import json, subprocess, time, datetime, os, ctypes

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
clock = now.replace(microsecond=0).isoformat()

class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

ms = MS(); ms.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
total_gb = ms.ullTotalPhys / 2**30
free_gb = ms.ullAvailPhys / 2**30
load_pct = float(ms.dwMemoryLoad)

gpu_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.strip()
    f, t, u = [x.strip() for x in out.splitlines()[0].split(",")]
    gpu_free_mb = float(f)
    gpu_total_mb = float(t)
    gpu_util = float(u)
except Exception as e:  # honest absence
    gpu_total_mb = gpu_util = None

fields = {
    "last_seen": clock,
    "ts": clock,
    "clock_read": clock,
    "heartbeat_epoch_utc": int(time.time()),
    "current_task": "r1269 closeout",
    "current_task_short": "r1269 strand delivered",
    "verdict": "A_STRAND_IS_ONLY_DEBT_UNTIL_IT_IS_ON_ORIGIN",
    "did": ("r1269: rebased the 28-commit strand onto origin r1398-1401 (union for ledgers/docs, origin for "
            "regenerable faces) and pushed it -- behind 0 / ahead 0; then refreshed three core legs"),
    "cpu_cores": 32,
    "ram_free_gb": round(free_gb, 2),
    "ram_free_pct": round(100.0 * free_gb / total_gb, 1),
    "ram_load_pct": load_pct,
    "total_ram_gb": round(total_gb, 1),
    "idle_rounds": 0,
    "agenda_starved": False,
    "last_round": 1269,
    "last_round_label": "r1269",
    "last_round_at": clock,
    "last_push_at": "2026-11-07T16:40+08:00",
    "last_commit": "03fd741172",
    "last_artifact": "results/data_lane_freshness.json",
    "next_milestone": "full chain + full smoke on the integrated tree, and the 12 stale-base faces regenerated (<=24h)",
}
if gpu_free_mb is not None:
    fields["gpu_free_mb"] = gpu_free_mb
    fields["gpu_free_vram_mb"] = gpu_free_mb
    fields["gpu_free_vram_gb"] = round(gpu_free_mb / 1024.0, 2)
    fields["gpu_free_gb"] = round(gpu_free_mb / 1024.0, 2)
    fields["gpu_total_mb"] = gpu_total_mb
    fields["gpu_util_pct"] = gpu_util

fpath = os.path.join(os.environ["TEMP"], "bm-a-r1269-hb.json")
with open(fpath, "w", encoding="utf-8") as fh:
    json.dump(fields, fh, ensure_ascii=False)

r = subprocess.run(["python", os.path.join(ROOT, "Tools", "heartbeat_write.py"), "apply",
                    "--fields", fpath],
                   capture_output=True, text=True, cwd=ROOT)
print("hw rc=%s" % r.returncode)
print((r.stdout + r.stderr).strip()[-800:])

# read-back invariants
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-a.json"), encoding="utf-8"))
print("epoch_int=%s acks=%s clock=%s" % (
    isinstance(hb.get("heartbeat_epoch_utc"), int),
    len(hb.get("orders_ack") or []),
    hb.get("clock_read")))