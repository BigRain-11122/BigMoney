# -*- coding: utf-8 -*-
"""r2066 read-only probe: what exactly are today's margin and the step distribution?

Nothing is written except the printed report.  Imports the real faces so the numbers
are the book's own numbers, not a re-implementation.
"""
from __future__ import annotations

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from scripts import etf_book_k_identity_bar as KIB  # noqa: E402
from scripts import etf_book_k_leg_rehearsal as RB  # noqa: E402
import etf_book_rebalance_permission as PP  # noqa: E402


def main():
    sched, meta = KIB._published_schedule()
    print("sched type:", type(sched), "len:", len(sched), "meta:", meta)
    pairs = list(sched.items()) if hasattr(sched, "items") else list(sched)
    print("first:", pairs[:2])
    print("last:", pairs[-2:])

    rows = [(str(r[0])[:10], float(r[1]), float(r[2])) for r in pairs]
    diffs = [rows[i + 1][1] - rows[i][1] for i in range(len(rows) - 1)]
    drops = sorted([-d for d in diffs if d < 0])
    print("n_steps:", len(rows), "n_drops:", len(drops))
    if drops:
        print("drop_pct_pp median/p90/max:",
              round(100 * statistics.median(drops), 4),
              round(100 * drops[int(0.9 * (len(drops) - 1))], 4),
              round(100 * max(drops), 4))

    ident = KIB._published_schedule  # only to keep linters quiet
    p = os.path.join(ROOT, "results", "etf_book_size_rulers_decision.json")
    rulers = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    tf, ticket = PP.latest_ticket()
    print("ticket:", tf)
    print("k_now:", ticket.get("k_now"), "k_rule:", ticket.get("k_rule"),
          "nav:", (ticket.get("ticket") or {}).get("nav"))
    print("cells:", json.dumps({k: {"k": v.get("k"), "bars": v.get("bars")}
                                for k, v in (rulers or {}).get("cells", {}).items()}))

    on_disk = PP.decide(rulers, ticket)
    print("ON-DISK verdict:", on_disk.get("verdict"), "permitted_k:", on_disk.get("permitted_k"),
          "cut_cny:", on_disk.get("cut_cny"), "unreadable:", on_disk.get("readings_unreadable"))

    base_bar = rows[-1][0]
    k_base = rows[-1][1]
    beta = RB.beta_from_k(k_base, ticket.get("beta_target"))
    rr = RB.rehearse(rulers, ticket, k_base, beta, base_bar)
    print("PATCHED:", json.dumps({k: rr["permission"].get(k) for k in
                                 ("verdict", "permitted_k", "cut_k", "cut_pp", "cut_cny")},
                                ensure_ascii=False))

    perm = rr["permission"].get("permitted_k")
    if perm is not None:
        k_now = float(ticket.get("k_now"))
        nav = float((ticket.get("ticket") or {}).get("nav") or 0)
        print("margin_pp:", round(100 * (k_now - perm), 4),
              "margin_cny:", round((k_now - perm) * nav, 2),
              "tol_pp:", 100 * PP.SIZE_TOL)

    # what happens if k_now drops by each historical magnitude
    if perm is not None and ticket is not None:
        nav = float((ticket.get("ticket") or {}).get("nav") or 0)
        k_now = float(ticket.get("k_now"))
        for label, drop in (("median", statistics.median(drops) if drops else 0.0),
                            ("p90", drops[int(0.9 * (len(drops) - 1))] if drops else 0.0),
                            ("max", max(drops) if drops else 0.0)):
            t2 = dict(ticket)
            t2["k_now"] = round(k_now - drop, 9)
            t2["_file"] = ticket.get("_file")
            d = PP.decide(rulers if False else rr and rulers, t2)
        # the patched rulers are needed for a fair re-decide; rebuild them once
        patched = dict(rulers)
        patched["cells"] = RB.patch_cells(rulers.get("cells"), k_base, beta, base_bar)
        for label, drop in (("median", statistics.median(drops) if drops else 0.0),
                            ("p90", drops[int(0.9 * (len(drops) - 1))] if drops else 0.0),
                            ("max", max(drops) if drops else 0.0)):
            t2 = dict(ticket)
            t2["k_now"] = round(k_now - drop, 9)
            d = PP.decide(patched, t2)
            print("if k drops %s (%.4fpp): verdict=%s cut_cny=%s" %
                  (label, 100 * drop, d.get("verdict"), d.get("cut_cny")))


if __name__ == "__main__":
    main()
