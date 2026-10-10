"""r949 bm-a: S0.5 dual scan (content-addressed, zero timestamp filters).

Leg 1: local fleet/orders O-*.md face vs heartbeat orders_ack diff set.
Leg 2: group decisions/orders watermark via C: Desktop real-path
       (state-bm-a provenance method: fetch + git show origin/main,
       python subprocess raw-bytes, SHA-256), compare vs stored keys.
Read-only; prints JSON verdict. Exit 0.
"""
import hashlib
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
ORD_DIR = os.path.join(ROOT, "fleet", "orders")
GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
STATE = os.path.join(ROOT, "state-bm-a.json")

out = {"leg1": {}, "leg2": {}, "err": None}

# ---- Leg 1: local orders vs ack diff ----
try:
    hb = json.load(open(HB, encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))
    files = sorted(f for f in os.listdir(ORD_DIR)
                   if f.startswith("O-") and f.endswith(".md"))
    unacked = [f for f in files if f[:-3] not in ack]
    # hash of local orders face for change detection
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode("utf-8"))
        h.update(open(os.path.join(ORD_DIR, f), "rb").read())
    out["leg1"] = {"order_files": len(files), "ack_entries": len(ack),
                   "unacked": unacked, "face_sha256": h.hexdigest()}
except Exception as e:
    out["leg1"] = {"err": repr(e)}

# ---- Leg 2: group watermark via Desktop real-path ----
try:
    st = json.load(open(STATE, encoding="utf-8"))
    r = subprocess.run(["git", "-C", GROUP, "fetch", "origin"],
                       capture_output=True)
    blobs = {}
    for key, path in (("decisions", "docs/decisions.md"),
                      ("orders", "docs/orders.md")):
        b = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                           capture_output=True)
        blobs[key] = b.stdout if b.returncode == 0 else None
    d_sha = hashlib.sha256(blobs["decisions"]).hexdigest() if blobs["decisions"] else None
    o_sha = hashlib.sha256(blobs["orders"]).hexdigest() if blobs["orders"] else None
    out["leg2"] = {
        "fetch_rc": r.returncode,
        "decisions_sha256": d_sha,
        "decisions_baseline": st.get("last_decisions_sha"),
        "decisions_changed": d_sha != st.get("last_decisions_sha"),
        "orders_sha256": o_sha,
        "orders_baseline": st.get("last_orders_sha"),
        "orders_changed": o_sha != st.get("last_orders_sha"),
    }
except Exception as e:
    out["leg2"] = {"err": repr(e)}

print(json.dumps(out, ensure_ascii=False, indent=1))
