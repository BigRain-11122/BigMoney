# r1000 S0.5 dual-delta consume: fetch group tree, compute pinned-method watermarks, diff vs state keys, print new rows
import subprocess, hashlib, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GT = r"K:\Fluxgroup\FluxGroup"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def show(path):
    # raw bytes from origin blob (no PS pipe) per r938 law
    return subprocess.check_output([GIT, "-C", GT, "show", "origin/main:%s" % path])

subprocess.run([GIT, "-C", GT, "fetch", "origin"], capture_output=True)

ord_bytes = show("docs/orders.md")
dec_bytes = show("docs/decisions.md")
ord_sha1 = hashlib.sha1(ord_bytes).hexdigest()   # ORD pin: content-bytes sha1
dec_sha256 = hashlib.sha256(dec_bytes).hexdigest()  # DEC pin: raw-blob bytes sha256

state = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", encoding="utf-8"))
old_ord = state.get("last_orders_sha", "")
old_dec = state.get("last_decisions_sha", "")

print("ORD: old=%s new=%s delta=%s" % (old_ord, ord_sha1, ord_sha1 != old_ord))
print("DEC: old=%s new=%s delta=%s" % (old_dec, dec_sha256, dec_sha256 != old_dec))

ord_text = ord_bytes.decode("utf-8", errors="replace")
dec_text = dec_bytes.decode("utf-8", errors="replace")

import re
ord_lines = ord_text.splitlines()
new_ord = [l for l in ord_lines if "2026-10-14" in l]
print("--- ORD 10-14 rows (%d) tail 40: ---" % len(new_ord))
for l in new_ord[-40:]:
    print(l[:400])

dec_lines = dec_text.splitlines()
new_dec = [l for l in dec_lines if "2026-10-14" in l]
print("--- DEC 10-14 rows (%d) tail 20: ---" % len(new_dec))
for l in new_dec[-20:]:
    print(l[:400])
