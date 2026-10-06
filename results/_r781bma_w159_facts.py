# -*- coding: utf-8 -*-
"""r781 bm-a W159 freeze fact-finding: (a) W158 finalize K/ledger/round from
on-disk receipts; (b) W159 pre-seat probe receipt filename; (c) W159 seat
delivery facts (git); (d) seat MSG self-ack state; (e) W159 prereg fact
lines (fork-face check vs the n1 entry prose to be generated)."""
import glob
import json
import subprocess
import io

# (a) W158 finalize facts
print("=== W158 finalize receipts ===")
for f in sorted(glob.glob(r"results\*w158*finalize*") + glob.glob(r"results\*w158*final*")):
    print("  ", f)
f158 = r"results\perpetual_faces\n1_w158_results.json"
try:
    d = json.load(open(f158, encoding="utf-8"))
    print("n1_w158_results keys:", sorted(d.keys())[:12])
    for k in ("merged", "merge", "pool", "finalize", "k_merged", "K", "ledger", "trials_ledger"):
        if k in d:
            v = d[k]
            print(f"  {k}:", str(v)[:200])
except FileNotFoundError:
    print("  n1_w158_results.json missing")
# ledger head scan
for f in sorted(glob.glob(r"results\perpetual_faces\n1_w15*_results.json")):
    d = json.load(open(f, encoding="utf-8"))
    tl = d.get("trials_ledger", {})
    print(" ledger:", f.split("\\")[-1], "total:", tl.get("total"), "keys:", sorted(tl.keys())[:6])

# (b) W159 pre-seat probe receipts
print("=== W159 r779 files ===")
for f in sorted(glob.glob(r"results\_r779bma_w159*")):
    print("  ", f)

# (c) seat delivery facts
print("=== seat commits ===")
for sha in ("bf059816d", "7b60d09da"):
    p = subprocess.run(["git", "log", "--oneline", "--format=%h %p %s", "-1", sha],
                       capture_output=True).stdout.decode("utf-8", errors="replace")
    print("  ", p.strip()[:180])

# (d) seat MSG self-ack state
print("=== seat MSG files ===")
for f in sorted(glob.glob(r"fleet\inbox\*w159*") + glob.glob(r"fleet\inbox\processed\*w159*")):
    print("  ", f)

# (e) W159 prereg fact lines
print("=== W159 prereg fork-face lines ===")
txt = io.open(r"research\PERPETUAL_N1_W159_PREREG.md", encoding="utf-8").read()
for kw in ("finalize landed", "net chain head", "merged pool", "ledger head",
           "seat", "delivery window", "7b60d09da", "bf059816d", "753,012",
           "K=", "345,520", "engine_owner rows"):
    hits = [l.strip()[:150] for l in txt.splitlines() if kw in l]
    for h in hits[:4]:
        print(f"  [{kw}]", h)
    if not hits:
        print(f"  [{kw}] --none--")
