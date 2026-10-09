# -*- coding: utf-8 -*-
"""r818 bm-c H3 local T2V 768P smoke-test client (O-20261009-1746 bm-c lane).

Adapted from the canon client cph4/fleet/h3-local-test/h3_t2v_client.py
(bm-a 480P precedent) for bm-c paths + 768P class + CEO audio-track ban
(2026-10-09 19:0x: no VAEDecodeAudio / no CreateVideo audio input -- pure
visual output; audio VAE file stays on disk as manifest integrity but is
NOT wired into any film pipeline).

Pre-submit gate: byte-verify all 5 H3 files against the r815 manifest
(any miss = honest exit 2, zero submission).
During run: nvidia-smi VRAM sampler thread (peak recorded).
After run: copy MP4 to group-tree outbound staging + evidence JSON to
results/_r818bmc_h3_t2v_evidence.json.
Usage: python Tools/_r818bmc_h3_t2v_client.py [--seed N] [--wait S]
ASCII-only prints (GBK console safety)."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MODELS = r"D:\ComfyUI\ComfyUI\models"
WF_PATH = r"K:\Fluxgroup\FluxGroup\cph4\fleet\h3-local-test\h3_t2v_local_768p_bmc.json"
COMFY_OUTPUT = os.path.join(r"D:\ComfyUI\ComfyUI\output", "h3_local_test")
OUT_STAGE = os.path.join(R, "results", "_r818bmc_h3_outbound_stage")
EVIDENCE = os.path.join(R, "results", "_r818bmc_h3_t2v_evidence.json")
CLIENT_ID = "bmc-h3-local-test"
SERVER = "http://127.0.0.1:8188"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

MANIFEST = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors", 16825666232),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", 15687142551),
    ("vae/minimax_h3_video_vae_fp16.safetensors", 5207808496),
    ("vae/minimax_h3_audio_vae_fp32.safetensors", 605254808),
    ("loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", 1956192992),
]


def http_json(url, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def verify_manifest():
    missing = []
    for rel, target in MANIFEST:
        p = os.path.join(MODELS, rel)
        if not os.path.isfile(p) or os.path.getsize(p) != target:
            have = os.path.getsize(p) if os.path.isfile(p) else -1
            missing.append((rel, have, target))
    return missing


def vram_sampler(stop, peaks):
    while not stop["stop"]:
        try:
            p = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used",
                 "--format=csv,noheader,nounits"],
                capture_output=True, creationflags=CNW, timeout=10)
            v = int(p.stdout.decode("utf-8", "replace").strip().splitlines()[0])
            peaks.append(v)
        except Exception:
            pass
        time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261009)
    ap.add_argument("--wait", type=int, default=7200)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    miss = verify_manifest()
    if miss:
        print("MANIFEST INCOMPLETE (%d):" % len(miss))
        for rel, have, target in miss:
            print("  %s have=%d want=%d (%.1f%%)" % (rel, have, target,
                  100.0 * max(have, 0) / target))
        return 2

    with open(WF_PATH, "r", encoding="utf-8") as f:
        wf = json.load(f)
    wf["10"]["inputs"]["noise_seed"] = args.seed
    print("MANIFEST 5/5 byte-verified; workflow nodes=%d seed=%d" % (
        len(wf), args.seed))
    if args.dry_run:
        return 0

    t0 = time.time()
    resp = http_json(SERVER + "/prompt", {"prompt": wf,
                                          "client_id": CLIENT_ID})
    pid = resp.get("prompt_id")
    if not pid:
        print("SUBMIT FAILED: %s" % json.dumps(resp)[:300])
        return 2
    print("SUBMITTED prompt_id=%s" % pid)

    peaks = [0]
    stop = {"stop": False}
    th = threading.Thread(target=vram_sampler, args=(stop, peaks))
    th.start()
    try:
        while True:
            time.sleep(10)
            if time.time() - t0 > args.wait:
                print("TIMEOUT after %ds" % args.wait)
                return 5
            try:
                hist = http_json(SERVER + "/history/" + pid, timeout=15)
            except urllib.error.URLError:
                print("[%4ds] poll err (busy), retry" % (time.time() - t0))
                continue
            entry = hist.get(pid)
            if entry is None:
                print("[%4ds] running... vram_peak=%dMiB" % (
                    time.time() - t0, max(peaks)))
                continue
            status = entry.get("status", {})
            if not status.get("completed", False):
                print("NOT COMPLETED: %s" % json.dumps(status)[:400])
                return 3
            outputs = entry.get("outputs", {})
            saved = []
            for node_out in outputs.values():
                for item in (node_out.get("videos") or []):
                    saved.append(item)
            dur = time.time() - t0
            print("DONE in %.0fs vram_peak=%dMiB saved=%s" % (
                dur, max(peaks), json.dumps(saved)[:200]))
            os.makedirs(OUT_STAGE, exist_ok=True)
            os.makedirs(COMFY_OUTPUT, exist_ok=True)
            copied = []
            for item in saved:
                src = os.path.join(r"D:\ComfyUI\ComfyUI\output",
                                   item.get("subfolder", "") or "",
                                   item.get("filename", ""))
                if os.path.isfile(src):
                    dst = os.path.join(OUT_STAGE, item.get("filename", ""))
                    shutil.copy2(src, dst)
                    copied.append((dst, os.path.getsize(dst)))
            ev = {"order": "O-20261009-1746", "machine": "bm-c",
                  "lane": "local H3 T2V 768P 5s 16:9-ish (1344x768) 4-step "
                          "turbo, pure visual per CEO audio ban 2026-10-09",
                  "prompt_id": pid, "seed": args.seed,
                  "duration_sec": round(dur, 1),
                  "vram_peak_mib": max(peaks),
                  "workflow": WF_PATH,
                  "delivered": [{"path": p, "bytes": b} for p, b in copied],
                  "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
            with open(EVIDENCE, "w", encoding="utf-8") as f:
                json.dump(ev, f, ensure_ascii=False, indent=1)
            for p, b in copied:
                print("DELIVERED: %s (%d bytes)" % (p, b))
            return 0 if copied else 4
    finally:
        stop["stop"] = True
        th.join()


if __name__ == "__main__":
    sys.exit(main())
