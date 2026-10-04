# -*- coding: utf-8 -*-
"""r518 bm-c GORDERS probe: group-tree docs/orders.md raw-blob bytes SHA-1
watermark check (state last_orders_sha; r706 law: python subprocess raw
bytes, zero PS pipeline). Read-only; --update rewrites the state key only
after consumption. Pattern credit: Tools/_r515bmc_close.py GORDERS leg."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))
RE_KEYWORD = re.compile(r"BigMoney|bigmoney|quant|bm-[abc]", re.IGNORECASE)


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=GROUP,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (a[:3], r.stderr.decode("utf-8", "replace")))
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()
    sp = os.path.join(ROOT, "state-bm-c.json")
    with open(sp, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    prev = (st.get("last_orders_sha") or "").upper()
    git("fetch", "origin")
    blob = git("show", "origin/main:docs/orders.md")
    sha = hashlib.sha1(blob).hexdigest().upper()
    if sha == prev:
        print("GORDERS MATCH (group orders watermark unchanged: %s)" % sha[:12])
        return 0
    print("GORDERS CHANGED: %s -> %s" % (prev[:12], sha[:12]))
    text = blob.decode("utf-8", "replace")
    hits = [ln for ln in text.splitlines() if RE_KEYWORD.search(ln)]
    print("--- orders.md keyword rows (%d, last 40) ---" % len(hits))
    for ln in hits[-40:]:
        print(ln[:300])
    if args.update:
        st["last_orders_sha"] = sha
        with open(sp, "w", encoding="utf-8", newline="") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
        print("state last_orders_sha updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
