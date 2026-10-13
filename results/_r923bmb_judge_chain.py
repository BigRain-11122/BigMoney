"""r923 bm-b judge-chain driver (tsgate-probe -> judge).

Detached one-shot: the dead-session postburn driver (probe -> export-topk
-> judge) completed 04:50:32 with judge honestly refusing on the missing
tsgate_anchors leg (driver design gap: cmd_tsgate_probe was never in its
step list). This driver completes the chain per the leg-4 spec order:
tsgate-probe pins the frozen consumption anchors first (refuse-if-exists),
then judge consumes anchors + TOPK (sha16-pinned) -> JUDGED-<cutoff>.json
+ ledger 32. Crash-safe partial log per step; stop at first non-zero rc
(honest refusals included). pythonw + CREATE_NO_WINDOW per U060 zero-window.
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = r"C:\Program Files\Python311\python.exe"
SCRIPT = os.path.join(ROOT, "scripts", "alphagen_rl_p1.py")
OUT = os.path.join(ROOT, "results", "_r923bmb_judge_chain.json")
STEPS = [("tsgate-probe", ["tsgate-probe"]),
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
