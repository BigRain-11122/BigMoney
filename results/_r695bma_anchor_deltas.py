# r695 bm-a: 3 judged anchors -- today census vs frozen judged face (r512 deltas recited)
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC

# frozen judged face (REV_OSC_STOCK_P1 products, r282 era)
p1 = json.load(io.open(os.path.join(ROOT, "results", "rev_osc", "p1_results.json"),
                       encoding="utf-8"))
rows = p1.get("cells") or p1.get("rows") or p1
if isinstance(rows, dict):
    rows = list(rows.values())
judged = {}
for r in rows:
    nm = r.get("name") or r.get("cell") or r.get("id")
    judged[nm] = r
print("judged face cells:", sorted(judged.keys()))

RC._init_worker()
for c in RC.census_cells():
    if not c.get("anchor_judged"):
        continue
    row = RC._cell_job(c)
    jname = {"Dtop10|yang|base|time|h7": "FY_BG",
             "Dtop10|yang|base|time|h10": "FY_BG_H10",
             "Dtop10|yang|base|tp8sl10|h7": "FY_BG_TP8"}.get(c["name"])
    j = judged.get(jname, {})
    print("%-30s census_today_sharpe=%r judged=%r delta=%+.4f | ann %r vs %r | entries %r vs %r"
          % (c["name"], row["sharpe_full"], j.get("sharpe_full", j.get("sharpe")),
             (row["sharpe_full"] or 0) - (j.get("sharpe_full", j.get("sharpe")) or 0),
             row["ann_ret"], j.get("ann_ret"),
             row["entries"], j.get("entries", j.get("n_entries"))))
print("r512 recorded stageA deltas: FY_BG -0.2777 vs -0.2725 (d=-0.0052); "
      "FY_BG_H10 +0.2067 vs +0.2143 (d=-0.0076); FY_BG_TP8 -0.2190 vs -0.2119 (d=-0.0071)")
print("PROBE_OK")
