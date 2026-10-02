"""r374 bm-c D-19 fresh-read: group decisions.md raw-blob SHA + orders.md
CEO physical-items face scan (r292 raw-bytes law; CREATE_NO_WINDOW on all child git)."""
import subprocess
import hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"
NO_WIN = 0x08000000
LAST = "937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1"

dec = subprocess.check_output(["git", "-C", GROUP, "show", "origin/main:docs/decisions.md"],
                              creationflags=NO_WIN)
sha = hashlib.sha256(dec).hexdigest().upper()
print("DEC_SHA=" + sha)
print("MATCH" if sha == LAST.upper() else "CHANGED")

orders = subprocess.check_output(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"],
                                 creationflags=NO_WIN)
text = orders.decode("utf-8", "replace")
hits = [ln.strip() for ln in text.splitlines()
        if ("bm-c" in ln.lower() or "bigmoney" in ln.lower() or "quant" in ln.lower())
        and ln.strip().startswith("-")]
print("ORDERS_HITS=" + str(len(hits)))
for h in hits[-8:]:
    print("ORD|" + h[:220])
