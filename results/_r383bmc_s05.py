"""r383 bm-c S0.5: (1) fleet/orders full-set diff vs heartbeat orders_ack
(r367 programmatic law, no window truncation); (2) D-19 decisions watermark:
fetch group tree, raw-blob SHA-256 of origin/main:docs/decisions.md vs state
key (r292/r503: upper() normalize both sides); read orders.md CEO physical
items for BigMoney lines. Zero-window subprocess throughout (U060)."""
import hashlib, json, os, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
CN = 0x08000000

def gsilent(cwd, *args):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True,
                       creationflags=CN)
    if r.returncode != 0:
        raise SystemExit(f"git {args[:2]} rc={r.returncode}: "
                         f"{r.stderr.decode('utf-8', 'replace')[:300]}")
    return r.stdout

# --- 1) orders full-set diff
orders_dir = os.path.join(ROOT, "fleet", "orders")
on_disk = sorted(os.listdir(orders_dir))
order_names = [f for f in on_disk if f.startswith("O-") and f.endswith(".md")]
with open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"),
          encoding="utf-8") as f:
    hb = json.load(f)
ack = set(hb.get("orders_ack", []))
pending = [o for o in order_names if o not in ack]
print(f"orders on disk={len(order_names)} acked={len(ack & set(order_names))} "
      f"pending={len(pending)}")
for p in pending:
    print("PENDING ORDER:", p)

# --- 2) D-19 decisions watermark (fresh-read law)
gsilent(GROUP, "fetch", "origin")
blob = gsilent(GROUP, "show", "origin/main:docs/decisions.md")
sha = hashlib.sha256(blob).hexdigest().upper()
with open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8") as f:
    st = json.load(f)
prev = (st.get("last_decisions_sha") or "").upper()
print(f"decisions sha={sha[:10]} state_key={prev[:10]} "
      f"match={'YES' if sha == prev else 'CHANGED'}")
if sha != prev:
    txt = blob.decode("utf-8", "replace")
    print("--- decisions.md tail 60 lines ---")
    for line in txt.splitlines()[-60:]:
        if line.strip():
            print(line[:220])

# --- 3) CEO physical items in group orders.md (BigMoney-relevant lines)
oblob = gsilent(GROUP, "show", "origin/main:docs/orders.md")
otxt = oblob.decode("utf-8", "replace")
hits = [l for l in otxt.splitlines()
        if ("BigMoney" in l or "bigmoney" in l or "量化" in l or "quant" in l.lower())
        and l.strip()]
print(f"orders.md BigMoney-relevant lines: {len(hits)}")
for h in hits[-15:]:
    print("CEO-ITEM:", h[:200])
