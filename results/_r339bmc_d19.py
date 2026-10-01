"""r339 bm-c D-19 decision watermark check (raw-blob SHA-256 law, r292/r503)."""
import subprocess, hashlib

repo = r"K:\Fluxgroup\FluxGroup"
data = subprocess.check_output(["git", "-C", repo, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(data).hexdigest().upper()
print("DEC_SHA", sha)

orders = subprocess.check_output(["git", "-C", repo, "show", "origin/main:docs/orders.md"]).decode("utf-8", errors="replace")
lines = orders.splitlines()
print("ORDERS_TAIL_BEGIN")
for ln in lines[-50:]:
    print(ln)
print("ORDERS_TAIL_END")
