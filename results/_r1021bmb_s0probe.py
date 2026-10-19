"""r1021 bm-b: S0/S0.5 probe bundle.

Legs:
  A. orders ack diff: fleet/orders/*.md vs heartbeat orders_ack (bm-b.json).
  B. D-19 dual probe: group repo (C:\\Fluxgroup\\FluxGroup) fresh-read
     docs/decisions.md + docs/orders.md via git show origin/main:<path>
     after fetch; SHA-256 vs heartbeat last_*_sha keys.
  C. BM repo state: fetch + behind/ahead vs origin/main + porcelain short
     status (top faces only) + HEAD sha. Read-only beyond fetch.
Zero writes to shared faces; prints only. ASCII code per encoding law.
"""
import glob
import hashlib
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEARTBEAT = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
GROUP = r"C:\Fluxgroup\FluxGroup"
NO_WINDOW = 0x08000000


def sh(args, cwd=None, timeout=120):
    p = subprocess.run(args, cwd=cwd, capture_output=True, timeout=timeout,
                       creationflags=NO_WINDOW)
    return p.returncode, p.stdout, p.stderr


def main():
    hb = json.load(open(HEARTBEAT, encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))

    # --- A. orders ack diff ---
    files = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md"))
    )
    unacked = [f for f in files if f not in ack]
    print("A. orders files=%d acked=%d unacked=%s" % (
        len(files), len(ack & set(files)), unacked))

    # --- B. D-19 dual probe (fresh read via git show origin/main) ---
    rc, out, err = sh(["git", "fetch", "origin"], cwd=GROUP, timeout=120)
    print("B. group fetch rc=%d %s" % (rc, err.decode(errors="replace").strip()[:120]))
    for label, path, key in (
        ("DEC", "docs/decisions.md", "last_decisions_sha"),
        ("ORD", "docs/orders.md", "last_orders_sha"),
    ):
        rc, out, err = sh(["git", "show", "origin/main:%s" % path], cwd=GROUP, timeout=60)
        if rc == 0:
            h = hashlib.sha256(out).hexdigest()
            prev = hb.get(key, "")
            print("B. %s sha=%s prev=%s verdict=%s" % (
                label, h[:16], prev[:16],
                "UNCHANGED" if h == prev else "CHANGED"))
        else:
            print("B. %s show rc=%d err=%s" % (label, rc, err.decode(errors="replace")[:120]))

    # --- C. BM repo state ---
    rc, out, err = sh(["git", "fetch", "origin"], cwd=ROOT, timeout=180)
    print("C. bm fetch rc=%d %s" % (rc, err.decode(errors="replace").strip()[:160]))
    rc, out, err = sh(["git", "rev-list", "--count", "HEAD..origin/main"], cwd=ROOT, timeout=60)
    behind = out.decode().strip() or "?"
    rc2, out2, err2 = sh(["git", "rev-list", "--count", "origin/main..HEAD"], cwd=ROOT, timeout=60)
    ahead = out2.decode().strip() or "?"
    rc3, out3, err3 = sh(["git", "rev-parse", "--short", "HEAD", "origin/main"], cwd=ROOT, timeout=60)
    shas = out3.decode().split()
    print("C. behind=%s ahead=%s HEAD=%s origin=%s" % (
        behind, ahead, shas[0] if shas else "?", shas[1] if len(shas) > 1 else "?"))
    rc4, out4, err4 = sh(["git", "status", "--porcelain"], cwd=ROOT, timeout=120)
    dirty = out4.decode(errors="replace").splitlines()
    print("C. dirty_faces=%d" % len(dirty))
    for line in dirty[:30]:
        print("C. dirty: %s" % line.strip()[:150])
    if len(dirty) > 30:
        print("C. ... %d more" % (len(dirty) - 30))
    rc5, out5, err5 = sh(["git", "log", "--oneline", "-3", "origin/main"], cwd=ROOT, timeout=60)
    print("C. origin top3:")
    for line in out5.decode(errors="replace").splitlines()[:3]:
        print("C.   %s" % line[:150])


if __name__ == "__main__":
    main()
