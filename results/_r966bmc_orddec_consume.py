# -*- coding: utf-8 -*-
"""r966 bm-c S0.5 ORD/DEC delta consumption: extract new rows since r965 watermarks.

Programmatic reads only (r583 law): shas computed from live blob bytes,
zero literal watermark constants -- state values read via json.
"""
import io, json, subprocess, hashlib, sys

GROUP = r"K:\Fluxgroup\FluxGroup"
STATE = r"state-bm-c.json"

state = json.load(io.open(STATE, encoding="utf-8"))
last_ord = state["last_orders_sha"]          # sha256 of blob bytes (canonical)
last_dec = state["last_decisions_sha"]

def blob_bytes(path):
    p = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True)
    if p.returncode != 0:
        print("BLOB-FAIL", path, p.stderr[:200]); sys.exit(2)
    return p.stdout

def sha256(b):
    return hashlib.sha256(b).hexdigest()

ord_b = blob_bytes("docs/orders.md")
dec_b = blob_bytes("docs/decisions.md")
ord_s, dec_s = sha256(ord_b), sha256(dec_b)
print("ORD blob sha256:", ord_s)
print("  vs state:", last_ord, "delta=", ord_s != last_ord)
print("DEC blob sha256:", dec_s)
print("  vs state:", last_dec, "delta=", dec_s != last_dec)

ord_t = ord_b.decode("utf-8", "replace")
dec_t = dec_b.decode("utf-8", "replace")

print("\n=== ORD rows dated 10-13 (all, for delta eyeball) ===")
seen = 0
for ln in ord_t.splitlines():
    if ("10-13" in ln or "2026-10-13" in ln) and ln.strip().startswith(("1", "2", "0", "-", "[")):
        seen += 1
        print(ln[:400])
print("ORD 10-13 rows total:", seen)

print("\n=== DEC rows/sections dated 2026-10-13 ===")
for ln in dec_t.splitlines():
    if "2026-10-13" in ln or "D-20261013" in ln or "C-20261013" in ln:
        print(ln[:400])

json.dump({"ord_sha256": ord_s, "dec_sha256": dec_s,
           "ord_delta": ord_s != last_ord, "dec_delta": dec_s != last_dec,
           "ts": "2026-10-13T12:4x"},
          io.open(r"results\_r966bmc_orddec_facts.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nfacts written results/_r966bmc_orddec_facts.json")
