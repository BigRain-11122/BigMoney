# -*- coding: utf-8 -*-
"""d19_check.py -- D-20260930-19 decisions watermark standing check (P-32 wiring).

Law: D-20260930-19 fresh-read = git -C <group> fetch + git show
origin/main:docs/decisions.md RAW-BLOB bytes -> SHA-256 (r292: PS pipeline
join = transcoding false-drift; r503: upper() case-normalize both sides).
Zero tree touch on the group repo. Watermark lives in state-<id>.json
last_decisions_sha (content-addressed, never line-count).

Usage (from repo root, any machine):
    python Tools/d19_check.py            # print MATCH/CHANGED + context
    python Tools/d19_check.py --update   # also rewrite state last_decisions_*
                                        # fields (call ONLY after consumption)

On CHANGED prints: the 派工通告板 dispatch-block rows + docs/orders.md CEO
待办区 rows touching this repo, plus the tail of decisions.md (newest rows)
for the round to consume. All child git calls carry CREATE_NO_WINDOW
(session-host flash guard, U060/O-67fbec7 law family).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))  # bigmoney -> quant -> FluxGroup
RE_KEYWORD = re.compile(r"BigMoney|bigmoney|quant|bm-[abc]", re.IGNORECASE)


def _git(group_args, cwd):
    r = subprocess.run(["git"] + group_args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (group_args[:3],
                                        r.stderr.decode("utf-8", "replace")))
    return r.stdout


def machine_id():
    with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8-sig") as fh:
        return json.load(fh)["machine_id"]


def state_path(mid):
    return os.path.join(ROOT, "state-%s.json" % mid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()

    mid = machine_id()
    sp = state_path(mid)
    with open(sp, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    prev = (st.get("last_decisions_sha") or "").upper()

    _git(["fetch", "origin"], GROUP)
    blob = _git(["show", "origin/main:docs/decisions.md"], GROUP)
    sha = hashlib.sha256(blob).hexdigest().upper()

    if sha == prev:
        print("D-19 MATCH (decisions watermark unchanged: %s)" % sha[:12])
        return 0

    print("D-19 CHANGED: %s -> %s" % (prev[:12], sha[:12]))
    text = blob.decode("utf-8", "replace")
    lines = text.splitlines()
    # dispatch board rows + keyword rows + file tail for new-decision review
    hits = [ln for ln in lines if RE_KEYWORD.search(ln)]
    print("--- keyword rows (%d) ---" % len(hits))
    for ln in hits[-40:]:
        print(ln[:300])
    print("--- decisions.md tail (last 30 lines) ---")
    for ln in lines[-30:]:
        print(ln[:300])
    try:
        orders = _git(["show", "origin/main:docs/orders.md"], GROUP).decode("utf-8", "replace")
        print("--- orders.md keyword rows ---")
        for ln in orders.splitlines():
            if RE_KEYWORD.search(ln):
                print(ln[:300])
    except SystemExit:
        print("(orders.md not found on origin -- skip)")
    if args.update:
        st["last_decisions_sha"] = sha
        st["last_decisions_read_at"] = st.get("clock_read") or ""
        with open(sp, "w", encoding="utf-8", newline="") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
        print("state last_decisions_sha updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
