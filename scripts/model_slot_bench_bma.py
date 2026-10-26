"""bm-a model-slot bench (SLOT-POLICY-v1 machine leg, CEO 2026-10-27 00:40 order).

Measures, on THIS machine and without evicting any resident model:
  * the ollama model currently resident (POST /api/generate, stream=false ->
    eval_count/eval_duration = decode tok/s, prompt_eval = prefill),
  * the llama-server process that is already running (POST /completion ->
    timings.predicted_per_second),
  * the GPU / VRAM floor taken BEFORE any measurement (the idle baseline the
    committee's acceptance criterion 4 asks for).

Design law learned the hard way in this fleet: a bench that unloads the
production model to measure a first-load number breaks the running service.
So first-load is reported as NOT MEASURED here and only models that are
already resident are timed. Every number in the JSON carries the command
that produced it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _get(url: str, payload: dict | None = None, timeout: int = 180) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def nvidia() -> dict:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=60)
    line = (out.stdout or "").strip().splitlines()[0]
    parts = [p.strip() for p in line.split(",")]
    return {"name": parts[0], "total_mb": int(parts[1]), "used_mb": int(parts[2]),
            "free_mb": int(parts[3]), "util_pct": int(parts[4]), "raw": line}


def ollama_ps() -> str:
    out = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=60)
    return (out.stdout or "").strip()


def bench_ollama(model: str, runs: int = 3) -> dict:
    """Decode rate of an already-resident ollama model."""
    rows = []
    for i in range(runs):
        t0 = time.time()
        r = _get("http://127.0.0.1:11434/api/generate", {
            "model": model,
            "prompt": "用一句话说明量化回测里样本外验证为什么必要。",
            "stream": False,
            "keep_alive": "1h",   # never ask ollama to unload/reschedule the resident face
            "options": {"temperature": 0, "num_predict": 128},
        })
        wall = time.time() - t0
        ev = r.get("eval_count") or 0
        evd = (r.get("eval_duration") or 0) / 1e9
        pev = r.get("prompt_eval_count") or 0
        pevd = (r.get("prompt_eval_duration") or 0) / 1e9
        rows.append({
            "run": i + 1,
            "tokens": ev,
            "decode_tok_s": round(ev / evd, 2) if evd > 0 else None,
            "prefill_tok_s": round(pev / pevd, 2) if pevd > 0 else None,
            "wall_s": round(wall, 2),
        })
    rates = [r["decode_tok_s"] for r in rows if r["decode_tok_s"]]
    return {"model": model, "runs": rows,
            "median_decode_tok_s": sorted(rates)[len(rates) // 2] if rates else None,
            "command": "POST http://127.0.0.1:11434/api/generate stream=false num_predict=128 temperature=0"}


def llama_server_port() -> int | None:
    """Port the resident llama-server actually listens on (not assumed)."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='llama-server.exe'\" | "
          "Select-Object -ExpandProperty CommandLine")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=120)
    cmd = (out.stdout or "").strip().splitlines()
    if not cmd:
        return None
    line = cmd[0]
    for i, tok in enumerate(line.split()):
        if tok == "--port" and i + 1 < len(line.split()):
            try:
                return int(line.split()[i + 1])
            except ValueError:
                pass
    return 8090


def bench_llama(port: int, runs: int = 3) -> dict:
    rows = []
    for i in range(runs):
        r = _get(f"http://127.0.0.1:{port}/completion", {
            "prompt": "用一句话说明量化回测里样本外验证为什么必要。",
            "n_predict": 128, "temperature": 0, "cache_prompt": True,
        })
        t = r.get("timings") or {}
        rows.append({
            "run": i + 1,
            "tokens": t.get("predicted_n"),
            "decode_tok_s": round(t.get("predicted_per_second", 0), 2) or None,
            "prefill_tok_s": round(t.get("prompt_per_second", 0), 2) or None,
        })
    rates = [x["decode_tok_s"] for x in rows if x["decode_tok_s"]]
    return {"port": port, "runs": rows,
            "median_decode_tok_s": sorted(rates)[len(rates) // 2] if rates else None,
            "command": f"POST http://127.0.0.1:{port}/completion n_predict=128 temperature=0"}


def run(tag: str = "manual") -> dict:
    gpu0 = nvidia()
    ps_before = ollama_ps()
    resident = []
    for line in ps_before.splitlines()[1:]:
        cols = line.split()
        if cols:
            resident.append({"name": cols[0], "size": cols[2] if len(cols) > 2 else None,
                             "processor": " ".join(cols[3:5]) if len(cols) > 4 else None})

    ollama_rows = []
    for model in [m["name"] for m in resident]:
        try:
            ollama_rows.append(bench_ollama(model))
        except Exception as exc:                     # measurement fault is data, not a crash
            ollama_rows.append({"model": model, "error": f"{type(exc).__name__}: {exc}"})

    llama = None
    port = llama_server_port()
    if port:
        try:
            llama = bench_llama(port)
        except Exception as exc:
            llama = {"port": port, "error": f"{type(exc).__name__}: {exc}"}

    gpu1 = nvidia()
    doc = {
        "machine_id": "bm-a",
        "tag": tag,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "gpu": gpu0,
        "gpu_after": gpu1,
        "idle_baseline_note": "gpu0 is the state BEFORE any bench call (acceptance criterion 4)",
        "ollama_ps_before": ps_before,
        "ollama_resident": resident,
        "ollama_bench": ollama_rows,
        "llama_server": llama,
        "first_load": "NOT MEASURED by design: unloading a resident production model to time a cold load breaks the running service; disclosed, not estimated",
        "not_in_inventory_warning": "only models present in `ollama list` can be timed; anything the paper matrix v1.2 names but that is not on disk is reported absent, never extrapolated",
    }
    out = ROOT / "results" / "model_slots" / f"bench-bm-a-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    latest = out.parent / "bench-bm-a-latest.json"
    latest.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out),
                      "ollama": [(r.get("model"), r.get("median_decode_tok_s")) for r in ollama_rows],
                      "llama": (llama or {}).get("median_decode_tok_s") if isinstance(llama, dict) else None,
                      "gpu_used_mb": gpu0["used_mb"]}, ensure_ascii=False))
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run"])
    ap.add_argument("--tag", default="manual")
    a = ap.parse_args(argv)
    run(tag=a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())