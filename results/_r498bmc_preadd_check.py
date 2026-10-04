# -*- coding: utf-8 -*-
"""r498 bm-c pre-add validation: checkpoint jsonl line-parse + claim-face reparse (fail-closed)."""
import json
import os
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CHECK = [
    r"results\n2_w15\checkpoint\n2_screen_shard_0of12.jsonl",
    r"results\n2_w15\checkpoint\n2_screen_shard_3of12.jsonl",
]
CLAIM_DIR = r"results\pool_claims\PERPETUAL-N2-W15-SHARD-4"

for rel in CHECK:
    p = os.path.join(ROOT, rel)
    with open(p, "rb") as fh:
        raw = fh.read()
    lines = [ln for ln in raw.split(b"\n") if ln.strip()]
    for i, ln in enumerate(lines):
        try:
            json.loads(ln.decode("utf-8"))
        except Exception as e:
            sys.exit("TORN/BAD LINE %s#%d: %s" % (rel, i, e))
    ids = set()
    for ln in lines:
        ids.add(json.loads(ln.decode("utf-8")).get("candidate_id"))
    print("%s: %d lines all-parse, unique ids=%d" % (rel, len(lines), len(ids)))

for fn in sorted(os.listdir(os.path.join(ROOT, CLAIM_DIR))):
    p = os.path.join(ROOT, CLAIM_DIR, fn)
    with open(p, "rb") as fh:
        json.load(fh)  # reparse gate
    print("claim face reparse OK: %s (%dB)" % (fn, os.path.getsize(p)))
print("PRE-ADD VALIDATION OK")
