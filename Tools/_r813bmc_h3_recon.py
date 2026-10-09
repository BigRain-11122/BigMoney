# -*- coding: utf-8 -*-
"""r813 bm-c: audit re-run with full capture + MiniMax-H3 (O-20261009-1746)
install preconditions recon: disk free, ComfyUI version, ModelScope channel
probe. Read-only apart from the audit snapshot file."""
import subprocess
import io
import os
import json
import shutil
import urllib.request

CNW = 0x08000000
G = "K:/Fluxgroup/FluxGroup"
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney"
out = io.open(os.path.join(R, "results", "_r813bmc_h3_recon.txt"), "w",
              encoding="utf-8")
w = out.write

# --- 1) audit re-run, full capture ---
cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "-File",
       os.path.join(R, "results", "_r813bmc_Tools_fleet-workspace-audit.ps1"),
       "-Root", G]
try:
    p = subprocess.run(cmd, capture_output=True, creationflags=CNW,
                       timeout=300)
    o = p.stdout.decode("utf-8", "replace")
    e = p.stderr.decode("utf-8", "replace")
    w("AUDIT rc=%d stdout_len=%d stderr=%s\n" % (p.returncode, len(o),
                                                 e.strip()[:300]))
    w(o)
except subprocess.TimeoutExpired:
    w("AUDIT TIMEOUT\n")

# --- 2) disk free ---
for drv in ("C:\\", "D:\\", "K:\\"):
    try:
        du = shutil.disk_usage(drv)
        w("DISK %s free=%.1fGB total=%.1fGB\n" % (
            drv, du.free / 1024 ** 3, du.total / 1024 ** 3))
    except Exception as ex:
        w("DISK %s err %s\n" % (drv, ex))

# --- 3) ComfyUI version faces ---
cands = [r"D:\ComfyUI\ComfyUI\comfyui_version.py",
         r"D:\ComfyUI\ComfyUI\custom_nodes",
         r"D:\ComfyUI\version.txt", r"D:\ComfyUI\ComfyUI\__init__.py"]
for c in cands:
    w("COMFY face %s exists=%s\n" % (c, os.path.exists(c)))
try:
    # ComfyUI repo tags / version stamp
    p = subprocess.run(["git", "-C", "D:\\ComfyUI", "describe", "--tags"],
                       capture_output=True, creationflags=CNW, timeout=20)
    w("COMFY git describe rc=%d out=%s err=%s\n" % (
        p.returncode, p.stdout.decode("utf-8", "replace").strip()[:60],
        p.stderr.decode("utf-8", "replace").strip()[:100]))
    p = subprocess.run(["git", "-C", "D:\\ComfyUI", "log", "-1",
                        "--format=%h %ci"], capture_output=True,
                       creationflags=CNW, timeout=20)
    w("COMFY last commit: %s\n" % p.stdout.decode("utf-8", "replace").strip())
except Exception as ex:
    w("COMFY git err %s\n" % ex)

# --- 4) ModelScope channel probe for MiniMax-H3 faces ---
probes = [
    "https://modelscope.cn/api/v1/models/MiniMaxAI/MiniMax-H3",
    "https://modelscope.cn/api/v1/models/iic/MiniMax-H3",
]
for u in probes:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=15)
        d = r.read().decode("utf-8", "replace")
        w("MS probe %s -> %d %s\n" % (u.split("/")[-1], r.status, d[:200]))
    except Exception as ex:
        w("MS probe %s -> ERR %s\n" % (u.split("/")[-1], str(ex)[:120]))
# search API
try:
    u = ("https://modelscope.cn/api/v1/dolphin/models?PageSize=10&PageNumber=1"
         "&Search=MiniMax-H3")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=20)
    d = r.read().decode("utf-8", "replace")
    w("MS search MiniMax-H3 -> %d %s\n" % (r.status, d[:600]))
except Exception as ex:
    w("MS search ERR %s\n" % str(ex)[:200])
# community 8G deploy repo probe
for name in ("Danshiduzhi/minimax-h3-8g-deploy",):
    try:
        u = "https://api.github.com/repos/" + name
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=15)
        d = json.loads(r.read().decode("utf-8", "replace"))
        w("GH %s -> stars=%s size_kb=%s updated=%s\n" % (
            name, d.get("stargazers_count"), d.get("size"),
            d.get("updated_at")))
    except Exception as ex:
        w("GH %s ERR %s\n" % (name, str(ex)[:120]))
out.close()
print("h3 recon done")
