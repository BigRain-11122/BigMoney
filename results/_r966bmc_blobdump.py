# -*- coding: utf-8 -*-
import io, json, subprocess, hashlib

GROUP = r"K:\Fluxgroup\FluxGroup"

def blob_bytes(path):
    p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True)
    if p.returncode != 0:
        raise SystemExit("BLOB-FAIL " + path)
    return p.stdout

ord_b = blob_bytes("docs/orders.md")
dec_b = blob_bytes("docs/decisions.md")
io.open(r"results\_r966bmc_orders_now.md", "wb").write(ord_b)
io.open(r"results\_r966bmc_decisions_now.md", "wb").write(dec_b)

# git log for the two files (recent commits touching them)
for path in ("docs/orders.md", "docs/decisions.md"):
    p = subprocess.run(["git", "-C", GROUP, "log", "--oneline", "-8", "--", path],
                       capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    io.open(r"results\_r966bmc_gitlog.txt", "a", encoding="utf-8").write(
        "== " + path + "\n" + out + "\n")
print("dumped; sha256 ord=%s dec=%s" % (hashlib.sha256(ord_b).hexdigest()[:16],
                                        hashlib.sha256(dec_b).hexdigest()[:16]))
