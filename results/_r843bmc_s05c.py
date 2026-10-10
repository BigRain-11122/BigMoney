import json, subprocess, hashlib, io
GRP = r"K:\Fluxgroup\FluxGroup"
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
r = subprocess.run(["git","-C",GRP,"show","origin/main:docs/orders.md"], capture_output=True, timeout=30)
ob = r.stdout.decode("utf-8","replace")
r2 = subprocess.run(["git","-C",GRP,"show","origin/main:docs/decisions.md"], capture_output=True, timeout=30)
db = r2.stdout.decode("utf-8","replace")
lines = ob.splitlines()
rows = [l for l in lines if l.startswith("|")]
# find last consumed marker: the 10-10 23:5x row (O-20261010-2350)
idx2350 = max(i for i,l in enumerate(rows) if "O-20261010-2350" in l or "23:5x" in l[:20])
new_ord = rows[idx2350+1:]
drows = [l for l in db.splitlines() if l.startswith("|")]
# decisions: last consumed = D-20261010-02 orders-row batch (r831 consumed D-11/12 + C-01/02; r842 consumed nothing new)
# find index of D-20261010-12 or the last "2026-10-10 | D-20261010-1" row
idx = max(i for i,l in enumerate(drows) if "D-20261010-1" in l[:60] or "D-20261010-02" in l[:80])
new_dec = drows[idx+1:]
out = {
 "orders_sha1": hashlib.sha1(ob.encode()).hexdigest(),
 "decisions_sha256": hashlib.sha256(db.encode()).hexdigest(),
 "new_orders_count": len(new_ord),
 "new_orders": new_ord,
 "new_decisions_count": len(new_dec),
 "new_decisions": new_dec,
}
with io.open(ROOT + r"\results\_r843bmc_s05_delta.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("written:", len(new_ord), "new ord rows,", len(new_dec), "new dec rows")
print("orders_sha1:", out["orders_sha1"])
print("decisions_sha256:", out["decisions_sha256"])
