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
  4. heartbeat aliveness -- TWO faces, freshest wins (v1.2, r1535):
       fleet/machines/bm-c.json   what the rest of the fleet reads for liveness
       state-bm-c.json            the loop round ledger (heartbeat_epoch_utc)
     Reading only the ledger reported a file, not a machine: on 2026-11-11 05:05
     this face printed heartbeat_stale_5910s while the fleet heartbeat was ten
     minutes old, because the ledger had not moved since 03:26 (interactive
     rounds advance the fleet heartbeat and leave the ledger alone).
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
HB_STALE_S = 1800  # unchanged threshold; v1.2 only changes WHICH face answers it


def _read_hb(path, now_ts):
    """One heartbeat face: {path, epoch, age_s, error}. Missing is not stale."""
    face = {"path": path, "epoch": None, "age_s": None}
    if not os.path.exists(path):
        face["error"] = "missing"
        return face
    try:
        with io.open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        face["error"] = ("unreadable: " + str(e))[:80]
        return face
    raw = doc.get("heartbeat_epoch_utc")
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        face["error"] = "heartbeat_epoch_utc is %r, not a number" % (raw,)
        return face
    face["epoch"] = int(raw)
    face["age_s"] = max(0, int(now_ts - raw))  # a clock running ahead never reads as negative age
    return face


def _heartbeat_face(root, now_ts):
    """"Is this machine alive?" is answered by the freshest face, not by one file.

    Two files carry a heartbeat and different writers maintain them:
      fleet/machines/<id>.json  what the rest of the fleet reads (any round)
      state-<id>.json           the loop round ledger (heartbeat_epoch_utc)
    Reading only one of them reports a file instead of a machine (r1535). So:
    aliveness = the minimum age; staleness needs EVERY readable face stale;
    nothing readable is "unknown" and never degrades.
    """
    faces = {"loop_state": _read_hb(os.path.join(root, "state-bm-c.json"), now_ts),
             "fleet": _read_hb(os.path.join(root, "fleet", "machines", "bm-c.json"), now_ts)}
    live = dict((k, v) for k, v in faces.items() if v.get("age_s") is not None)
    if not live:
        return {"faces": faces, "trusted": None, "age_s": None,
                "stale_faces": [], "verdict": "unknown"}
    order = sorted(live.items(), key=lambda kv: (kv[1]["age_s"], 0 if kv[0] == "fleet" else 1))
    trusted, fresh_face = order[0]
    stale = sorted(k for k, v in live.items() if v["age_s"] > HB_STALE_S)
    return {"faces": faces, "trusted": trusted, "age_s": fresh_face["age_s"],
            "stale_faces": stale, "verdict": ("stale" if len(stale) == len(live) else "fresh")}


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

    hb_face = _heartbeat_face(ROOT, ts)
    hb_age_s = hb_face["age_s"]

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
    if hb_face["verdict"] == "stale":
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
            "heartbeat_verdict": hb_face["verdict"], "heartbeat_trusted": hb_face["trusted"],
            "heartbeat_faces": hb_face["faces"], "heartbeat_stale_faces": hb_face["stale_faces"],
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
    print("sentinel tick %s %s hb=%s(%ss of %s)" %
          (tick["verdict"], now_iso, hb_face["verdict"], hb_age_s, hb_face["trusted"]))
    return 0 if not degraded else 1


def _selftest():
    """Fixture matrix for the two-face heartbeat. Offline, no repo writes."""
    import shutil, tempfile
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[0] += 1 if cond else 0
        ok[1] += 1
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, (" | " + detail) if detail else ""))

    now = 1800000000
    base = tempfile.mkdtemp(prefix="hb_fixture_")
    try:
        def write(root, loop_epoch=None, fleet_epoch=None, raw_loop=None, raw_fleet=None):
            os.makedirs(os.path.join(root, "fleet", "machines"), exist_ok=True)
            for name, path, ep, raw in (
                    ("state-bm-c.json", "state-bm-c.json", loop_epoch, raw_loop),
                    ("fleet", os.path.join("fleet", "machines", "bm-c.json"), fleet_epoch, raw_fleet)):
                full = os.path.join(root, path)
                if raw is not None:
                    with io.open(full, "w", encoding="utf-8") as f:
                        f.write(raw)
                elif ep is not None:
                    with io.open(full, "w", encoding="utf-8") as f:
                        json.dump({"heartbeat_epoch_utc": ep}, f)

        # L1 both fresh, tie -> the fleet face wins (that is the one other machines read)
        r = os.path.join(base, "l1"); write(r, now - 60, now - 60)
        f = _heartbeat_face(r, now)
        chk("L1 both fresh -> fresh, tie trusts the fleet face",
            f["verdict"] == "fresh" and f["age_s"] == 60 and f["trusted"] == "fleet",
            "%s %s %s" % (f["verdict"], f["age_s"], f["trusted"]))

        # L2 THE REGRESSION LEG: a stale loop ledger beside a fresh fleet heartbeat
        r = os.path.join(base, "l2"); write(r, now - 5910, now - 569)
        f = _heartbeat_face(r, now)
        chk("L2 stale loop ledger + fresh fleet -> fresh (the r1535 false alarm)",
            f["verdict"] == "fresh" and f["age_s"] == 569 and f["stale_faces"] == ["loop_state"],
            "%s age=%s stale=%s" % (f["verdict"], f["age_s"], f["stale_faces"]))
        chk("L2b the stale face is still disclosed, not silently dropped",
            f["faces"]["loop_state"]["age_s"] == 5910 and f["trusted"] == "fleet",
            "loop=%s" % f["faces"]["loop_state"]["age_s"])

        # L3 both stale -> stale, age = the FRESHEST of the two (the best face still misses the line)
        r = os.path.join(base, "l3"); write(r, now - 7200, now - 2400)
        f = _heartbeat_face(r, now)
        chk("L3 both stale -> stale with the freshest age",
            f["verdict"] == "stale" and f["age_s"] == 2400 and len(f["stale_faces"]) == 2,
            "%s %s %s" % (f["verdict"], f["age_s"], f["stale_faces"]))

        # L4 nothing readable -> unknown, never stale (a missing file is not a dead machine)
        r = os.path.join(base, "l4"); os.makedirs(r, exist_ok=True)
        f = _heartbeat_face(r, now)
        chk("L4 both missing -> unknown, age None, not stale",
            f["verdict"] == "unknown" and f["age_s"] is None and f["trusted"] is None,
            "%s %s" % (f["verdict"], f["age_s"]))

        # L5 a malformed fleet epoch falls back to the ledger and names the fault
        r = os.path.join(base, "l5"); write(r, now - 120, raw_fleet='{"heartbeat_epoch_utc": "1794344141"}')
        f = _heartbeat_face(r, now)
        chk("L5 string epoch -> that face unreadable, ledger trusted, fault named",
            f["verdict"] == "fresh" and f["trusted"] == "loop_state"
            and str(f["faces"]["fleet"].get("error", "")).startswith("heartbeat_epoch_utc"),
            "%s %s %s" % (f["verdict"], f["trusted"], f["faces"]["fleet"].get("error")))

        # L6 a clock running ahead must not produce a negative age
        r = os.path.join(base, "l6"); write(r, now + 300, now + 300)
        f = _heartbeat_face(r, now)
        chk("L6 future epoch clamps to 0, stays fresh",
            f["verdict"] == "fresh" and f["age_s"] == 0, "%s %s" % (f["verdict"], f["age_s"]))

        # L7 unparseable ledger JSON degrades that face only
        r = os.path.join(base, "l7"); write(r, raw_loop="{not json", fleet_epoch=now - 30)
        f = _heartbeat_face(r, now)
        chk("L7 unparseable ledger -> fleet answers, error recorded",
            f["verdict"] == "fresh" and f["trusted"] == "fleet"
            and str(f["faces"]["loop_state"].get("error", "")).startswith("unreadable"),
            "%s %s" % (f["verdict"], f["faces"]["loop_state"].get("error")))

        # L8 only the ledger present and stale -> stale (every READABLE face is stale)
        r = os.path.join(base, "l8"); write(r, now - 3600)
        f = _heartbeat_face(r, now)
        chk("L8 single readable face, stale -> stale",
            f["verdict"] == "stale" and f["trusted"] == "loop_state",
            "%s %s" % (f["verdict"], f["trusted"]))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("selftest %d/%d PASS" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        raise SystemExit(_selftest())
    raise SystemExit(main())
