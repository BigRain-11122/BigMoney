# -*- coding: utf-8 -*-
"""r1052 ORD delta verify: pinned method = content-bytes sha1 (r977 law).
Probe face reported sha256-vs-sha1 method mismatch = phantom-delta suspect.
This script computes ground truth both ways and extracts real new rows if any.
"""
import subprocess, hashlib, json, io, sys

GROUP = r"K:\Fluxgroup\FluxGroup"

def gb(*args):
    return subprocess.run(["git", "-C", GROUP] + list(args),
                          capture_output=True, timeout=120).stdout

content = gb("show", "origin/main:docs/orders.md")
sha1 = hashlib.sha1(content).hexdigest()
sha256 = hashlib.sha256(content).hexdigest()

state_ord_key = "9d0f539d41d14b7b17e1d4081dedaebc1c8078a7e35b0b7cfaab30ab8b9fb516"

facts = {
    "ts": "2026-10-16T13:4x",
    "ord_content_sha1": sha1,
    "ord_content_sha256": sha256,
    "state_ord_key": state_ord_key,
    "real_delta_sha1": sha1 != state_ord_key,
}

if sha1 == state_ord_key:
    facts["verdict"] = "PHANTOM_DELTA (probe sha256-vs-sha1 method mismatch, r977 family) -- zero rows owed, watermark key correct as-is"
else:
    facts["verdict"] = "REAL_DELTA -- extract rows below"
    # find rows newer than the state's consumption: last consumed at r1051 12:51 (ORD 9d0f539d, 9 foreign rows + own 2 receipts)
    text = content.decode("utf-8", errors="replace")
    lines = text.splitlines()
    # tail scan: rows after line containing "12:5" timestamp markers from today; safer: dump last 60 rows for eyeball + machine filter
    facts["tail_rows"] = lines[-60:]

with io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1052bmc_ord_check.json", "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)

print(json.dumps({k: facts[k] for k in ("ord_content_sha1", "real_delta_sha1", "verdict")}, ensure_ascii=False))
