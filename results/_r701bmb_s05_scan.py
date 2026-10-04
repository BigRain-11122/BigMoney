# r701 S0.5 order ledger scan + D-19 fresh-read gate (group decisions/orders)
import subprocess, json, hashlib, os, glob

# 1) local fleet/orders diff vs heartbeat ack set
hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
acked = set(hb.get("orders_ack", []))
orders = sorted(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
unacked = [o for o in orders if o not in acked]
print("local orders total:", len(orders), "acked:", len(acked),
      "unacked:", unacked)


def show_bytes(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    return r.returncode, r.stdout


# 2) group decisions.md fresh read (D-20261004-02(3) real-path recipe: this
#    worktree clone IS a local group-tree path -> fetch already done at S0)
st = json.load(open("state.json", encoding="utf-8"))
rc, dec = show_bytes("origin/main", "docs/decisions.md")
sha = hashlib.sha256(dec).hexdigest().upper() if rc == 0 else None
print("decisions sha:", sha, "| state watermark:", st.get("last_decisions_sha"),
      "| MATCH" if sha == st.get("last_decisions_sha") else "| CHANGED")

# 3) group orders.md fresh read (CEO pending physical-items section)
rc, o = show_bytes("origin/main", "docs/orders.md")
osha = hashlib.sha256(o).hexdigest().upper() if rc == 0 else None
print("orders sha:", osha, "| state watermark:", st.get("last_orders_sha"),
      "| MATCH" if osha == st.get("last_orders_sha") else "| CHANGED")
if rc == 0:
    tail = o.decode("utf-8", errors="replace").splitlines()[-12:]
    print("--- orders.md tail 12 ---")
    for ln in tail:
        print(ln)
