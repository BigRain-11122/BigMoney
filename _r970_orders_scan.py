import json, os, re, glob

HB = r"fleet\machines\bm-a.json"
ORD = r"fleet\orders"

hb = json.load(open(HB, encoding="utf-8"))
ack = hb.get("orders_ack", {})
acked = set(ack.keys()) if isinstance(ack, dict) else set(ack)

files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ORD, "O-*.md")))
unacked = [f for f in files if f not in acked]

print(f"total O-files: {len(files)} | acked keys: {len(acked)} | unacked: {len(unacked)}")
for f in unacked:
    print("  UNACKED:", f)

# for any unacked, check addressee relevance to bm-a
for f in unacked:
    txt = open(os.path.join(ORD, f), encoding="utf-8", errors="replace").read()
    rel = []
    for pat, name in [(r"@bm-a\b", "bm-a"), (r"@ALL\b", "ALL"), (r"bigmoney", "bigmoney"), (r"quant", "quant")]:
        if re.search(pat, txt, re.I):
            rel.append(name)
    print(f"  relevance {f}: {rel}")
