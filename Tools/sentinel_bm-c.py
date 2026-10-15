# -*- coding: utf-8 -*-
"""bm-c-Sentinel v1.1 (O-20261014-0949 sec.1-4, bm-b-Sentinel O-0948 pattern adapted)

Stack health probe + idle watch + LIMITED self-heal (alert-only, zero restarts).
Zero repo writes: no git mutations ever; writes only the state face below.

v1.1 (O-20261015-0025 receipt, bm-b v1.2 TTL-law absorption, bm-c-appropriate form):
  - VALVE TTL FACE (report-only): machine-state.flag saying "paused" older than 12h
    with GPU showing zero real batch work -> tick flags stale_pause_valve_suspect.
    Alert-only per v1.0 covenant: NO auto-clear (MV V3 burn lane protected
    O-20261014-0312 sec.2; a real CEO pause valve is highest law -- clearing is
    left to a live loop round with evidence, never to the sentinel itself).
  - OLLAMA FACE ALIGNMENT: ollama API down on bm-c is the EXPECTED standing state
    since CEO 2026-10-14 lane law (35B coding LLM decommissioned from bm-c GPU,
    migrated to bm-a; bm-c GPU = generation-visual only). Probe kept for
    visibility, no longer a DEGRADED trigger.

Scope of probes (bm-c stack):
  1. ollama API 127.0.0.1:11434 (/api/tags store count + /api/ps loaded models)
     -- REPORT-ONLY since v1.1 (decommission face, see above)
  2. ComfyUI 127.0.0.1:8188 /system_stats  -- REPORT-ONLY, never restarted here:
     MV V3 GPU burn lane is protected per O-20261014-0312 sec.2 (zero touch).
  3. saturation engine state face freshness (results/saturation_engine_state.bm-c.json)
  4. heartbeat freshness (state-bm-c.json heartbeat_epoch_utc age)
  5. disk free (K:), RAM free, GPU face (nvidia-smi csv)
  6. schtask presence face for Bigmoney-IterationLoop / Bigmoney-LoopWatchdog (report-only)
  7. machine-state pause-valve freshness face (TTL law, 12h, alert-only)

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


VALVE_PATH = r"K:\Fluxgroup\.codely-cli\machine-state.flag"
VALVE_TTL_H = 12.0  # bm-b v1.2 TTL law (O-20261015-0025 sec.2), alert-only on bm-c


def _valve_face(gpu_util_pct):
    """machine-state pause-valve freshness face (TTL law, alert-only, v1.1).

    Reads the flag file written by machine-state.ps1: 'resumed <iso>' or
    'paused <iso>'. A 'paused' valve older than VALVE_TTL_H hours with the GPU
    showing no real batch work is flagged stale_pause_valve_suspect -- evidence
    for a live loop round to clear it; the sentinel itself never clears.
    """
    face = {"path": VALVE_PATH, "present": False}
    try:
        if not os.path.exists(VALVE_PATH):
            face["note"] = "no valve file (bm-c pause law not engaged)"
            return face
        with io.open(VALVE_PATH, encoding="utf-8", errors="replace") as f:
            raw = f.read().strip()
        face["present"] = True
        face["raw"] = raw[:60]
        parts = raw.split(None, 1)
        state = parts[0].lower() if parts else "unknown"
        face["state"] = state
        if len(parts) > 1:
            try:
                stamp = datetime.datetime.fromisoformat(parts[1].strip())
                age_h = (datetime.datetime.now() - stamp).total_seconds() / 3600.0
                face["age_h"] = round(age_h, 2)
            except Exception:
                face["age_h"] = None
        if state == "paused":
            age = face.get("age_h")
            util = None
            try:
                util = float(str(gpu_util_pct).replace("%", "").strip())
            except Exception:
                pass
            face["gpu_util_pct"] = util
            if age is not None and age > VALVE_TTL_H and (util is None or util < 5.0):
                face["stale_suspect"] = True
            else:
                face["stale_suspect"] = False
    except Exception as e:
        face["error"] = str(e)[:80]
    return face


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
    gpu = _gpu_face()
    valve = _valve_face(gpu.get("util_pct"))

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
    # v1.1: ollama DOWN is the expected standing state on bm-c since CEO
    # 2026-10-14 lane law (35B LLM decommissioned to bm-a) -- report-only face,
    # NOT a degraded trigger (was a standing false alarm since 2026-10-14).
    if engine_age_s is not None and engine_age_s > 600:
        degraded.append("engine_state_stale_%ds" % engine_age_s)
    if hb_age_s is not None and hb_age_s > 1800:
        degraded.append("heartbeat_stale_%ds" % hb_age_s)
    if disk_free_gb is not None and disk_free_gb < 20:
        degraded.append("disk_low_%sG" % disk_free_gb)
    # ComfyUI down is REPORT-ONLY (MV lane protected, O-20261014-0312 sec.2) -- not a degrade.
    # v1.1 valve TTL law (alert-only): stale paused valve + zero GPU real work.
    if valve.get("stale_suspect"):
        degraded.append("stale_pause_valve_suspect_%sh" % valve.get("age_h"))

    tick = {
        "ts": now_iso, "epoch": int(ts), "verdict": "DEGRADED" if degraded else "NORMAL",
        "degraded": degraded,
        "stack": {
            "ollama_api": ("DOWN (decommissioned per O-20261014 lane law, report-only)"
                           if not ok_tags else "UP"),
            "ollama_store_models": store_n,
            "ollama_loaded": loaded,
            "comfy_8188": "UP" if ok_comfy else "DOWN (report-only, MV lane protected)",
            "engine_state_age_s": engine_age_s, "heartbeat_age_s": hb_age_s,
            "disk_free_gb": disk_free_gb, "ram_free_gb": ram_free_gb, "gpu": gpu,
            "pause_valve": valve,
            "tasks": _task_face(),
        },
        "self_heal": "v1.1 alert-only (valve TTL law absorbed O-20261015-0025, report-only; zero restarts; MV V3 burn lane protected per O-20261014-0312 sec.2)",
    }

    try:
        with io.open(OUT, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        doc = {"schema": "bm-c-sentinel v1.1", "law_ref": "O-20261014-0949 sec.1-4 + O-0948 pattern + O-20261015-0025 valve TTL (bm-b v1.2, alert-only form)", "ticks": []}
    doc["ticks"] = (doc.get("ticks", []) + [tick])[-MAX_TICKS:]
    doc["schema"] = "bm-c-sentinel v1.1"
    doc["latest"] = tick
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print("sentinel tick %s %s" % (tick["verdict"], now_iso))
    return 0 if not degraded else 1


if __name__ == "__main__":
    raise SystemExit(main())
