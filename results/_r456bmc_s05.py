# -*- coding: utf-8 -*-
"""r456 bm-c S0.5: group-tree fetch FIRST (r452 law: probe fetches before any
origin-blob read), then orders double-scan leg 1 (Tools/orders_diff.py
canonical), D-19 decisions watermark (raw-blob sha256 per D-20260930-18),
group orders.md sha1, inbox unread scan. Read-only."""
import hashlib
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
DEC_SHA = "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA"
ORD_SHA1 = "68947C178D21814FBB5B20C3497F1DC28D42D50C"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run(args, cwd):
    return subprocess.run(
        args, capture_output=True, cwd=cwd, text=True, encoding="utf-8",
        errors="replace", creationflags=NO_WINDOW)


def run_raw(args, cwd):
    return subprocess.run(
        args, capture_output=True, cwd=cwd, creationflags=NO_WINDOW)


def main():
    # 0) group-tree fetch (fresh-read law)
    r = run_raw(["git", "fetch", "origin"], GROUP)
    print("GROUP_FETCH_RC", r.returncode)
    if r.returncode != 0:
        print("FETCH_ERR:", (r.stderr or b"").decode("utf-8", "replace")[:200])
    # 1) fleet orders diff
    r = run(["python", "Tools/orders_diff.py"], ROOT)
    print("ORDERS_DIFF:", r.stdout.strip()[:400])
    # 2) D-19 decisions hash (raw blob)
    r = run_raw(["git", "show", "origin/main:docs/decisions.md"], GROUP)
    if r.returncode != 0:
        print("DECISIONS_READ_FAIL rc=%d" % r.returncode)
    else:
        sha = hashlib.sha256(r.stdout).hexdigest().upper()
        if sha == DEC_SHA:
            print("DECISIONS_MATCH", sha[:12])
        else:
            print("DECISIONS_CHANGED", sha)
            text = r.stdout.decode("utf-8", "replace")
            lines = text.splitlines()
            for i, ln in enumerate(lines):
                if "派工通告板" in ln:
                    print("--- 派工通告板 block ---")
                    print("\n".join(lines[i:i + 40]))
                    break
    # 3) group orders.md sha1 (raw blob)
    r = run_raw(["git", "show", "origin/main:docs/orders.md"], GROUP)
    if r.returncode != 0:
        print("GROUP_ORDERS_READ_FAIL rc=%d" % r.returncode)
    else:
        sha1 = hashlib.sha1(r.stdout).hexdigest().upper()
        if sha1 == ORD_SHA1:
            print("GROUP_ORDERS_MATCH", sha1[:12])
        else:
            print("GROUP_ORDERS_CHANGED", sha1)
            text = r.stdout.decode("utf-8", "replace")
            lines = text.splitlines()
            hit = False
            for i, ln in enumerate(lines):
                if "CEO" in ln and ("待办" in ln or "物理" in ln):
                    hit = True
                    print("--- CEO pending physical-items area ---")
                    print("\n".join(lines[i:i + 30]))
                    break
            if not hit:
                print("(no CEO-pending marker; tail below)")
                print("\n".join(lines[-25:]))
    # 4) inbox scan
    inbox = os.path.join(ROOT, "fleet", "inbox")
    unread = []
    if os.path.isdir(inbox):
        for name in sorted(os.listdir(inbox)):
            p = os.path.join(inbox, name)
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    head = f.read(300)
                if "bm-c" in head or "ALL" in head:
                    unread.append((name, head.splitlines()[:3]))
    print("--- INBOX (%d addressed to bm-c/ALL) ---" % len(unread))
    for name, head in unread:
        print(" ", name, "|", " / ".join(head))
    print("S05_DONE")


if __name__ == "__main__":
    main()
