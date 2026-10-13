# -*- coding: utf-8 -*-
# r977 ORD row extraction: walk group log for docs/orders.md commits to locate
# watermark blob a20281ea, then diff old vs current to list added rows.
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")

G = r"K:\Fluxgroup\FluxGroup"
WM_ORD = "a20281ea1fa1a751eab6a6922e567a191774bf0b"

def run(args, binary=False, ok=False):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True)
    if r.returncode != 0 and not ok:
        return None
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

log = run(["log", "origin/main", "--format=%H", "-n", "40", "--", "docs/orders.md"])
old_content = None
found = None
for line in log.splitlines():
    sha = line.strip()
    if not sha:
        continue
    blob = run(["rev-parse", sha + ":docs/orders.md"])
    if blob and blob.strip() == WM_ORD:
        found = sha
        old_content = run(["show", sha + ":docs/orders.md"])
        break

print("watermark commit found:", found)
if old_content is not None:
    new_content = run(["show", "origin/main:docs/orders.md"])
    old_set = set(l.rstrip("\r") for l in old_content.splitlines())
    added = [l.rstrip("\r") for l in new_content.splitlines() if l.rstrip("\r") not in old_set]
    print("=== ORD ADDED LINES (%d) ===" % len(added))
    for l in added:
        print(l[:800])
else:
    # fallback: print all rows timestamped 2026-10-13 2x:xx or later dates
    new_content = run(["show", "origin/main:docs/orders.md"])
    hits = [l for l in new_content.splitlines() if ("2026-10-13 2" in l) or ("2026-10-14" in l) or ("2026-10-13 21:" in l) or ("2026-10-13 22:" in l) or ("2026-10-13 23:" in l) or ("2026-10-13 20:" in l)]
    print("=== ORD FALLBACK TAIL CANDIDATES (%d) ===" % len(hits))
    for l in hits:
        print(l[:800])
