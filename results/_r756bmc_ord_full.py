# -*- coding: utf-8 -*-
"""r756 bm-c ORD full-row extraction: pull full text of the 12:1x modified
O-20261008-1205-bm-c row + fleet-nodes.json bm-c entry from origin blob for
re-verification (zero tree touch)."""
import json
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000


def blob(path):
    p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True, creationflags=CF)
    assert p.returncode == 0, "blob read fail " + path
    return p.stdout.decode("utf-8", "replace")


out = {}
ordr = blob("docs/orders.md")
for ln in ordr.splitlines():
    if "O-20261008-1205-bm-c" in ln:
        out.setdefault("ord_rows", []).append(ln)
dec = blob("docs/decisions.md")
for ln in dec.splitlines():
    if "D-20261008-08" in ln or "D-20261008-06" in ln:
        out.setdefault("dec_rows", []).append(ln)

try:
    fn = blob("Tools/fleet-nodes.json")
    out["fleet_nodes_raw_len"] = len(fn)
    try:
        data = json.loads(fn)
        out["fleet_nodes_keys"] = list(data.keys()) if isinstance(data, dict) else "list"
        for k, v in (data.items() if isinstance(data, dict) else []):
            if "bm-c" in k or (isinstance(v, dict) and "bm-c" in json.dumps(v)):
                out.setdefault("bmc_entry", {})[k] = v
    except Exception as e:
        out["fleet_nodes_parse_err"] = repr(e)[:200]
        out["fleet_nodes_head"] = fn[:1200]
except AssertionError as e:
    out["fleet_nodes_err"] = str(e)

dest = os.path.join(ROOT, "results", "_r756bmc_ord_full.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print(json.dumps({k: (len(v) if isinstance(v, (list, str)) else "obj")
                  for k, v in out.items()}, indent=1))
