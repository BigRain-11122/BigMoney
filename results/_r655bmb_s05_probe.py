# r655 bm-b S0.5+D-19 probe: orders ack diff (same-caliber set compare r646 law)
# + D-19 fresh-read via group origin blob (r631 law: git show origin bytes, no tree read)
import json, hashlib, os, subprocess, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
hb = json.load(open(os.path.join(root, "fleet", "machines", "bm-b.json"), encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
files = set(f for f in os.listdir(os.path.join(root, "fleet", "orders")) if f.startswith("O-") and f.endswith(".md"))
missing = sorted(files - ack)
stale = sorted(ack - files)
print("ORDERS total=%d ack=%d missing_ack=%d stale_ack=%d" % (len(files), len(ack), len(missing), len(stale)))
for m in missing:
    p = os.path.join(root, "fleet", "orders", m)
    txt = open(p, encoding="utf-8", errors="replace").read(600)
    print("=== NEW ORDER %s ===" % m)
    print(txt)
    print("=== END %s ===" % m)

# D-19 decisions + group orders fresh read (origin blob bytes only)
grp = r"C:\Fluxgroup\FluxGroup"
def show_bytes(path):
    r = subprocess.run(["git", "-C", grp, "show", "origin/main:" + path], capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")
    return r.stdout, None

subprocess.run(["git", "-C", grp, "fetch", "origin"], capture_output=True)
st = json.load(open(os.path.join(root, "state.json"), encoding="utf-8"))
for label, key, path in [("DECISIONS", "last_decisions_sha", "docs/decisions.md"),
                         ("GORDERS", "last_orders_sha", "docs/orders.md")]:
    b, err = show_bytes(path)
    if b is None:
        print("%s FETCH_FAIL %s" % (label, err.strip()[:200]))
        continue
    sha = hashlib.sha256(b).hexdigest().upper()
    prev = st.get(key, "")
    print("%s sha=%s prev_match=%s bytes=%d" % (label, sha[:16], "MATCH" if sha == prev else "CHANGED", len(b)))
    if sha != prev:
        open(os.path.join(root, "results", "_r655bmb_%s_new.txt" % label.lower()), "wb").write(b)
        print("%s CHANGED -> full blob dumped to results/_r655bmb_%s_new.txt" % (label, label.lower()))
print("PROBE_DONE")
