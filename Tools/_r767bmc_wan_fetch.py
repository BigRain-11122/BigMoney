# -*- coding: utf-8 -*-
"""r767 bm-c Wan2.2 fetch driver (MV-0001 sample-line video channel, per
O-20261008-1715/1755-bm-c + HANDOVER.md S3: Wan2.2-5B GGUF Q4 first-choice).
ModelScope mirror QuantStack/Wan2.2-TI2V-5B-GGUF (TI2V hybrid = t2v + i2v,
first-frame-anchor method compatible). 8-segment ranged parallel download,
per-part resume, byte-exact + magic + sha256 triple gate. Detached pythonw
zero-window run, self-logging to results/_r767bmc_wan_fetch.log (CEO 10%
CPU headroom law: 8 threads < 26-core cap, network-bound)."""
import hashlib
import os
import threading
import time
import urllib.request

LOG = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r767bmc_wan_fetch.log"
BASE = "https://modelscope.cn/models/QuantStack/Wan2.2-TI2V-5B-GGUF/resolve/master/"
SEGMENTS = 8

FILES = [
    {"url": BASE + "Wan2.2-TI2V-5B-Q4_K_M.gguf", "total": 3433116000,
     "out": r"D:\ComfyUI\ComfyUI\models\diffusion_models\Wan2.2-TI2V-5B-Q4_K_M.gguf",
     "magic": b"GGUF", "sha256": "95b19697b7f98e65b0a543640e9ca7b4dfec32e2a6e3731e8e10708be52655e2"},
    {"url": BASE + "VAE/Wan2.2_VAE.safetensors", "total": 1409400960,
     "out": r"D:\ComfyUI\ComfyUI\models\vae\Wan2.2_VAE.safetensors",
     "magic": None, "sha256": "e40321bd36b9709991dae2530eb4ac303dd168276980d3e9bc4b6e2b75fed156"},
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


def fetch_one(spec):
    out = spec["out"]
    total = spec["total"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out) and os.path.getsize(out) == total:
        log("SKIP (already complete): %s" % os.path.basename(out))
        return True
    per = total // SEGMENTS
    threads, results = [], [None] * SEGMENTS
    for i in range(SEGMENTS):
        s = i * per
        e = total - 1 if i == SEGMENTS - 1 else (s + per - 1)
        t = threading.Thread(target=seg_fetch,
                             args=(spec["url"], out + ".part%d" % i, s, e, i, results))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    log("%s parts: %s" % (os.path.basename(out), results))
    if any(r != "ok" and r != "done" for r in results):
        return False
    with open(out, "wb") as fh:
        for i in range(SEGMENTS):
            with open(out + ".part%d" % i, "rb") as pf:
                while True:
                    chunk = pf.read(1 << 22)
                    if not chunk:
                        break
                    fh.write(chunk)
    size = os.path.getsize(out)
    if size != total:
        log("FAIL size %d != %d: %s" % (size, total, out))
        return False
    if spec["magic"]:
        with open(out, "rb") as fh:
            head = fh.read(4)
        if head != spec["magic"]:
            log("FAIL magic %r: %s" % (head, out))
            return False
    h = hashlib.sha256()
    with open(out, "rb") as fh:
        while True:
            chunk = fh.read(1 << 22)
            if not chunk:
                break
            h.update(chunk)
    digest = h.hexdigest()
    if digest != spec["sha256"]:
        log("FAIL sha256 %s != %s: %s" % (digest[:16], spec["sha256"][:16], out))
        return False
    for i in range(SEGMENTS):
        try:
            os.remove(out + ".part%d" % i)
        except OSError:
            pass
    log("OK sha256-verified: %s (%d B)" % (out, size))
    return True


def main():
    log("=== wan fetch start (Q4_K_M + VAE, 8-seg parallel) ===")
    ok = True
    for spec in FILES:
        try:
            ok = fetch_one(spec) and ok
        except Exception as exc:
            log("EXC %s: %r" % (os.path.basename(spec["out"]), exc))
            ok = False
    log("=== wan fetch done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
