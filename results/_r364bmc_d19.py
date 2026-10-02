"""r364 bm-c D-19 fresh-read: group decisions.md raw-blob SHA + orders.md
CEO physical-items face scan (r292 raw-bytes law, no PS pipeline transcoding)."""
import subprocess
import hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
LAST = "4FD50184453162A8B01C47D6CA79224B95869DB2487AA18E10D61479177F250C"

dec = subprocess.check_output(["git", "-C", GROUP, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(dec).hexdigest().upper()
print("DEC_SHA=" + sha)
print("MATCH" if sha == LAST.upper() else "CHANGED")

orders = subprocess.check_output(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"])
text = orders.decode("utf-8", "replace")
hits = [ln.strip() for ln in text.splitlines()
        if ("bm-c" in ln.lower() or "bigmoney" in ln.lower() or "quant" in ln.lower())
        and ln.strip().startswith("-")]
print("ORDERS_HITS=" + str(len(hits)))
for h in hits[-8:]:
    print("ORD|" + h[:220])
