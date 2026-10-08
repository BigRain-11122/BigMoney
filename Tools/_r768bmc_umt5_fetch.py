# -*- coding: utf-8 -*-
"""r768 bm-c umt5-xxl encoder fetch driver (MV-0001 channel, per HANDOVER.md
S3 + r767 next-pointer item-1). ModelScope city96/umt5-xxl-encoder-gguf
Q4_K_M (matches diffusion Q4_K_M tier; ComfyUI-GGUF CLIPLoaderGGUF consumes).
8-segment ranged parallel, per-part resume, byte-exact + magic + sha256
triple gate. Detached pythonw zero-window run, self-logging to
results/_r768bmc_umt5_fetch.log (CEO 10% CPU headroom law: 8 threads)."""
import hashlib
import os
import threading
import time
import urllib.request

LOG = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r768bmc_umt5_fetch.log"
URL = "https://modelscope.cn/models/city96/umt5-xxl-encoder-gguf/resolve/master/umt5-xxl-encoder-Q4_K_M.gguf"
TOTAL = 3655145312
OUT = r"D:\ComfyUI\ComfyUI\models\text_encoders\umt5-xxl-encoder-Q4_K_M.gguf"
SHA256 = "17cf97a5bbbc60a646d6105b832b6f657ce904a8a1ad970e4b59df0c67584a40"
SEGMENTS = 8


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
        with urllib.request.urlopen(req, timeout=120) as resp, open(path, "ab") as fh:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        final = os.path.getsize(path)
        results[idx] = "ok" if final >= want else "short(%d/%d)" % (final, want)
    except Exception as exc:
        results[idx] = "err:" + repr(exc)[:120]


def main():
    log("=== umt5 fetch start (Q4_K_M %d B, 8-seg parallel) ===" % TOTAL)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT) and os.path.getsize(OUT) == TOTAL:
        log("SKIP (already complete)")
        return
    per = TOTAL // SEGMENTS
    threads, results = [], [None] * SEGMENTS
    for i in range(SEGMENTS):
        s = i * per
        e = TOTAL - 1 if i == SEGMENTS - 1 else (s + per - 1)
        t = threading.Thread(target=seg_fetch,
                             args=(URL, OUT + ".part%d" % i, s, e, i, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
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
        head = fh.read(4)
    if head != b"GGUF":
        log("FAIL magic %r" % head)
        return
    h = hashlib.sha256()
    with open(OUT, "rb") as fh:
        while True:
            chunk = fh.read(1 << 22)
            if not chunk:
                break
            h.update(chunk)
    digest = h.hexdigest()
    if digest != SHA256:
        log("FAIL sha256 %s != %s" % (digest[:16], SHA256[:16]))
        return
    for i in range(SEGMENTS):
        try:
            os.remove(OUT + ".part%d" % i)
        except OSError:
            pass
    log("OK sha256-verified: %s (%d B)" % (OUT, size))


if __name__ == "__main__":
    main()
