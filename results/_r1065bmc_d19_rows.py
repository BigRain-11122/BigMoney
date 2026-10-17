# -*- coding: utf-8 -*-
"""r1065 bm-c: D-19 dual-delta row extraction (ORD content-sha1 + DEC raw-blob sha256 methods).

Locate the watermark-version blob in group-tree git history, diff vs origin/main,
print new rows for judging. Read-only; no watermark advance here.
"""
import subprocess, hashlib, sys, io
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GRP = r"K:\Fluxgroup\FluxGroup"
ORD_WM = "6aae4d9ca9cfb5a49b1796673d3f65c84a823914"   # state last_orders_sha (content-sha1)
DEC_WM = "7f12de366ee9409ce96f6fbd1bf8d917034add234db09706f0cab54eb17f2f93"  # state last_decisions_sha (sha256 raw bytes)

def sh(*a):
    return subprocess.run(["git", "-C", GRP, *a], capture_output=True).stdout

def sha1(b): return hashlib.sha1(b).hexdigest()
def sha256(b): return hashlib.sha256(b).hexdigest()

sh("fetch", "origin")

def find_wm_commit(path, wm, hsh):
    commits = sh("log", "--format=%H", "-n", "60", "origin/main", "--", path).decode().split()
    for c in commits:
        blob = sh("show", f"{c}:{path}")
        if hsh(blob) == wm:
            return c, blob
    return None, None

report = {}
for path, wm, hsh, name in (("docs/orders.md", ORD_WM, sha1, "ORD"),
                            ("docs/decisions.md", DEC_WM, sha256, "DEC")):
    c, old = find_wm_commit(path, wm, hsh)
    cur = sh("show", f"origin/main:{path}")
    if c is None:
        print(f"[{name}] watermark blob NOT FOUND in last 60 commits -- falling back to tail-only view")
        c = "(not-found)"
        old_lines = []
    else:
        old_lines = old.decode("utf-8", "replace").splitlines()
    cur_lines = cur.decode("utf-8", "replace").splitlines()
    old_set = set(old_lines)
    new_rows = [l for l in cur_lines if l not in old_set]
    report[name] = {"wm_commit": c, "new_rows": new_rows}
    print(f"== {name} delta (wm@{c} -> origin/main): {len(new_rows)} new row(s)")
    for l in new_rows:
        print("  |", l[:400])

with io.open(r"results\_r1065bmc_d19_rows.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(f"# r1065 bm-c D-19 delta rows (ORD wm {ORD_WM[:12]}.. / DEC wm {DEC_WM[:12]}..)\n\n")
    for name, r in report.items():
        f.write(f"## {name} (wm commit {r['wm_commit']})\n")
        for l in r["new_rows"]:
            f.write(l + "\n")
        f.write("\n")
print("written results/_r1065bmc_d19_rows.md")
