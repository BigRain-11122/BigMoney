"""r317 bm-c D-19 fresh-read check: group decisions.md raw-blob SHA-256 + orders.md BigMoney hits.
r292 law: python subprocess raw bytes (PS pipeline = transcoding false-drift).
r503 law: uppercase-normalize both sides before compare.
"""
import subprocess
import hashlib

GR = r"K:\Fluxgroup\FluxGroup"

d = subprocess.check_output(["git", "-C", GR, "show", "origin/main:docs/decisions.md"])
print("D19SHA=" + hashlib.sha256(d).hexdigest().upper())

o = subprocess.run(
    ["git", "-C", GR, "show", "origin/main:docs/orders.md"],
    capture_output=True,
).stdout.decode("utf-8", errors="replace")
lines = [l for l in o.splitlines() if ("BigMoney" in l or "quant" in l or "bm-" in l)]
print("ORDERS_HITS=" + str(len(lines)))
for l in lines[-25:]:
    print(" | " + l[:220])
