"""r832 bm-b: H3 int4 DiT fetcher from rockerBOO/minimax-h3-nvfp4-convrot.

r831 fetch died on this file (Comfy-Org/MiniMax-H3 has no int4_simple variant
-> ModelScope 500; HF direct GFW-blocked). Root-fix per Danshiduzhi 8g-deploy
README: the exact file `minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors`
lives in rockerBOO/minimax-h3-nvfp4-convrot (HF), reachable via hf-mirror.com.
Resume-capable (Range), detached, status JSON for later-round harvest.
Run: python results/_r832bmb_dit_fetch.py
"""
import json
import os
import sys
import time
import urllib.request

BASE = r"C:\Fluxgroup\MiniGame\Tools\ComfyUI_windows_portable\ComfyUI\models\diffusion_models"
LOG = os.path.join(os.environ["TEMP"], "r832_dit_fetch.log")
STATUS = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r832bmb_dit_fetch_status.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SRC = "https://hf-mirror.com/rockerBOO/minimax-h3-nvfp4-convrot/resolve/main/"

FILES = [
    ("minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors", 18064290304),
    ("minimax_h3_layer_config_int4_convrot.json", 0),
]


def log(msg):
    line = time.strftime("%H:%M:%S") + " " + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def head_len(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return -1


def fetch(url, dst):
    part = dst + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    total = head_len(url)
    if total > 0 and have >= total:
        os.replace(part, dst)
        return total
    req = urllib.request.Request(url, headers=dict(UA))
    if have > 0:
        req.add_header("Range", "bytes=%d-" % have)
    with urllib.request.urlopen(req, timeout=120) as r, open(part, "ab") as f:
        t0 = time.time()
        while True:
            chunk = r.read(1 << 22)
            if not chunk:
                break
            f.write(chunk)
            if int(time.time() - t0) % 60 == 0:
                log("... %s %d/%d B" % (os.path.basename(dst), os.path.getsize(part), total))
    sz = os.path.getsize(part)
    if total > 0 and sz < total:
        return -1
    os.replace(part, dst)
    return sz


def main():
    status = {"round": "r832", "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "files": {}, "done": False}
    for name, hint in FILES:
        dst = os.path.join(BASE, name)
        try:
            os.makedirs(BASE, exist_ok=True)
        except Exception as e:
            log("MKDIR FAIL: %r" % e)
            status["files"][name] = {"state": "mkdir_fail"}
            continue
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            status["files"][name] = {"state": "exists", "size": os.path.getsize(dst)}
            log("SKIP exists %s" % name)
            continue
        url = SRC + name
        log("TRY %s" % url)
        try:
            sz = fetch(url, dst)
            if sz > 0:
                log("OK %s (%d B)" % (name, sz))
                status["files"][name] = {"state": "done", "size": sz, "url": url}
            else:
                log("INCOMPLETE %s (resume next run)" % name)
                status["files"][name] = {"state": "partial", "url": url}
        except Exception as e:
            log("FAIL %s: %r" % (url, e))
            status["files"][name] = {"state": "failed", "err": repr(e)[:300], "url": url}
    status["done"] = all(v.get("state") in ("done", "exists") for v in status["files"].values()) and len(status["files"]) == len(FILES)
    status["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(status, open(STATUS, "w", encoding="utf-8"), ensure_ascii=True, indent=1)
    log("STATUS written done=%s" % status["done"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
