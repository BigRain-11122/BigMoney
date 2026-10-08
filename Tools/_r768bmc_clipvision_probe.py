# -*- coding: utf-8 -*-
"""r768 bm-c: locate a working download source for Wan2.2 CLIP vision
(clip_vision_h.safetensors) - the only missing hard dependency of the
Wan2.2-TI2V-5B i2v chain. Probes candidate mirrors with HEAD requests,
prints status+size. Read-only probe, no download."""
import re
import urllib.request

src = open(r"Tools\_r767bmc_wan_fetch.py", encoding="utf-8",
           errors="replace").read()
for m in re.finditer(r"https?://[^\s\"']+", src):
    print("WANFETCH-URL:", m.group(0)[:150])

CANDS = [
    # city96 Wan2.2 GGUF repo may also host the vision tower
    "https://modelscope.cn/models/city96/Wan2.2-TI2V-5B-GGUF/resolve/master/clip_vision_h.safetensors",
    "https://modelscope.cn/models/city96/Wan2.2-TI2V-5B-GGUF/resolve/master/clip_vision_h_fp16.safetensors",
    # Comfy-Org repackaged split (canonical for Wan 2.1/2.2 vision)
    "https://hf-mirror.com/Comfy-Org/Wan_2.1_ComfyUI_Repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
    "https://modelscope.cn/models/Comfy-Org/Wan_2.1_ComfyUI_Repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
    "https://modelscope.cn/models/AI-ModelScope/Wan2.1_ComfyUI_Repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
    "https://modelscope.cn/models/SD.ORG/ComfyUI-Wan/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
]
for u in CANDS:
    try:
        req = urllib.request.Request(u, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            print("HIT", r.status, r.headers.get("Content-Length"), u[:110])
    except Exception as e:
        print("fail", repr(e)[:90], u[:110])
