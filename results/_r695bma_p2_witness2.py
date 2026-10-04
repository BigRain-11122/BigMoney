# r695 bm-a: 3-way witness -- P2 x1 cell products vs stage-A anchors vs today re-run
import io, json, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import contest_ytd_legs as CX

anchors = CX._census_anchor_rows()
names = ["D-15|raw|base|time|h20", "Dtop10|raw|base|time|h20", "D-25|raw|base|time|h20",
         "D-15|yang|base|time|h20", "D-25|yang|base|time|h20", "Dtop10|yang|base|time|h20",
         "D-15|raw|liq2|time|h20", "D-25|raw|liq2|time|h20", "Dtop10|raw|liq2|time|h20",
         "D-15|yang|liq2|time|h20"]
print("%-32s %-10s %-10s %-10s" % ("cell", "P2_x1", "stageA", "match"))
for nm in names:
    fp_key = nm.replace("|", "_")
    fp = os.path.join(ROOT, "results", "refine_bench_stock", "rev_p2",
                      "cells", fp_key + "_x1.json")
    d = json.load(io.open(fp, encoding="utf-8"))
    p2s = d.get("sharpe_full", d.get("stats", {}).get("sharpe_full"))
    a = anchors.get(nm, {})
    print("%-32s %-10r %-10r %s  ann %r vs %r | entries %r vs %r"
          % (nm, p2s, a.get("sharpe_full"), "SAME" if p2s == a.get("sharpe_full") else "DIFF",
             d.get("ann_ret", d.get("stats", {}).get("ann_ret")), a.get("ann_ret"),
             d.get("entries"), a.get("entries")))
print("PROBE_OK")
