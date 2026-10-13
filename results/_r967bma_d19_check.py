# r967 D-19 double watermark canonical check (python raw-bytes per law)
import subprocess, hashlib, json, sys

GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
STATE = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\state-bm-a.json"

def fetch_show(path):
    subprocess.run(["git", "-C", GRP, "fetch", "origin"], capture_output=True)
    r = subprocess.run(["git", "-C", GRP, "show", f"origin/main:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"show {path} rc={r.returncode}")
    return r.stdout

dec = fetch_show("docs/decisions.md")
ordr = fetch_show("docs/orders.md")
dec_sha = hashlib.sha256(dec).hexdigest().upper()
ord_sha = hashlib.sha256(ordr).hexdigest().upper()
print("decisions_sha:", dec_sha)
print("orders_sha:", ord_sha)

with open(STATE, encoding="utf-8") as f:
    st = json.load(f)
print("state last_decisions_sha:", st.get("last_decisions_sha"))
print("state last_orders_sha:", st.get("last_orders_sha"))
print("DEC_CHANGED:", dec_sha != st.get("last_decisions_sha"))
print("ORD_CHANGED:", ord_sha != st.get("last_orders_sha"))

# dump tails for consumption: decisions -> last '## 台账·2026-10-13' batch rows; orders -> tail 40 lines
dec_text = dec.decode("utf-8", "replace")
ord_text = ordr.decode("utf-8", "replace")
with open(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r967bma_dec_tail.txt", "w", encoding="utf-8") as f:
    f.write(dec_text[-6000:])
with open(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r967bma_ord_tail.txt", "w", encoding="utf-8") as f:
    f.write(ord_text[-9000:])
# count rows mentioning bigmoney/quant in the delta zone (after 10-12)
import re
tail_zone = dec_text[-20000:]
rows = [l for l in tail_zone.splitlines() if l.startswith("| 2026-10-1") and ("igMoney" in l or "igmoney" in l or "quant" in l.lower())]
print("DEC bigmoney-mention rows in tail zone:", len(rows))
for r in rows[-6:]:
    print("DEC-ROW:", r[:300])
ord_tail_zone = ord_text[-12000:]
orows = [l for l in ord_tail_zone.splitlines() if ("bigmoney" in l.lower() or "量化" in l or "BigMoney" in l) and l.strip().startswith("|")]
print("ORD bigmoney rows in tail:", len(orows))
for r in orows[-6:]:
    print("ORD-ROW:", r[:300])
