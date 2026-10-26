"""bm-c model-slot bench (SLOT-POLICY-v1 machine leg, CEO 2026-10-27 00:40 order).

bm-a's bench (scripts/model_slot_bench_bma.py) only times models that are
ALREADY resident, because unloading a production model there breaks a running
service. This machine has no resident model at all (every Ollama task was
cleared on 2026-10-17), so the only way to get a first-load number here is to
load the model ourselves -- and then unload it again (keep_alive=0) so the
desktop user never inherits a 13 GB resident.

Because that path can OOM a 24 GB box, every model passes a MEMORY GATE first:
estimated weights + a fixed working-set reserve must fit in what is actually
available right now. A model that fails the gate is reported `skipped` with the
numbers that failed it -- never extrapolated, never timed halfway.

Every row carries the command that produced it. Inventory is derived from the
manifest directory (not hardcoded), so a model that appears or disappears on
disk changes the report without editing code.

    python scripts/model_slot_bench_bmc.py run
    python scripts/model_slot_bench_bmc.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.path.expanduser("~"))
MANIFEST_ROOT = HOME / ".ollama" / "models" / "manifests" / "registry.ollama.ai" / "library"
OLLAMA_EXE = HOME / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"
API = "http://127.0.0.1:11434"
PROMPT = "Explain in one sentence why a scheduler must not evict a resident model."
GEN_CMD = ("POST /api/generate stream=false num_predict=128 temperature=0 "
           "keep_alive=0")
# Weights alone are not the cost: the runner also needs KV cache + graph arena.
# 1.5 GB is the measured floor for a 4B at ctx 4096 on this box plus slack.
WORKING_SET_RESERVE_GB = 1.5
CREATE_NO_WINDOW = 0x08000000


# ---------------------------------------------------------------- pure helpers
def model_name_from_manifest(path: Path) -> str:
    """.../library/qwen3.5/9b-q4_K_M -> 'qwen3.5:9b-q4_K_M' (no extension logic)."""
    parts = Path(path).parts
    if len(parts) < 2:
        raise ValueError(f"not a model manifest path: {path}")
    return f"{parts[-2]}:{parts[-1]}"


def estimate_size_bytes(manifest: dict) -> int:
    """Sum layer sizes minus the `config` and `license` metadata blobs.

    Ollama stores weights + template params as layers; config/license are text
    metadata, and counting them inflates a 4B by tens of MB -- harmless for a
    gate but wrong in a report a human reads.
    """
    total = 0
    for layer in manifest.get("layers") or []:
        if layer.get("mediaType") in ("application/vnd.docker.container.image.v1+json",
                                      "application/vnd.ollama.image.license"):
            continue
        total += int(layer.get("size") or 0)
    return total


def gate(avail_gb: float, vram_free_gb: float, size_gb: float) -> tuple[bool, str]:
    """Two-sided gate: weights must fit EITHER whole on the GPU or in RAM.

    Weights parked in VRAM still need a RAM working set (KV cache arena, graph
    buffers) but not the weight bytes, so one 13 GB model can run on a box with
    1.9 GB free RAM and 14.9 GB free VRAM. Counting only RAM over-refuses;
    counting only VRAM would let a model spill into a full page file.
    """
    reserve = WORKING_SET_RESERVE_GB
    if vram_free_gb >= size_gb + 0.5:
        if avail_gb >= reserve:
            return True, (f"vram {vram_free_gb:.2f}GB >= weights {size_gb:.2f}+0.5 "
                          f"and ram {avail_gb:.2f}GB >= reserve {reserve}")
        return False, (f"vram fits weights but ram {avail_gb:.2f}GB < reserve {reserve}")
    need = round(size_gb + reserve, 2)
    if avail_gb >= need:
        return True, f"ram {avail_gb:.2f}GB >= need {need:.2f}GB (weights {size_gb:.2f} + reserve {reserve})"
    return False, (f"neither fits: vram {vram_free_gb:.2f}GB < weights {size_gb:.2f}+0.5 "
                   f"and ram {avail_gb:.2f}GB < need {need:.2f}GB")


def median(values: list[float]) -> float | None:
    vs = sorted(v for v in values if v is not None)
    return vs[len(vs) // 2] if vs else None


# ------------------------------------------------------------------ live probes
def _get(url: str, payload: dict | None = None, timeout: int = 900) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def server_up(timeout: int = 3) -> bool:
    try:
        _get(f"{API}/api/tags", timeout=timeout)
        return True
    except Exception:
        return False


def ensure_server(log_path: Path) -> dict:
    if server_up():
        return {"started": False, "reason": "already listening"}
    if not OLLAMA_EXE.exists():
        return {"started": False, "reason": f"binary missing: {OLLAMA_EXE}"}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(log_path, "ab")
    proc = subprocess.Popen([str(OLLAMA_EXE), "serve"],
                            stdout=fh, stderr=subprocess.STDOUT,
                            creationflags=CREATE_NO_WINDOW)
    for _ in range(60):
        time.sleep(1)
        if server_up():
            return {"started": True, "pid": proc.pid, "log": str(log_path)}
    return {"started": False, "reason": "serve did not answer within 60s", "pid": proc.pid}


def vram() -> dict | None:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=60)
        line = (out.stdout or "").strip().splitlines()[0]
        p = [x.strip() for x in line.split(",")]
        return {"name": p[0], "total_mb": int(p[1]), "used_mb": int(p[2]),
                "free_mb": int(p[3]), "util_pct": int(p[4]), "raw": line}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def available_gb() -> float:
    try:
        import psutil
        return round(psutil.virtual_memory().available / 2 ** 30, 2)
    except Exception:
        return 0.0


def ollama_ps() -> list[dict]:
    try:
        r = _get(f"{API}/api/ps", timeout=30)
    except Exception:
        return []
    return r.get("models") or []


def inventory() -> list[dict]:
    rows = []
    if not MANIFEST_ROOT.exists():
        return rows
    for path in sorted(MANIFEST_ROOT.rglob("*")):
        if not path.is_file():
            continue
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        size = estimate_size_bytes(manifest)
        rows.append({"name": model_name_from_manifest(path),
                     "size_bytes": size,
                     "size_gb": round(size / 2 ** 30, 2),
                     "manifest": str(path)})
    return sorted(rows, key=lambda r: r["size_gb"])


def bench_model(name: str, runs: int = 3) -> dict:
    rows = []
    for i in range(runs):
        t0 = time.time()
        r = _get(f"{API}/api/generate", {
            "model": name,
            "prompt": PROMPT,
            "stream": False,
            "keep_alive": 0,          # unload right after: this box is the user's desktop
            "options": {"temperature": 0, "num_predict": 128},
        })
        wall = time.time() - t0
        ev = r.get("eval_count") or 0
        evd = (r.get("eval_duration") or 0) / 1e9
        pev = r.get("prompt_eval_count") or 0
        pevd = (r.get("prompt_eval_duration") or 0) / 1e9
        rows.append({"run": i + 1, "tokens": ev,
                     "decode_tok_s": round(ev / evd, 2) if evd > 0 else None,
                     "prefill_tok_s": round(pev / pevd, 2) if pevd > 0 else None,
                     "wall_s": round(wall, 2),
                     "load_s": round((r.get("load_duration") or 0) / 1e9, 2)})
    return {"model": name, "runs": rows,
            "median_decode_tok_s": median([x["decode_tok_s"] for x in rows]),
            "median_prefill_tok_s": median([x["prefill_tok_s"] for x in rows]),
            "median_first_load_s": median([x["load_s"] for x in rows]),
            "command": GEN_CMD}


def run(tag: str = "manual", only: list[str] | None = None,
        reserve_gb: float = WORKING_SET_RESERVE_GB) -> dict:
    global WORKING_SET_RESERVE_GB
    WORKING_SET_RESERVE_GB = reserve_gb
    tmp = ROOT / ".codely-cli" / "tmp"
    started = ensure_server(tmp / "ollama-serve-bmc.log")
    inv = inventory()
    if only:
        wanted = {o.strip() for o in only}
        inv = [r for r in inv if r["name"] in wanted]
    vram_before = vram()
    avail_before = available_gb()

    results = []
    for row in inv:
        free_mb = (vram() or {}).get("free_mb") or 0
        ok, why = gate(available_gb(), free_mb / 1024, row["size_gb"])
        if not ok:
            results.append({"model": row["name"], "size_gb": row["size_gb"],
                            "status": "skipped_memory_gate", "gate": why})
            continue
        try:
            b = bench_model(row["name"])
            b.update({"size_gb": row["size_gb"], "status": "measured",
                      "gate": why})
            results.append(b)
        except Exception as exc:            # a failed measurement is data, not a crash
            results.append({"model": row["name"], "size_gb": row["size_gb"],
                            "status": "error", "gate": why,
                            "error": f"{type(exc).__name__}: {exc}"})
        finally:
            try:
                _get(f"{API}/api/generate", {"model": row["name"], "keep_alive": 0}, timeout=120)
            except Exception:
                pass

    doc = {
        "machine_id": "bm-c",
        "tag": tag,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "server": started,
        "hardware": {"gpu": vram_before, "ram_total_gb": 23.9,
                     "ram_available_gb": avail_before,
                     "ram_gate_reserve_gb": WORKING_SET_RESERVE_GB},
        "gpu_after": vram(),
        "inventory": inv,
        "results": results,
        "resident_after": ollama_ps(),
        "measurement_note": (
            "decode tok/s = eval_count / eval_duration from /api/generate. bm-c has "
            "NO resident production model (Ollama automation cleared 2026-10-17), so the "
            "first-load cost IS measured here (median_first_load_s) and each model is "
            "unloaded with keep_alive=0 immediately after. bm-a's bench deliberately "
            "cannot do this on its host."),
        "memory_gate_note": (
            "a model whose estimated weights + reserve do not fit in currently "
            "available RAM is skipped, not attempted: the desktop user shares this box."),
    }
    out = ROOT / "results" / "model_slots" / f"bench-bm-c-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    latest = out.parent / "bench-bm-c-latest.json"
    latest.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out),
                      "rows": [(r.get("model"), r.get("status"),
                                r.get("median_decode_tok_s")) for r in results],
                      "vram_before_mb": (vram_before or {}).get("used_mb")},
                     ensure_ascii=False))
    return doc


# ---------------------------------------------------------------------- selftest
def selftest() -> int:
    fails = []

    def leg(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    p = Path("/x/manifests/registry.ollama.ai/library/qwen3.5/9b-q4_K_M")
    leg("L1 manifest path -> model name", model_name_from_manifest(p) == "qwen3.5:9b-q4_K_M",
        model_name_from_manifest(p))

    m = {"layers": [
        {"mediaType": "application/vnd.ollama.image.model", "size": 3000},
        {"mediaType": "application/vnd.ollama.image.template", "size": 50},
        {"mediaType": "application/vnd.docker.container.image.v1+json", "size": 500},
        {"mediaType": "application/vnd.ollama.image.license", "size": 400},
    ]}
    leg("L2 size estimate skips config/license blobs", estimate_size_bytes(m) == 3050,
        str(estimate_size_bytes(m)))

    ok, why = gate(10.0, 2.0, 3.32)
    leg("L3 gate admits a model that fits in RAM", ok, why)
    ok2, why2 = gate(1.89, 2.0, 13.15)
    leg("L4 gate refuses an oversized model and says why", not ok2, why2)
    ok3, _ = gate(4.4, 2.0, 3.32)
    leg("L5 gate reserves working set, not just weights", not ok3,
        "3.32+1.5=4.82 > 4.40")
    ok4, why4 = gate(1.89, 14.9, 13.15)
    leg("L5b weights that fit whole in VRAM clear a RAM-tight box", ok4, why4)
    ok5, why5 = gate(1.0, 14.9, 13.15)
    leg("L5c a VRAM fit still needs the RAM working set", not ok5, why5)

    leg("L6 median is order-independent", median([3.0, 1.0, 2.0]) == 2.0)
    leg("L7 median ignores None", median([None, 5.0]) == 5.0)
    leg("L8 median of empty is None", median([]) is None)

    live = inventory()
    leg("L9 live inventory is non-empty and every row has a size",
        bool(live) and all(r["size_gb"] > 0 for r in live),
        f"{len(live)} models")

    print(f"\nselftest {'OK' if not fails else 'FAIL'}: {11 - len(fails)}/11")
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--tag", default="manual")
    ap.add_argument("--only", default="", help="comma-separated model names")
    ap.add_argument("--min-ram-reserve", type=float, default=WORKING_SET_RESERVE_GB,
                    help="RAM working-set reserve in GB (default %.1f)" % WORKING_SET_RESERVE_GB)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    only = [x for x in (a.only or "").split(",") if x.strip()] or None
    run(tag=a.tag, only=only, reserve_gb=a.min_ram_reserve)
    return 0


if __name__ == "__main__":
    sys.exit(main())