# -*- coding: utf-8 -*-
"""r669 bm-c S0.5 sweep facts writer (s05 leg; s7close leg re-runs same script).

Replicates r666 facts format exactly (consumed by close batch + state
watermark keys, r583 S4 law: facts-driven, never hand-typed).
Legs: (a) DEC = group-tree origin/main:docs/decisions.md raw-blob SHA-256;
(b) ORD = group-tree origin/main:docs/orders.md raw-blob SHA-1 (ALGORITHM
PIN per r537 law); (c) fleet orders ack diff via Tools/orders_diff.py
canonical logic (never re-derive, r74 law); (d) inbox unread for bm-c/ALL
(filter widened: dashless 'bmc' machine-id form catches MSG-0625 family).
All child git calls carry CREATE_NO_WINDOW (U060 flash guard).
Pattern credit: r655-r667 s05 facts lineage."""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orders_diff

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))  # bigmoney -> quant -> FluxGroup
ROUND = 669
FACTS_PATH = os.path.join(ROOT, "results", "_r%d%s_s05_facts.json" % (ROUND, "bmc"))


def _git(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r


def main():
    os.chdir(ROOT)
    with open("state-bm-c.json", encoding="utf-8-sig") as fh:
        st = json.load(fh)
    prev_dec = (st.get("last_decisions_sha") or "").upper()
    prev_ord = (st.get("last_orders_sha") or "").upper()

    r = _git(["fetch", "origin"], GROUP)
    fetch_rc = r.returncode
    dec_blob = _git(["show", "origin/main:docs/decisions.md"], GROUP).stdout
    ord_blob = _git(["show", "origin/main:docs/orders.md"], GROUP).stdout
    assert dec_blob and ord_blob, "empty group blob read"
    dec_sha = hashlib.sha256(dec_blob).hexdigest().upper()
    ord_sha = hashlib.sha1(ord_blob).hexdigest().upper()

    unacked = orders_diff.unacked_orders()
    files = sorted(f for f in os.listdir(os.path.join(ROOT, "fleet", "orders"))
                   if f.startswith("O-"))

    inbox_dir = os.path.join(ROOT, "fleet", "inbox")
    inbox_unread = []
    for name in sorted(os.listdir(inbox_dir)):
        if not os.path.isfile(os.path.join(inbox_dir, name)):
            continue
        low = name.lower()
        if "bm-c" in low or "bmc" in low or "all" in low:
            inbox_unread.append(name)

    shape = (len(dec_sha) == 64 and len(ord_sha) == 40
             and len(prev_dec) == 64 and len(prev_ord) == 40)
    facts = {
        "round": ROUND,
        "fetch_rc": fetch_rc,
        "dec_sha": dec_sha,
        "prev_dec_sha": prev_dec,
        "dec_delta": dec_sha != prev_dec,
        "ord_sha": ord_sha,
        "prev_ord_sha": prev_ord,
        "ord_delta": ord_sha != prev_ord,
        "dec_bytes": len(dec_blob),
        "ord_bytes": len(ord_blob),
        "fleet_orders_total": len(files),
        "unacked": unacked,
        "inbox_unread": inbox_unread,
        "shape_assert": bool(shape),
    }
    assert shape, "sha shape assert failed"
    with open(FACTS_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print("S05 facts written:", FACTS_PATH)
    print("DEC", dec_sha[:12], "delta=", facts["dec_delta"])
    print("ORD", ord_sha[:12], "delta=", facts["ord_delta"])
    print("fleet_orders", len(files), "unacked", len(unacked),
          "inbox_unread", len(inbox_unread), inbox_unread)
    return 0


if __name__ == "__main__":
    sys.exit(main())
