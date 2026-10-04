"""r478 bm-c S0.5 orders same-caliber set-diff + D-19 dual-key watermark probe.

Laws: r646 same-caliber same-form set diff (full filenames w/ .md);
r458 per-key hash caliber (decisions=SHA-256, group-orders=SHA-1);
r660 raw-blob bytes via python subprocess (zero PS pipeline, zero disk-copy hash);
ASCII-only stdout (pit-encoding console law).
"""
import hashlib
import json
import os
import subprocess
import sys

CREATE = 0x08000000
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"

# --- S0.5: orders vs orders_ack (full-filename form, both sides) ---
orders_dir = os.path.join(REPO, "fleet", "orders")
orders = sorted(f for f in os.listdir(orders_dir)
                if f.startswith("O-") and f.endswith(".md"))
hb_path = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hb_path, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
acks = set(hb.get("orders_ack", []))
orders_set = set(orders)
unacked = sorted(orders_set - acks)
ack_extra = sorted(a for a in acks - orders_set if a != "README.md")

# --- D-19: group tree raw-blob dual-key hash ---
def blob(repo, path):
    p = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path],
                       capture_output=True, creationflags=CREATE)
    if p.returncode != 0:
        return None, p.stderr.decode("utf-8", "replace").strip()
    return p.stdout, None

dec, dec_err = blob(GROUP, "docs/decisions.md")
gord, gord_err = blob(GROUP, "docs/orders.md")
dec_sha = hashlib.sha256(dec).hexdigest().upper() if dec else None
gord_sha = hashlib.sha1(gord).hexdigest().upper() if gord else None

st_path = os.path.join(REPO, "state-bm-c.json")
with open(st_path, "r", encoding="utf-8") as fh:
    st = json.load(fh)
state_dec = st.get("last_decisions_sha")
state_ord = st.get("last_orders_sha")

res = {
    "orders_total": len(orders),
    "acks_total": len(acks),
    "unacked": unacked,
    "ack_extra_non_README": ack_extra,
    "decisions_sha256": dec_sha,
    "state_decisions_sha256": state_dec,
    "decisions_match": dec_sha == state_dec if dec_sha and state_dec else None,
    "group_orders_sha1": gord_sha,
    "state_group_orders_sha1": state_ord,
    "group_orders_match": gord_sha == state_ord if gord_sha and state_ord else None,
    "dec_err": dec_err,
    "gord_err": gord_err,
}
print(json.dumps(res, indent=1, ensure_ascii=True))
