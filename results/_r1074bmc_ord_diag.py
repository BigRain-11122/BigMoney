"""r1074 bm-c: diagnostic -- current ORD content-sha1 vs state watermark key vs group-tree origin tip."""
import hashlib
import json
import subprocess

STATE = "state-bm-c.json"
GRP = r"K:\Fluxgroup\FluxGroup"

st = json.load(open(STATE, encoding="utf-8"))
print("state last_orders_sha :", st.get("last_orders_sha"))
print("state last_decisions_sha:", st.get("last_decisions_sha"))

blob = subprocess.run(
    ["git", "-C", GRP, "show", "origin/main:docs/orders.md"],
    capture_output=True,
).stdout
ord_sha = hashlib.sha1(blob).hexdigest()
print("live ORD content-sha1 :", ord_sha, "| bytes:", len(blob))

blob2 = subprocess.run(
    ["git", "-C", GRP, "show", "origin/main:docs/decisions.md"],
    capture_output=True,
).stdout
dec_sha = hashlib.sha256(blob2).hexdigest()
print("live DEC raw-blob sha256:", dec_sha, "| bytes:", len(blob2))

tip = subprocess.run(
    ["git", "-C", GRP, "rev-parse", "origin/main"],
    capture_output=True, text=True,
).stdout.strip()
print("group-tree origin/main tip:", tip)
log = subprocess.run(
    ["git", "-C", GRP, "log", "--oneline", "-3", "origin/main"],
    capture_output=True, text=True,
).stdout
print("group-tree last 3 commits:")
print(log)
