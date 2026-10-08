# -*- coding: utf-8 -*-
"""r768 bm-c: Wan2.2 CLIP vision tower fetch (clip_vision_h.safetensors,
Comfy-Org Wan_2.1_ComfyUI_Repackaged split_files canonical, 1,264,219,396 B).
Last missing hard dependency of the Wan2.2-TI2V-5B i2v chain (probe hits:
modelscope Comfy-Org mirror + hf-mirror fallback). 8-segment ranged
parallel with per-part resume (clone credit: _r768bmc_umt5_fetch.py
channel pattern), gates = byte-exact size + safetensors header parse +
sha256 recorded to log. Detached pythonw zero-window, self-logging.
CEO 10% CPU headroom law: 8 threads."""
import hashlib
import json
import os
import struct
import threading
import time
import urllib.request

LOG = (r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"
       r"\_r768bmc_clipvision_fetch.log")
OUT = r"D:\ComfyUI\ComfyUI\models\clip_vision\clip_vision_h.safetensors"
TOTAL = 1264219396
SEGMENTS = 8
URLS = [
    "https://modelscope.cn/models/Comfy-Org/Wan_2.1_ComfyUI_Repackaged"
    "/resolve/master/split_files/clip_vision/clip_vision_h.safetensors",
    "https://hf-mirror.com/Comfy-Org/Wan_2.1_ComfyUI_Repackaged"
    "/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
]


def log(msg):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))


def seg_fetch(url, path, start, end, idx, results):
    try:
        have = os.path.getsize(path) if os.path.exists(path) else 0
        want = end - start + 1
        if have >= want:
            results[idx] = "done"
            return
        req = urllib.request.Request(url)
        req.add_header("Range", "bytes=%d-%d" % (start + have, end))
        with urllib.request.urlopen(req, timeout=120) as resp, \
                open(path, "ab") as fh:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        final = os.path.getsize(path)
        results[idx] = "ok" if final >= want else "short(%d/%d)" % (final,
                                                                    want)
    except Exception as exc:
        results[idx] = "err:" + repr(exc)[:120]


def main():
    log("=== clip_vision_h fetch start (%d B, 8-seg parallel) ===" % TOTAL)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT) and os.path.getsize(OUT) == TOTAL:
        log("SKIP (already complete)")
        return
    per = TOTAL // SEGMENTS
    threads, results = [], [None] * SEGMENTS
    for i in range(SEGMENTS):
        s = i * per
        e = TOTAL - 1 if i == SEGMENTS - 1 else (s + per - 1)
        t = threading.Thread(
            target=seg_fetch,
            args=(URLS[0], OUT + ".part%d" % i, s, e, i, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    if any(r not in ("ok", "done") for r in results):
        log("primary channel parts: %s -> retry hf-mirror" % results)
        threads, results2 = [], [None] * SEGMENTS
        for i in range(SEGMENTS):
            s = i * per
            e = TOTAL - 1 if i == SEGMENTS - 1 else (s + per - 1)
            if results[i] in ("ok", "done"):
                continue
            t = threading.Thread(
                target=seg_fetch,
                args=(URLS[1], OUT + ".part%d" % i, s, e, i, results2))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        for i in range(SEGMENTS):
            if results[i] not in ("ok", "done"):
                results[i] = results2[i] if results2[i] else "dead"
    log("parts: %s" % results)
    if any(r != "ok" and r != "done" for r in results):
        log("FAIL parts incomplete")
        return
    with open(OUT, "wb") as fh:
        for i in range(SEGMENTS):
            with open(OUT + ".part%d" % i, "rb") as pf:
                while True:
                    chunk = pf.read(1 << 22)
                    if not chunk:
                        break
                    fh.write(chunk)
    size = os.path.getsize(OUT)
    if size != TOTAL:
        log("FAIL size %d != %d" % (size, TOTAL))
        return
    with open(OUT, "rb") as fh:
        head8 = fh.read(8)
        hlen = struct.unpack("<Q", head8)[0]
        hdr = fh.read(min(hlen, 4096))
    try:
        meta = json.loads(hdr.rstrip(b"\x00 "))
        ok_magic = isinstance(meta, dict) and len(meta) > 0
    except Exception:
        ok_magic = False
    if not ok_magic:
        log("FAIL safetensors header parse hlen=%d" % hlen)
        return
    h = hashlib.sha256()
    with open(OUT, "rb") as fh:
        while True:
            chunk = fh.read(1 << 22)
            if not chunk:
                break
            h.update(chunk)
    digest = h.hexdigest()
    log("OK size+magic verified, sha256=%s (%d B) -> %s"
        % (digest, size, OUT))
    for i in range(SEGMENTS):
        try:
            os.remove(OUT + ".part%d" % i)
        except OSError:
            pass


if __name__ == "__main__":
    main()
