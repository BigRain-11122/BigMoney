# -*- coding: utf-8 -*-
"""r818 bm-c MiniMax-H3 weight downloader phase-2 (files 3-5) -- takes over
from the r815 driver, which was retired at ZERO-byte file-3 progress
(r815 blind face: 1MB chunks + socket-timeout reset per recv = trickling
connections never break, threads hang for hours on ~0.1MB/s admissions;
files 1-2 already assembled+verified so the takeover loses nothing).

Mechanism unchanged from r815 (8-segment parallel ranged download +
per-part size resume + concat + byte verify + already-complete skip for
files 1-2). ONE fix family added:
FIX-A (stall-break): per-read progress check -- if a read() call yields
  nothing for STALL_SEC (45s) or the connection delivers under
  STALL_MIN_BYTES in STALL_SEC, abort + reconnect (fresh admission
  chance instead of riding a dead trickle forever).
FIX-B (visibility): 256KB chunks (4x faster part-file growth feedback).
State: results/_r818bmc_h3_download2_state.json
Receipt: results/_r818bmc_h3_download2_receipt.json"""
import json
import os
import threading
import time
import urllib.request
from datetime import datetime, timezone, timedelta

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MODELS = r"D:\ComfyUI\ComfyUI\models"
STATE = os.path.join(R, "results", "_r818bmc_h3_download2_state.json")
RECEIPT = os.path.join(R, "results", "_r818bmc_h3_download2_receipt.json")
PART_DIR = os.path.join(MODELS, "_h3_parts")
SEG = 8
CHUNK = 256 * 1024
STALL_SEC = 45
STALL_MIN_BYTES = 256 * 1024
SAVE_LOCK = threading.Lock()
STATE_REF = [None]

FILES = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors",
     16825666232,
     "https://hf-mirror.com/rockerBOO/minimax-h3-nvfp4-convrot/resolve/main/"
     "minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors"),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
     15687142551,
     "https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/text_encoders/"
     "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("vae/minimax_h3_video_vae_fp16.safetensors",
     5207808496,
     "https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/vae/"
     "minimax_h3_video_vae_fp16.safetensors"),
    ("vae/minimax_h3_audio_vae_fp32.safetensors",
     605254808,
     "https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/vae/"
     "minimax_h3_audio_vae_fp32.safetensors"),
    ("loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors",
     1956192992,
     "https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/loras/"
     "minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors"),
]
MANIFEST_TOTAL = sum(t for (_, t, _) in FILES)


def now_iso():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(
        timespec="seconds")


def save_state(obj):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def fetch_range(url, start, end, out_path, fstate, key):
    """Ranged fetch with resume + FIX-A stall-break: a connection that
    delivers under STALL_MIN_BYTES within STALL_SEC is aborted (fresh
    reconnect) instead of riding a dead trickle forever."""
    last_err = None
    while True:
        have = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        want = end - start + 1
        if have >= want:
            with SAVE_LOCK:
                fstate.setdefault("parts", {})[key] = have
                save_state(STATE_REF[0])
            return True
        try:
            req = urllib.request.Request(
                url, headers={"Range": "bytes=%d-%d" % (start + have, end),
                              "User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status not in (200, 206):
                    raise IOError("http %d" % r.status)
                with open(out_path, "ab") as f:
                    while True:
                        t0 = time.time()
                        buf = r.read(CHUNK)
                        dt = time.time() - t0
                        if not buf:
                            raise IOError("eof mid-range at %d/%d"
                                          % (have, want))
                        f.write(buf)
                        have += len(buf)
                        if dt > STALL_SEC and len(buf) < STALL_MIN_BYTES:
                            raise IOError("stall-break %.1fs/%dB" %
                                          (dt, len(buf)))
        except Exception as e:
            txt = repr(e)[:140]
            if txt != last_err:
                last_err = txt
                with SAVE_LOCK:
                    fstate.setdefault("errors", {})[key] = {
                        "ts": now_iso(), "err": txt}
                    save_state(STATE_REF[0])
            time.sleep(3)


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
                           "target": target, "parts": {}, "errors": {}}
    save_state(state)
    fstate = state["files"][rel]
    ths = []
    for (s, e, pp) in bounds:
        key = os.path.basename(pp)
        t = threading.Thread(target=fetch_range,
                             args=(url, s, e, pp, fstate, key))
        t.start()
        ths.append(t)
    for t in ths:
        t.join()
    with SAVE_LOCK:
        save_state(state)
    ok = all(os.path.getsize(pp) == (e - s + 1)
             for (s, e, pp) in bounds if os.path.exists(pp))
    if not ok:
        state["files"][rel]["status"] = "incomplete-restartable"
        save_state(state)
        return False
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
            try:
                os.remove(pp)
            except OSError:
                pass
        state["files"][rel] = {"status": "complete", "bytes": got,
                               "ts": now_iso()}
        save_state(state)
        return True
    state["files"][rel]["status"] = "concat-mismatch got=%d" % got
    save_state(state)
    return False


def main():
    state = {"started": now_iso(), "driver": "Tools/_r818bmc_h3_download2.py",
             "fix_release": "r818b FIX-A stall-break + FIX-B 256KB chunks "
                            "(r815 retired at zero-byte file-3 trickle-hang)",
             "manifest_bytes_total": MANIFEST_TOTAL, "files": {}}
    STATE_REF[0] = state
    save_state(state)
    allok = True
    for (rel, target, url) in FILES:
        allok = download_one(rel, target, url, state) and allok
    receipt = {"order": "O-20261009-1746", "machine": "bm-c",
               "driver": "r818 phase-2 (files 3-5; files 1-2 from r815 "
                         "verified + skipped)",
               "manifest_bytes_total": MANIFEST_TOTAL,
               "all_complete": allok, "done_ts": now_iso()}
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("H3 r818 driver exit all_complete=%s" % allok)
    return 0 if allok else 2


if __name__ == "__main__":
    raise SystemExit(main())
