"""r831 bm-b: H3 480P animatic lane model fetcher (CEO order 10-10 11:5x 修订二②).

Downloads the 4 model files referenced by h3_i2v_local_480p_v4.json into
bm-b ComfyUI portable models dirs. Resume-capable (Range), multi-candidate
URLs (ModelScope primary per bm-c live-fire recipe, HF fallback), detached
(CREATE_NO_WINDOW parent), status JSON for harvest by later rounds.
Run: python results/_r831bmb_h3_fetch.py
"""
import json
import os
import sys
import time
import urllib.request

BASE = r"C:\Fluxgroup\MiniGame\Tools\ComfyUI_windows_portable\ComfyUI\models"
LOG = os.path.join(os.environ["TEMP"], "r831_h3_fetch.log")
STATUS = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r831bmb_h3_fetch_status.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

MS = "https://modelscope.cn/models/Comfy-Org/MiniMax-H3/resolve/master/"
HF = "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/"

FILES = [
    ("minimax_h3_fl2va_pruned_int4_convrot_simple.safetensors", "diffusion_models",
     [MS + "diffusion_models/", MS, HF + "diffusion_models/", HF]),
    ("minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors", "loras",
     [MS + "loras/", MS, HF + "loras/", HF]),
    ("qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "text_encoders",
     [MS + "text_encoders/", MS, HF + "text_encoders/", HF]),
    ("minimax_h3_video_vae_fp16.safetensors", "vae",
     [MS + "vae/", MS, HF + "vae/", HF]),
]


def log(msg):
    line = time.strftime("%H:%M:%S") + " " + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def head_ok(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception as e:
        return -1


def fetch(url, dst):
    part = dst + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    total = head_ok(url)
    if total > 0 and have >= total:
        os.replace(part, dst)
        return total
    req = urllib.request.Request(url, headers=dict(UA))
    if have > 0:
        req.add_header("Range", "bytes=%d-" % have)
    with urllib.request.urlopen(req, timeout=60) as r, open(part, "ab") as f:
        while True:
            chunk = r.read(1 << 22)
            if not chunk:
                break
            f.write(chunk)
    sz = os.path.getsize(part)
    if total > 0 and sz < total:
        return -1  # incomplete, keep .part for resume
    os.replace(part, dst)
    return sz


def main():
    status = {"round": "r831", "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "files": {}, "done": False}
    for name, sub, prefixes in FILES:
        d = os.path.join(BASE, sub)
        try:
            os.makedirs(d, exist_ok=True)
        except Exception as e:
            log("MKDIR FAIL %s: %r" % (d, e))
            status["files"][name] = {"state": "mkdir_fail", "err": repr(e)}
            continue
        dst = os.path.join(d, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            log("SKIP exists %s (%d B)" % (name, os.path.getsize(dst)))
            status["files"][name] = {"state": "exists",
                                     "size": os.path.getsize(dst)}
            continue
        ok = False
        for p in prefixes:
            url = p + name
            log("TRY %s" % url)
            try:
                sz = fetch(url, dst)
                if sz > 0:
                    log("OK %s <- %s (%d B)" % (name, url, sz))
                    status["files"][name] = {"state": "done", "size": sz,
                                             "url": url}
                    ok = True
                    break
                log("INCOMPLETE %s from %s (will resume next run)" % (name, url))
                status["files"][name] = {"state": "partial", "url": url}
                ok = True  # resume on next round
                break
            except Exception as e:
                log("FAIL %s: %r" % (url, e))
        if not ok and name not in status["files"]:
            status["files"][name] = {"state": "all_urls_failed"}
    status["done"] = all(v.get("state") in ("done", "exists", "partial")
                         for v in status["files"].values()) and len(status["files"]) == len(FILES)
    status["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    json.dump(status, open(STATUS, "w", encoding="utf-8"),
              ensure_ascii=True, indent=1)
    log("STATUS written done=%s" % status["done"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
