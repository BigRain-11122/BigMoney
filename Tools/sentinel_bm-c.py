# -*- coding: utf-8 -*-
"""bm-c-Sentinel v1.0 (O-20261014-0949 sec.1-4, bm-b-Sentinel O-0948 pattern adapted)

Stack health probe + idle watch + LIMITED self-heal (v1 = alert-only, zero restarts).
Zero repo writes: no git mutations ever; writes only the state face below.

Scope of probes (bm-c stack):
  1. ollama API 127.0.0.1:11434 (/api/tags store count + /api/ps loaded models)
  2. ComfyUI 127.0.0.1:8188 /system_stats  -- REPORT-ONLY, never restarted here:
     MV V3 GPU burn lane is protected per O-20261014-0312 sec.2 (zero touch);
     self-heal re-enabled only when burn-window marker absent (v1.1+, not this file).
  3. saturation engine state face freshness (results/saturation_engine_state.bm-c.json)
  4. heartbeat freshness (state-bm-c.json heartbeat_epoch_utc age)
  5. disk free (K:), RAM free, GPU face (nvidia-smi csv)
  6. schtask presence face for Bigmoney-IterationLoop / Bigmoney-LoopWatchdog (report-only)

State face: results/_sentinel_bm-c.json  (ring buffer, last 20 ticks)
Exit codes: 0 NORMAL, 1 DEGRADED (probe down), 2 mechanism fault. Sentinel never raises windows (pythonw hidden chain).
"""
import json, io, os, time, datetime, subprocess, urllib.request

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(ROOT, "results", "_sentinel_bm-c.json")
MAX_TICKS = 20


def _probe(url, timeout=4):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return True, json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return False, str(e)[:120]


def _gpu_face():
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
        s = p.stdout.strip()
        parts = [x.strip() for x in s.split(",")]
        return {"util_pct": parts[0], "mem_used_mib": parts[1], "mem_total_mib": parts[2]}
    except Exception as e:
        return {"error": str(e)[:80]}


def _task_face():
    faces = {}
    for name in ("Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog"):
        try:
            p = subprocess.run(["schtasks", "/query", "/tn", name], capture_output=True, text=True, timeout=10)
            faces[name] = "present" if p.returncode == 0 else "absent"
        except Exception as e:
            faces[name] = "err:" + str(e)[:60]
    return faces


def main():
    now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    ts = time.time()

    ok_tags, tags = _probe("http://127.0.0.1:11434/api/tags")
    store_n = len(tags.get("models", [])) if ok_tags else 0
    ok_ps, ps = _probe("http://127.0.0.1:11434/api/ps")
    loaded = [m.get("name") for m in ps.get("models", [])] if ok_ps else []
    ok_comfy, comfy = _probe("http://127.0.0.1:8188/system_stats")

    engine_age_s = None
    try:
        eng = os.path.join(ROOT, "results", "saturation_engine_state.bm-c.json")
        engine_age_s = int(ts - os.path.getmtime(eng)) if os.path.exists(eng) else None
    except Exception:
        pass

    hb_age_s = None
    try:
        with io.open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8") as f:
            hb_age_s = int(ts - json.load(f).get("heartbeat_epoch_utc", 0))
    except Exception:
        pass

    try:
        import ctypes
        fm = ctypes.windll.kernel32.GetDiskFreeSpaceExW
        free = ctypes.c_ulonglong(); total = ctypes.c_ulonglong()
        fm("K:\\", ctypes.byref(free), ctypes.byref(total), None)
        disk_free_gb = round(free.value / 2**30, 1)
    except Exception:
        disk_free_gb = None

    try:
        import psutil  # optional; absence tolerated
        ram_free_gb = round(psutil.virtual_memory().available / 2**30, 1)
    except Exception:
        ram_free_gb = None

    degraded = []
    if not ok_tags:
        degraded.append("ollama_api_down")
    if engine_age_s is not None and engine_age_s > 600:
        degraded.append("engine_state_stale_%ds" % engine_age_s)
    if hb_age_s is not None and hb_age_s > 1800:
        degraded.append("heartbeat_stale_%ds" % hb_age_s)
    if disk_free_gb is not None and disk_free_gb < 20:
        degraded.append("disk_low_%sG" % disk_free_gb)
    # ComfyUI down is REPORT-ONLY (MV lane protected, O-20261014-0312 sec.2) -- not a degrade.

    tick = {
        "ts": now_iso, "epoch": int(ts), "verdict": "DEGRADED" if degraded else "NORMAL",
        "degraded": degraded,
        "stack": {
            "ollama_api": "UP" if ok_tags else "DOWN", "ollama_store_models": store_n,
            "ollama_loaded": loaded,
            "comfy_8188": "UP" if ok_comfy else "DOWN (report-only, MV lane protected)",
            "engine_state_age_s": engine_age_s, "heartbeat_age_s": hb_age_s,
            "disk_free_gb": disk_free_gb, "ram_free_gb": ram_free_gb, "gpu": _gpu_face(),
            "tasks": _task_face(),
        },
        "self_heal": "v1 alert-only (zero restarts; MV V3 burn lane protected per O-20261014-0312 sec.2)",
    }

    try:
        with io.open(OUT, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        doc = {"schema": "bm-c-sentinel v1.0", "law_ref": "O-20261014-0949 sec.1-4 + O-0948 pattern", "ticks": []}
    doc["ticks"] = (doc.get("ticks", []) + [tick])[-MAX_TICKS:]
    doc["latest"] = tick
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print("sentinel tick %s %s" % (tick["verdict"], now_iso))
    return 0 if not degraded else 1


if __name__ == "__main__":
    raise SystemExit(main())
