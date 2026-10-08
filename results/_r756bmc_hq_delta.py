# -*- coding: utf-8 -*-
"""r756 bm-c HQ delta probe: consume DEC/ORD watermark changes. Extracts
dispatch-board + CEO-physics-zone relevant rows from origin/main raw blobs
(zero tree touch per D-20260930-13 law), excerpts to
results/_r756bmc_hq_delta.json for same-round adjudication. C-01 standing
check: P-09/P-11 HQ follow-up scan included."""
import json
import os
import re
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000


def blob(path):
    p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True, creationflags=CF)
    assert p.returncode == 0, "blob read fail " + path
    return p.stdout.decode("utf-8", "replace")


dec = blob("docs/decisions.md")
ordr = blob("docs/orders.md")

KEYS = re.compile(r"(?i)(bm-c|bigmoney|quant|p-09|p-11)")


def scan(lines):
    hits = []
    for i, ln in enumerate(lines):
        if KEYS.search(ln) or re.search(r"2026-10-08", ln):
            hits.append((i, ln.rstrip()))
    return hits


dec_lines = dec.splitlines()
ord_lines = ordr.splitlines()
probe = {
    "dec_total_lines": len(dec_lines),
    "ord_total_lines": len(ord_lines),
    "dec_key_hits": [[i, ln[:260]] for i, ln in scan(dec_lines)],
    "ord_key_hits": [[i, ln[:260]] for i, ln in scan(ord_lines)],
    "dec_tail": [l[:260] for l in dec_lines[-60:]],
    "ord_tail": [l[:260] for l in ord_lines[-40:]],
}
out = os.path.join(ROOT, "results", "_r756bmc_hq_delta.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(probe, fh, indent=1, ensure_ascii=False)
print(json.dumps({"dec_hits": len(probe["dec_key_hits"]),
                   "ord_hits": len(probe["ord_key_hits"])}, indent=1))
