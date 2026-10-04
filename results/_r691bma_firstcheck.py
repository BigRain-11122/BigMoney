"""r691 bm-a first-thing probes: W3 judge product landing + pid liveness dual-form."""
import subprocess, os, json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

out = {}

prod = "results/mass_trial/w3_judge.json"
out["w3_product_exists"] = os.path.exists(prod)
if out["w3_product_exists"]:
    d = json.load(open(prod, encoding="utf-8"))
    out["w3"] = {
        "complete": d.get("complete"),
        "cells": len(d.get("cells", [])),
        "efp": d.get("expected_false_positives"),
        "g2_eligible": d.get("g2_eligible"),
    }

# pid 33768 liveness, CSV full-scan form (r659 law: no /FI single-pid filter)
r = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True)
txt = r.stdout.decode("gbk", "replace")
rows = [l for l in txt.splitlines() if l.startswith('"33768,')]
out["pid_33768_alive"] = bool(rows)
if rows:
    out["pid_33768_row"] = rows[0][:120]

# N2 face: any new N2 commits at origin since ping (r690 pointer 2)
g = subprocess.run(["git", "log", "origin/main", "--oneline", "--since=2026-10-04 18:00",
                    "--", "scripts/perpetual_faces_n2.py"], capture_output=True)
out["n2_commits_since_ping"] = g.stdout.decode("utf-8", "replace").strip().splitlines()

print(json.dumps(out, ensure_ascii=False, indent=1))
