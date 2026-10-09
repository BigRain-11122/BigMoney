# -*- coding: utf-8 -*-
"""r818 bm-c H3 T2V ignite: detached long-runner (O-20261009-1746 bm-c lane).

Phase 1 -- manifest gate: poll byte-verify of all 5 H3 files (r815 driver
still finishing files 3-5; up to 45 min patience).
Phase 2 -- GPU/RAM handoff per the O-1746 clause (CEO-direct-order priority:
pause in-flight batches + unpin resident ollama, restore in order after):
  a. disable MiniGameOllamaServe + MiniGameOllamaKeepWarm (5-min keepwarm
     would otherwise re-pin the 35b within minutes -- bm-a 10-09 recipe)
  b. taskkill llama-server.exe (frees ~13GB VRAM + host RAM)
  c. kill the W17 screen shard python (trial_labor_w17.py screen -- RAM
     relief; autofill resubmit loop relaunches it from checkpoint after)
Phase 3 -- run Tools/_r818bmc_h3_t2v_client.py (768P 5s T2V, pure visual
per CEO audio ban 2026-10-09 19:0x).
Phase 4 -- restore in order: re-enable both ollama tasks; W17 resumed by
the autofill loop naturally. Everything logged to
results/_r818bmc_h3_t2v_ignite.log (ASCII-safe prints).
All native exes via CREATE_NO_WINDOW (U060 zero-flash law)."""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r818bmc_h3_t2v_ignite.log")
CLIENT = os.path.join(ROOT, "Tools", "_r818bmc_h3_t2v_client.py")
MODELS = r"D:\ComfyUI\ComfyUI\models"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
MANIFEST = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors", 16825666232),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", 15687142551),
    ("vae/minimax_h3_video_vae_fp16.safetensors", 5207808496),
    ("vae/minimax_h3_audio_vae_fp32.safetensors", 605254808),
    ("loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", 1956192992),
]


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd, timeout=120):
    p = subprocess.run(cmd, capture_output=True, creationflags=CNW,
                       timeout=timeout)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace").strip()


def manifest_missing():
    miss = []
    for rel, target in MANIFEST:
        p = os.path.join(MODELS, rel)
        if not os.path.isfile(p) or os.path.getsize(p) != target:
            miss.append(rel)
    return miss


def vram_free_mib():
    rc, out = run(["nvidia-smi", "--query-gpu=memory.free",
                   "--format=csv,noheader,nounits"], timeout=30)
    try:
        return int(out.splitlines()[0]) if rc == 0 else -1
    except Exception:
        return -1


def ram_free_mb():
    rc, out = run(["wmic", "OS", "get", "FreePhysicalMemory", "/value"],
                  timeout=30)
    try:
        return int(out.split("=")[1]) // 1024 if rc == 0 else -1
    except Exception:
        return -1


def kill_w17_shards():
    # python.exe-only filter: wmic's own commandline never matches name filter
    rc, out = run(["wmic", "process", "where",
                   "name='python.exe' and commandline like '%trial_labor_w17%'",
                   "get", "processid"], timeout=60)
    pids = []
    for tok in out.replace("\r", "\n").split():
        if tok.isdigit():
            pids.append(tok)
    killed = []
    for pid in pids:
        krc, _ = run(["taskkill", "/PID", pid, "/F"], timeout=60)
        killed.append((pid, krc))
        log("w17 shard pid %s kill rc=%d (autofill resumes from checkpoint)"
            % (pid, krc))
    return killed


def main():
    log("ignite start: manifest gate (max 45 min patience)")
    t0 = time.time()
    while True:
        miss = manifest_missing()
        if not miss:
            log("MANIFEST 5/5 byte-verified after %.0f min" %
                ((time.time() - t0) / 60))
            break
        if time.time() - t0 > 45 * 60:
            log("GATE TIMEOUT, still missing: %s" % json.dumps(miss))
            return 2
        time.sleep(30)
    # phase 2: GPU/RAM handoff
    log("handoff: vram_free=%dMiB ram_free=%dMB" %
        (vram_free_mib(), ram_free_mb()))
    for tn in ("MiniGameOllamaServe", "MiniGameOllamaKeepWarm"):
        rc, out = run(["schtasks", "/change", "/tn", tn, "/disable"])
        log("disable %s rc=%d" % (tn, rc))
    rc, out = run(["taskkill", "/IM", "llama-server.exe", "/F"])
    log("kill llama-server rc=%d out=%s" % (rc, out[:120]))
    time.sleep(8)
    kill_w17_shards()
    time.sleep(8)
    log("post-handoff: vram_free=%dMiB ram_free=%dMB" %
        (vram_free_mib(), ram_free_mb()))
    # phase 3: T2V client
    log("T2V client launch")
    p = subprocess.run([sys.executable, CLIENT], cwd=ROOT,
                       capture_output=True, creationflags=CNW,
                       timeout=90 * 60)
    out = (p.stdout or b"").decode("utf-8", "replace")
    for line in out.splitlines():
        log("client: %s" % line)
    if p.stderr:
        log("client stderr tail: %s" % p.stderr.decode("utf-8", "replace")[-400:])
    log("client exit rc=%d" % p.returncode)
    # phase 4: restore in order
    for tn in ("MiniGameOllamaServe", "MiniGameOllamaKeepWarm"):
        rc, out = run(["schtasks", "/change", "/tn", tn, "/enable"])
        log("re-enable %s rc=%d" % (tn, rc))
    log("restore done: ollama tasks re-enabled; W17 resumes via autofill")
    log("ignite exit rc=%d" % (0 if p.returncode == 0 else p.returncode))
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main())
