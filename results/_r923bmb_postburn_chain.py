"""r923 bm-b post-burn chain driver (probe -> export-topk -> judge).

Detached one-shot: runs the three alphagen_rl_p1 legs sequentially,
logging rc/tail per step to results/_r923bmb_postburn_chain.json after
each step (crash-safe partial log). Stop at first non-zero rc (honest
refusals included). CREATE_NO_WINDOW per zero-window law (U060).
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = r"C:\Program Files\Python311\python.exe"
SCRIPT = os.path.join(ROOT, "scripts", "alphagen_rl_p1.py")
OUT = os.path.join(ROOT, "results", "_r923bmb_postburn_chain.json")
STEPS = [("probe", ["probe"]),
         ("export-topk", ["export-topk"]),
         ("judge", ["judge"])]

log = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": []}
for name, args in STEPS:
    t0 = time.time()
    p = subprocess.run([PY, SCRIPT] + args, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=ROOT, creationflags=0x08000000)
    log["steps"].append({
        "step": name, "rc": p.returncode,
        "sec": round(time.time() - t0, 1),
        "stdout_tail": (p.stdout or "").strip()[-600:],
        "stderr_tail": (p.stderr or "").strip()[-300:],
    })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1, ensure_ascii=False)
    if p.returncode != 0:
        break
log["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(log, f, indent=1, ensure_ascii=False)
