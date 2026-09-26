# _r293bma_closure_s05.py -- R293 closure session S0.5 scans (orders diff + group orders.md + decisions.md)
import json, os, re, glob, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GDOCS = r"C:\Users\sjs20\Desktop\FluxGroup\docs"

# 1) fleet/orders diff vs heartbeat orders_ack (R13: enumerate ALL, no timestamp filter)
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-a.json"), encoding="utf-8"))
ack_raw = hb.get("orders_ack", "")
ack_tokens = set(ack_raw.split())
orders = []
for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md")):
    base = os.path.basename(p)
    stem = base[:-3] if base.endswith(".md") else base
    orders.append(base)
    if base not in ack_tokens and stem not in ack_tokens:
        print("UNACKED:", base)
print(f"orders_scan: {len(orders)} O-files, ack_tokens={len(ack_tokens)}, unacked=listed above (none if empty)")

# 2) group docs/orders.md full-file scan for @BigMoney/quant dispatched lines (R287 law)
op = os.path.join(GDOCS, "orders.md")
if os.path.exists(op):
    txt = io.open(op, encoding="utf-8", errors="replace").read()
    hits = [l.strip() for l in txt.splitlines() if re.search(r"BigMoney|@quant", l)]
    print(f"group_orders.md: {len(hits)} @BigMoney/quant lines (receipt check below)")
    for l in hits:
        print("  L:", l[:160])
else:
    print("group_orders.md: NOT FOUND")

# 3) group docs/decisions.md new lines after D-20260927-05 (R292 audited 01..05)
dp = os.path.join(GDOCS, "decisions.md")
if os.path.exists(dp):
    lines = io.open(dp, encoding="utf-8", errors="replace").read().splitlines()
    known = [l for l in lines if re.match(r"^##?\s*D-2026092[56]", l) or "D-20260927-0" in l[:40]]
    new = [l for l in lines if re.search(r"D-2026092[67]-\d+", l) and not re.search(r"D-2026092[567]-(0[1-5])\b", l)]
    print(f"decisions.md: total lines={len(lines)}")
    for l in new[:10]:
        print("  NEW?:", l[:160])
else:
    print("decisions.md: NOT FOUND")

# 4) autofill tick state (04:50 tick check)
af = json.load(open(os.path.join(ROOT, "results", "autofill_state.json"), encoding="utf-8"))
lt = af.get("last_tick", {})
print(f"autofill last_tick: ts={lt.get('ts')} verdict={lt.get('verdict')} launches_n={len(af.get('launches', []))}")
