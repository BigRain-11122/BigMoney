# -*- coding: utf-8 -*-
"""r983 bm-a: S0.5 dual-delta verify (orders + decisions) -- fresh read, zero tree touch.

Dead-session (r983-era, 11:10) claimed: ORD bde2e581 consumed, tail zero BigMoney rows; DEC unchanged.
This script re-verifies independently:
  1. orders tail scan for BigMoney/quant directives (all O-*.md rows, no timestamp filter)
  2. decisions.md content-sha compare vs state pin (sha256, D-20261030-18)
"""
import subprocess, json, hashlib, re, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
GROUP = r"K:\Fluxgroup\FluxGroup"

def show(path, ref="origin/main", cwd=GROUP):
    b = subprocess.run([GIT, "-C", cwd, "show", f"{ref}:{path}"], capture_output=True)
    assert b.returncode == 0, (path, b.stderr[:200])
    return b.stdout

# ---- 1. orders scan (fleet/orders/ in THIS repo, origin tip via this repo) ----
b = subprocess.run([GIT, "ls-tree", "-r", "--name-only", "origin/main", "fleet/orders/"], capture_output=True)
files = [f for f in b.stdout.decode().splitlines() if f.strip()]
hit_rows = []
for f in files:
    txt = show(f, cwd=".")  # cwd arg unused; use this repo
    pass

# simpler: read local worktree copies (origin==HEAD==worktree for fleet/orders since pull clean there)
import os
ORD_DIR = os.path.join("fleet", "orders")
local_files = sorted(os.listdir(ORD_DIR))
print("orders files:", len(local_files))

# orders content sha across all O files (order-stable)
h = hashlib.sha256()
for fn in local_files:
    p = os.path.join(ORD_DIR, fn)
    if os.path.isfile(p):
        h.update(open(p, "rb").read())
print("orders_content_sha1:", h.hexdigest()[:8])

# BigMoney-relevant rows in the tail files: scan every O-*.md for BigMoney/quant mentions + exec owner
bm_hits = []
for fn in local_files:
    if not fn.startswith("O-") or not fn.endswith(".md"):
        continue
    p = os.path.join(ORD_DIR, fn)
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if re.search(r"BigMoney|bigmoney|quant", txt, re.I):
        bm_hits.append(fn)
print("bm-relevant order files:", bm_hits)

# ---- 2. decisions compare ----
state = json.load(open("state-bm-a.json", encoding="utf-8"))
pin = state.get("last_decisions_sha") or state.get("d19_watermark_guard", {}).get("decisions_sha256")
dec = show("docs/decisions.md")
sha = hashlib.sha256(dec).hexdigest()
print("decisions_sha256:", sha[:16], "pin:", (pin or "?")[:16])

# count decision rows to sanity-check tail
rows = [l for l in dec.decode("utf-8", "replace").splitlines() if re.match(r"^[-*]?\s*(D-2026|D-20261|D-202610)", l)]
print("decision-like rows:", len(rows))

print("VERDICT:", "DEC_UNCHANGED" if pin == sha else "DEC_CHANGED_NEED_CONSUME")
