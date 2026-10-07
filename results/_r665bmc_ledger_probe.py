import json, glob, os, re
root = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
heads = []
for p in glob.glob(os.path.join(root, "results", "perpetual_faces", "n1_w*_results.json")):
    m = re.search(r"n1_w(\d+)_results", p)
    if m: heads.append((int(m.group(1)), p))
heads.sort()
w, p = heads[-1]
d = json.load(open(p, encoding="utf-8"))
sg = d.get("science_gates", {})
tl = d.get("trials_ledger", {})
print("LIVE_HEAD", os.path.basename(p))
print("LEDGER_HEAD", tl.get("total", sg.get("ledger_head")))
print("K", sg.get("K", tl.get("K")))
