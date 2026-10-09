# -*- coding: utf-8 -*-
"""r814 bm-c MiniMax-H3 weight downloader (O-20261009-1746 mainline,
Danshiduzhi/minimax-h3-8g-deploy manifest, hf-mirror.com URLs -- the only
reachable HF channel on this machine per 2026-10-02 channel recon; hf.co
unreachable, ModelScope no H3 mirror 404 per r813 recon).
Paradigm = dl_qwen36.ps1 8-segment parallel ranged download + per-part
size resume + concat + byte-count verify (deploy repo's own verify is
byte-exact, mirrors that contract). Pure urllib (zero deps), 8 threads per
file for files >512MB else single stream. Progress -> state json updated
per part completion; final receipt on all-done. Long-runner: ignite via
_r814bmc_h3_ignite.py (DETACHED_PROCESS -- survives the 25-min wrapper
kill window; receipt verified in-round or next round, bm-a r919 law)."""
import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone, timedelta

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MODELS = r"D:\ComfyUI\ComfyUI\models"
STATE = os.path.join(R, "results", "_r814bmc_h3_download_state.json")
RECEIPT = os.path.join(R, "results", "_r814bmc_h3_download_receipt.json")
PART_DIR = os.path.join(MODELS, "_h3_parts")
SEG = 8
CHUNK = 1 << 20

# relpath | target bytes | url  (verbatim from scripts/download_weights.sh)
FILES = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors",
     16825666232,
     "https://hf-mirror.com/rockerBOO/minimax-h3-nvfp4-convrot/resolve/main/"
     "minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors"),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
     156871142551,
     "https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/"
     "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("vae/minimax_h3_video_vae_fp16.safetensors",
     5207808496,
     "https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/vae/"
     "minimax_h3_video_vae_fp16.safetensors"),
    ("vae/minimax_h3_audio_vae_fp32.safetensors",
     605254808,
     "https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/vae/"
     "minimax_h3_audio_vae_fp32.safetensors"),
    ("loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors",
     1956192992,
     "https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main/loras/"
     "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors"),
]


def now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(
        timespec="seconds")


def save_state(obj):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def fetch_range(url, start, end, out_path, stop_flag, state, key):
    """Append-mode ranged fetch with infinite self-healing retry.
    Resume = part file size; server must honor Range (hf-mirror proven)."""
    while not stop_flag["stop"]:
        have = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        want = end - start + 1
        if have >= want:
            state["parts"][key] = have
            return True
        try:
            req = urllib.request.Request(
                url, headers={"Range": "bytes=%d-%d" % (start + have, end),
                              "User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=(30, 90)) as r:
                if r.status not in (200, 206):
                    raise IOError("http %d" % r.status)
                with open(out_path, "ab") as f:
                    while True:
                        if stop_flag["stop"]:
                            return False
                        buf = r.read(CHUNK)
                        if not buf:
                            break
                        f.write(buf)
        except Exception:
            time.sleep(5)
    return False


def download_one(rel, target, url, state):
    final = os.path.join(MODELS, rel)
    os.makedirs(os.path.dirname(final), exist_ok=True)
    if os.path.exists(final) and os.path.getsize(final) == target:
        state["files"][rel] = {"status": "already-complete",
                               "bytes": target, "ts": now_iso()}
        save_state(state)
        return True
    segs = SEG if target > (512 << 20) else 1
    os.makedirs(PART_DIR, exist_ok=True)
    stem = os.path.join(PART_DIR, os.path.basename(rel))
    bounds = []
    per = target // segs
    for i in range(segs):
        s = i * per
        e = target - 1 if i == segs - 1 else (i + 1) * per - 1
        bounds.append((s, e, "%s.part%d" % (stem, i)))
    state["files"][rel] = {"status": "in-flight", "segs": segs,
                           "target": target, "parts": {}}
    state["parts"] = state["files"][rel].setdefault("parts", {})
    save_state(state)
    stop_flag = {"stop": False}
    ths = []
    for (s, e, pp) in bounds:
        key = os.path.basename(pp)
        t = threading.Thread(target=fetch_range,
                             args=(url, s, e, pp, stop_flag, state["files"][rel],
                                   key))
        t.start()
        ths.append(t)
    for t in ths:
        t.join()
    ok = all(os.path.getsize(pp) == (e - s + 1)
             for (s, e, pp) in bounds if os.path.exists(pp))
    if not ok:
        state["files"][rel]["status"] = "incomplete-restartable"
        save_state(state)
        return False
    # concat + byte verify
    with open(final, "wb") as out:
        for (s, e, pp) in bounds:
            with open(pp, "rb") as f:
                while True:
                    buf = f.read(8 << 20)
                    if not buf:
                        break
                    out.write(buf)
    got = os.path.getsize(final)
    if got == target:
        for (_, _, pp) in bounds:
            os.remove(pp)
        state["files"][rel] = {"status": "complete", "bytes": got,
                               "ts": now_iso()}
        save_state(state)
        return True
    state["files"][rel]["status"] = "concat-mismatch got=%d" % got
    save_state(state)
    return False


def main():
    state = {"started": now_iso(), "files": {}, "parts": {}}
    save_state(state)
    # disk pre-check (need 40.3GB; 376.9GB free at r813 recon)
    try:
        import shutil
        free = shutil.disk_usage(os.path.splitdrive(MODELS)[0] + "\\").free
        state["disk_free_bytes"] = free
        save_state(state)
        if free < (80 << 30):
            state["abort"] = "disk low: %d" % free
            save_state(state)
            print("ABORT disk low %d" % free)
            return 3
    except Exception:
        pass
    allok = True
    for (rel, target, url) in FILES:
        ok = download_one(rel, target, url, state)
        allok = allok and ok
    receipt = {"order": "O-20261009-1746", "machine": "bm-c",
               "manifest": [{"rel": r, "bytes": t, "url": u}
                            for (r, t, u) in FILES],
               "models_dir": MODELS, "done_ts": now_iso(),
               "all_complete": allok, "state_file": STATE}
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("H3 download driver exit all_complete=%s" % allok)
    return 0 if allok else 2


if __name__ == "__main__":
    raise SystemExit(main())
