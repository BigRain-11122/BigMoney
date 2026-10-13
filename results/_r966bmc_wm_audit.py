# -*- coding: utf-8 -*-
"""r966: watermark face audit -- locate state watermark shas in blob history,
diff orders.md new rows vs the c7d3ee65 face, verify decisions f41caf26 existence."""
import io, json, subprocess, hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
state = json.load(io.open(r"state-bm-c.json", encoding="utf-8"))
W_ORD = state["last_orders_sha"]
W_DEC = state["last_decisions_sha"]

def sh(cmd):
    p = subprocess.run(["git", "-C", GROUP] + cmd, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("CMD-FAIL: %s -> %s" % (cmd, p.stderr[:200]))
    return p.stdout

def blob_sha256(commit, path):
    b = sh(["show", commit + ":" + path])
    return hashlib.sha256(b).hexdigest(), b

# walk recent commits touching each file
for path, want in (("docs/orders.md", W_ORD), ("docs/decisions.md", W_DEC)):
    commits = sh(["log", "--format=%H", "-20", "--", path]).decode().split()
    print("== %s (want %s...)" % (path, want[:16]))
    hit = None
    faces = []
    for c in commits:
        s, _ = blob_sha256(c, path)
        faces.append((c[:9], s[:16]))
        if s == want:
            hit = c
    for c9, s16 in faces:
        print("   %s %s%s" % (c9, s16, "  <== WATERMARK MATCH" if s16 == want[:16] else ""))
    if hit:
        # diff vs origin/main
        d = sh(["diff", hit, "origin/main", "--", path]).decode("utf-8", "replace")
        io.open(r"results\_r966bmc_orddiff.txt" if "orders" in path
                else r"results\_r966bmc_decdiff.txt", "w", encoding="utf-8").write(d)
        print("   -> diff written (%d lines)" % len(d.splitlines()))
    else:
        print("   !! watermark NOT FOUND in last-20 blob history (phantom?)")
