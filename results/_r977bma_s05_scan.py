import subprocess, os, json, hashlib, re

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"

# --- 1. fleet orders diff (ack face = r964-era heartbeat backup = freshest) ---
hb = json.load(open(os.path.join(ROOT, "results/_quarantine/r964-estate-20261013/fleet__machines__bm-a.json"), encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
files = sorted(os.listdir(os.path.join(ROOT, "fleet", "orders")))
order_files = [f for f in files if f.startswith("O-") or f.startswith("MSG-")]
unacked = [f for f in order_files if f not in acked and f[:-3] not in acked]
print(f"fleet orders total={len(order_files)} acked={len(acked)} UNACKED={len(unacked)}")
for u in unacked:
    print("  UNACKED:", u)

# --- 2. group decisions/orders watermark (python raw-bytes canonical) ---
def group_show(path):
    r = subprocess.run([GIT, "-C", GRP, "show", f"origin/main:{path}"], capture_output=True)
    return r.stdout

st = json.load(open(os.path.join(ROOT, "state-bm-a.json"), encoding="utf-8"))
for key, path in [("last_decisions_sha", "docs/decisions.md"), ("last_orders_sha", "docs/orders.md")]:
    raw = group_show(path)
    sha = hashlib.sha256(raw).hexdigest()
    old = st.get(key, "")
    print(f"GROUP {path}: sha256={sha[:16]} state_key={str(old)[:16]} {'UNCHANGED' if sha==old else 'CHANGED'}")

# quick pull group repo first for freshness
subprocess.run([GIT, "-C", GRP, "fetch", "origin"], capture_output=True)
for key, path in [("last_decisions_sha", "docs/decisions.md"), ("last_orders_sha", "docs/orders.md")]:
    raw = group_show(path)
    sha = hashlib.sha256(raw).hexdigest()
    old = st.get(key, "")
    print(f"GROUP(fetch) {path}: sha256={sha[:16]} state_key={str(old)[:16]} {'UNCHANGED' if sha==old else 'CHANGED'}")
