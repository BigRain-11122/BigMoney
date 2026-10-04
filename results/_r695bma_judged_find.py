# r695 bm-a: 3 judged-anchor cells -- today census values vs frozen judged face
# r512 recorded: FY_BG census -0.2777 vs judged -0.2725; FY_BG_H10 +0.2067 vs +0.2143;
#                FY_BG_TP8 -0.2190 vs judged -0.2119  (all delta ~ -0.005..-0.008)
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import refine_bench_rev_census as RC

# find the 3 anchor cells
anchors = [c for c in RC.census_cells() if c.get("anchor_judged")]
print("anchor cells:", [c["name"] for c in anchors])

# judged face products: find REV_OSC_STOCK_P1 judged results
judged = {}
for cand in [r"results\rev_osc_stock_p1\judged.json",
             r"results\rev_osc_stock_p1\cells.json",
             r"results\rev_osc_stock_p1\rev_osc_stock_p1.json"]:
    p = os.path.join(ROOT, cand)
    if os.path.exists(p):
        print("judged face file:", cand)
        d = json.load(io.open(p, encoding="utf-8"))
        print(str(d)[:300])
        break
else:
    # search
    import glob
    for p in glob.glob(os.path.join(ROOT, "results", "**", "*.json"),
                       recursive=True):
        bn = os.path.basename(p).lower()
        if "rev_osc" in bn and os.path.getsize(p) < 200000:
            print("candidate:", p)
print("PROBE_OK")
