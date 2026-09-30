"""r497 bm-a T-135 bonsai 4070S GPU-tier night-window re-verify orchestrator.

Group decision D-20261001-02 dispatch (yield law D-20260930-04(3)) / fleet task
T-2026-10-01-135. Sole spec = cph4/research/R-20260928-bonsai-fleet-trial.md (HQ repo);
protocol precedent = results/_r386bmb_bonsai_trial.py (bm-b T-99) + T-100 co-residency face.

Scope (ticket): speed + coexistence legs re-verified in genuine night window
(three Tuanjie editors absent; MiniGameOllamaKeepWarm 10-min keeper owns the
in-service qwen2.5:7b-instruct residency -- its U020 release valve
(.codely-cli/engine-tick/keepwarm.pause, bm-b yield-window precedent) is the
sanctioned pause mechanism for this run).
  A. bare    = byte anchors (3/3) + llama-bench tg128 bare-window
               (no other model resident -- VRAM first-claim, run immediately
               after the yield unload)
  A2. deploy = llama-server /health ok leg (bare window, after the bench)
  C. coexist = qwen2.5:7b-instruct re-warmed resident (keep_alive=-1,
               standing-keeper design state) -> co-resident tg128 attempt ->
               honest verdict (can-co-reside / needs-yield-window)
  D. restore  = 7b left resident (standing keeper design state), pause flag
                deleted (next keeper pass re-verifies residency regardless)

Live-run numbers only (zero pre-write). Exit codes:
  0 = full receipt written; 2 = mechanism failure (honest, report as-is);
  3 = trigger condition failed at probe time (no burn, honest no-op).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEN = r"C:\Users\sjs20\Desktop\FluxGroup\life\BigLife\.codely-cli\labbench\bonsai2"
MODEL = os.path.join(BEN, "Ternary-Bonsai-2-27B-PTQ1_0.gguf")
RUNTIME_DIR = os.path.join(BEN, "runtime")
RESULT = os.path.join(ROOT, "results", "_r497bma_bonsai_gpu_reverify.json")
PORT = 8077  # bm-a chosen port per HQ spec sec.1.4
OLLAMA = "http://127.0.0.1:11434"
QWEN_7B = "qwen2.5:7b-instruct"  # in-service J13/MiniGame keepwarm stack
TRIGGER_FREE_MB = 9000
# U020 release valve: gaming/MiniGame/.codely-cli/engine-tick/keepwarm.pause --
# while present the 10-min keeper stands down silently (keep-warm.ps1 headnote).
PAUSE_FLAG = os.path.join(r"C:\Users\sjs20\Desktop\FluxGroup\gaming\MiniGame",
                          ".codely-cli", "engine-tick", "keepwarm.pause")

BYTE_ANCHORS = {
    "model": (MODEL, 5946648928),
    "llama-bin.zip": (os.path.join(BEN, "llama-bin.zip"), 257322810),
    "cudart.zip": (os.path.join(BEN, "cudart.zip"), 391443627),
}


def fail(msg, code=2):
    print(f"[REVERIFY-FAIL] {msg}", flush=True)
    sys.exit(code)


def http_json(url, payload=None, timeout=600):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def gpu_sample():
    try:
        rc = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
        parts = [p.strip() for p in rc.stdout.strip().splitlines()[0].split(",")]
        return {"free_mb": int(parts[0]), "used_mb": int(parts[1]), "util_pct": int(parts[2]),
                "ts": time.strftime("%H:%M:%S")}
    except Exception as e:
        return {"error": str(e), "ts": time.strftime("%H:%M:%S")}


def phase_byte_check(res):
    out = {}
    for name, (path, anchor) in BYTE_ANCHORS.items():
        if not os.path.exists(path):
            fail(f"byte-check: {name} missing")
        size = os.path.getsize(path)
        ok = size == anchor
        out[name] = {"bytes": size, "anchor": anchor, "match": ok}
        print(f"[bytes] {name}: {size} vs {anchor} -> {'MATCH' if ok else 'MISMATCH'}", flush=True)
        if not ok:
            fail(f"byte-check: {name} mismatch (spec sec.1.1: no sick deployment)")
    res["byte_check"] = out


def phase_unpack():
    marker = os.path.join(RUNTIME_DIR, ".unpacked")
    if os.path.exists(marker):
        print("[unpack] already unpacked (idempotent)", flush=True)
        return
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    for zname in ("llama-bin.zip", "cudart.zip"):
        print(f"[unpack] {zname} ...", flush=True)
        rc = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Expand-Archive -Path '{os.path.join(BEN, zname)}' -DestinationPath '{RUNTIME_DIR}' -Force"],
            capture_output=True, text=True)
        if rc.returncode != 0:
            fail(f"unpack {zname} rc={rc.returncode}: {rc.stderr[-500:]}")
    with open(marker, "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%S"))
    print("[unpack] done", flush=True)


def find_exe(name):
    for root, dirs, files in os.walk(RUNTIME_DIR):
        if name in files:
            return os.path.join(root, name)
    return None


def set_pause_valve(res):
    os.makedirs(os.path.dirname(PAUSE_FLAG), exist_ok=True)
    with open(PAUSE_FLAG, "w", encoding="utf-8") as f:
        f.write("bonsai bm-a GPU-tier re-verify yield window (T-2026-10-01-135 / "
                "D-20261001-02), set "
                + time.strftime("%Y-%m-%d %H:%M:%S")
                + " -- deleted by the same run when done; U020 release valve\n")
    res["pause_valve"] = {"set": True, "path": PAUSE_FLAG}
    print("[valve] keepwarm.pause set (U020 yield window)", flush=True)


def del_pause_valve(res):
    try:
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            print("[valve] keepwarm.pause deleted (released)", flush=True)
        res.setdefault("pause_valve", {})["released"] = True
    except Exception as e:
        res["pause_valve_release_error"] = str(e)
        print(f"[valve] delete failed: {e}", flush=True)


def ollama_resident():
    try:
        r = http_json(f"{OLLAMA}/api/ps", timeout=10)
        return [m.get("name") for m in (r.get("models") or [])]
    except Exception:
        return None


def phase_yield_window(res):
    """U020 yield window: valve up, graceful unload of the keeper's 7b,
    settle-poll on VRAM release (direct nvidia-smi signal), then the bare
    legs run IMMEDIATELY -- an independent 5-min-TTL reloader client on
    this box re-warms the 7b within ~tens of seconds (observed 01:53:45
    reload 25s after a 01:53:20 unload), so the bench must allocate VRAM
    first; a mid-run reload attempt by that client fails on its side and
    self-heals on its next tick.  Restore path re-warms with keep_alive=-1
    (the keeper's own standing design state)."""
    set_pause_valve(res)
    resident = ollama_resident()
    res["qwen_state_before"] = {"resident_models": resident,
                                "gpu": gpu_sample()}
    if resident and QWEN_7B in resident:
        try:
            http_json(f"{OLLAMA}/api/generate",
                      {"model": QWEN_7B, "prompt": "", "stream": False,
                       "keep_alive": 0}, timeout=180)
            print("[yield] unload requested (keep_alive=0)", flush=True)
        except Exception as e:
            fail(f"yield-window unload failed: {e}")
        for _ in range(10):
            time.sleep(2)
            s = gpu_sample()
            if s.get("free_mb", 0) >= TRIGGER_FREE_MB:
                break
    s = gpu_sample()
    res["gpu_probe_bare"] = s
    print(f"[probe] bare-window free={s.get('free_mb')}MiB trigger>={TRIGGER_FREE_MB}", flush=True)
    if s.get("free_mb", 0) < TRIGGER_FREE_MB:
        fail(f"bare window not reachable after yield (free={s.get('free_mb')} < {TRIGGER_FREE_MB})", code=3)


def phase_deploy_health(res):
    server = find_exe("llama-server.exe")
    if not server:
        fail("llama-server.exe not found after unpack")
    cmd = [server, "-m", MODEL, "-ngl", "99", "-fa", "on", "--host", "127.0.0.1",
           "--port", str(PORT), "-c", "4096", "--no-webui"]
    print(f"[deploy] booting llama-server port {PORT} (bare window) ...", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        healthy = None
        for _ in range(300):
            if proc.poll() is not None:
                fail(f"llama-server exited early rc={proc.returncode} (VRAM envelope breach?)")
            try:
                http_json(f"http://127.0.0.1:{PORT}/health", timeout=3)
                healthy = time.time() - t0
                break
            except Exception:
                time.sleep(1)
        if healthy is None:
            fail("llama-server /health not ok within 300s")
        res["deploy"] = {"port": PORT, "health_ok_sec": round(healthy, 1),
                        "gpu_during_load": gpu_sample()}
        print(f"[deploy] /health ok after {healthy:.1f}s", flush=True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except Exception:
            proc.kill()
        time.sleep(5)
    print("[deploy] server stopped (deploy leg done)", flush=True)


def run_bench(tag):
    bench = find_exe("llama-bench.exe")
    if not bench:
        fail("llama-bench.exe not found after unpack")
    cmd = [bench, "-m", MODEL, "-ngl", "99", "-fa", "on", "-p", "512", "-n", "128", "-r", "3"]
    print(f"[bench:{tag}] {' '.join(cmd)}", flush=True)
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(cmd), "ok": False, "timeout": True}
    dur = round(time.time() - t0, 1)
    if rc.returncode != 0:
        return {"cmd": " ".join(cmd), "wall_sec": dur, "rc": rc.returncode,
                "stderr_tail": rc.stderr[-800:], "ok": False}
    out = {"cmd": " ".join(cmd), "wall_sec": dur, "rc": 0, "ok": True,
           "stdout_tail": rc.stdout[-1500:]}
    for line in rc.stdout.splitlines():
        if line.strip().startswith("|") and "512" in line and "128" in line and "±" in line:
            out["raw_row"] = line.strip()
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            try:
                out["pp512_tok_s"] = float(parts[2])
                out["tg128_tok_s"] = float(parts[3])
            except (ValueError, IndexError):
                pass
    # separate-row format (this llama-bench build prints one row per test);
    # charset-agnostic separator (\D+): llama-bench stdout is UTF-8 while
    # subprocess text=True decodes cp936, so the plus-minus glyph arrives
    # mojibake and any literal-glyph regex silently fails (r497 live lesson)
    if "tg128_tok_s" not in out:
        import re
        for line in rc.stdout.splitlines():
            m = re.search(r"(pp512|tg128)\s*\|\s*([\d.]+)\D+([\d.]+)", line)
            if m:
                out[m.group(1) + "_tok_s"] = float(m.group(2))
                out[m.group(1) + "_pm"] = float(m.group(3))
    print(f"[bench:{tag}] tg128={out.get('tg128_tok_s')} pp512={out.get('pp512_tok_s')} wall={dur}s", flush=True)
    return out


def main():
    res = {"ts_start": time.strftime("%Y-%m-%dT%H:%M:%S"), "machine": "bm-a",
           "task": "T-2026-10-01-135", "decision_ref": "D-20261001-02",
           "spec": "cph4/research/R-20260928-bonsai-fleet-trial.md",
           "anchor_reference": {"bm_a_4070S_prev_tg128": 54.7, "bm_b_3070_tg128": 40.75,
                                 "bm_c_3070mod16g_coresident_tg128": 40.52},
           "round_start_gpu": gpu_sample(),
           "window_note": "round-start free=10770MiB (keeper not yet resident); "
                          "MiniGameOllamaKeepWarm fired 01:43:59 mid-window and "
                          "re-warmed the in-service 7b -- U020 valve used per "
                          "bm-b yield-window precedent"}
    try:
        phase_byte_check(res)
        phase_unpack()
        phase_yield_window(res)
        # B. bare-window speed leg FIRST (tightest window: VRAM first-claim
        #    beats the independent 5-min-TTL reloader client)
        res["bare"] = run_bench("bare")
        res["gpu_after_bare"] = gpu_sample()
        phase_deploy_health(res)
        # C. coexist leg: re-warm keeper 7b (standing design state), then
        #    co-resident bench attempt -- honest verdict either way
        try:
            http_json(f"{OLLAMA}/api/generate",
                      {"model": QWEN_7B, "prompt": "1", "stream": False,
                       "options": {"num_predict": 1}, "keep_alive": -1}, timeout=300)
            print("[coexist] 7b re-warmed (keep_alive=-1, keeper design state)", flush=True)
        except Exception as e:
            res["coexist"] = {"verdict": "ollama-unreachable", "error": str(e)}
            print(f"[coexist] ollama re-warm failed: {e}", flush=True)
        time.sleep(5)
        res["gpu_qwen_resident"] = gpu_sample()
        res["coresident"] = run_bench("coresident")
        res["gpu_coresident"] = gpu_sample()
        if res["coresident"].get("ok") and res["coresident"].get("tg128_tok_s"):
            verdict = "can-co-reside"
        else:
            verdict = "needs-yield-window"
        res["coexist"] = {"verdict": verdict, "qwen_model": QWEN_7B,
                          "note": "co-resident = in-service 7b resident "
                                  "(keep_alive=-1) during the bonsai bench; "
                                  "OOM/fail = honest needs-yield-window"}
    finally:
        # D. restore: valve released; 7b stays resident = keeper design state
        del_pause_valve(res)
        res["gpu_final"] = gpu_sample()
    res["ts_end"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(RESULT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"[done] receipt evidence -> {RESULT}", flush=True)


if __name__ == "__main__":
    main()
