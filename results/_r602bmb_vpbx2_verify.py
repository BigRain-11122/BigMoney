# r602 bm-b: verify stranded FUND-VALUE-P1 VALUE-PB x2 products completeness before targeted delivery (r586 heal)
import json, os
base = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\fund_value_p1"
cells = os.path.join(base, "cells_VALUE-PB_x2.jsonl")
cont = os.path.join(base, "cont_VALUE-PB_x2.json")

rows = [json.loads(l) for l in open(cells, encoding="utf-8") if l.strip()]
print("cells rows:", len(rows))
for r in rows:
    print("row keys:", sorted(r.keys())[:10])
    print("cell/face:", r.get("cell"), r.get("face"), "| done:", r.get("done"), "| sharpe:", r.get("sharpe"))
c = json.load(open(cont, encoding="utf-8"))
print("cont keys:", sorted(c.keys()))
print("cont: cell=%s face=%s n_days=%s n_trades=%s nav_last=%.2f ret_full=%s" % (
    c.get("cell"), c.get("face"), c.get("n_days"), c.get("n_trades"), c.get("nav_last", 0), c.get("ret_full")))
# nulls live-write face must NOT be in flight-committed: report presence only
nz = os.path.join(base, "nulls.jsonl")
print("nulls.jsonl exists:", os.path.exists(nz), "| size:", os.path.getsize(nz) if os.path.exists(nz) else 0)
