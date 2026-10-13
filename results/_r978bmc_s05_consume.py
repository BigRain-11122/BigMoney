# -*- coding: utf-8 -*-
# r978 S0.5 ground-truth consumption: fetch group tree, extract new ORD rows
# vs prior fresh dump (r977, content-sha1 watermark 91d9fad3 era), classify lanes.
import subprocess, hashlib, json, sys
sys.stdout.reconfigure(encoding="utf-8")

G = r"K:\Fluxgroup\FluxGroup"
BQ = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PREV_DUMP = BQ + r"\results\_r977bmc_ord_fresh.md"
NEW_DUMP = BQ + r"\results\_r978bmc_ord_fresh.md"

def run(args, binary=False):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True)
    if r.returncode != 0:
        print("GIT-FAIL", args, r.stderr.decode("utf-8", "replace")[:200]); sys.exit(2)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

run(["fetch", "origin"])
ord_raw = run(["show", "origin/main:docs/orders.md"], binary=True)
ord_sha1 = hashlib.sha1(ord_raw).hexdigest()
dec_raw = run(["show", "origin/main:docs/decisions.md"], binary=True)
dec_sha256 = hashlib.sha256(dec_raw).hexdigest()

prev = open(PREV_DUMP, "rb").read()
# dumps carry a small header; compare content bodies
prev_lines = set(l.rstrip("\r\n") for l in prev.decode("utf-8", "replace").splitlines())
new_lines = ord_raw.decode("utf-8", "replace").splitlines()
added = [l.rstrip("\r") for l in new_lines if l.rstrip("\r") not in prev_lines]

with open(NEW_DUMP, "wb") as f:
    f.write(ord_raw)

facts = {
    "ord_sha1_now": ord_sha1, "ord_wm": "91d9fad36a054a842b366cc5b8844b58a99fd9a8",
    "ord_delta": ord_sha1 != "91d9fad36a054a842b366cc5b8844b58a99fd9a8",
    "dec_sha256_now": dec_sha256, "dec_wm": "86187eff59851ded73aa827b6251ca997adf57318e74571800c6838bdffc04e7",
    "dec_delta": dec_sha256 != "86187eff59851ded73aa827b6251ca997adf57318e74571800c6838bdffc04e7",
    "added_rows": len(added),
    "origin_tip": run(["rev-parse", "origin/main"]).strip(),
    "ts": "2026-10-14 01:4x",
}
print(json.dumps(facts, ensure_ascii=False, indent=1))
print("=== ORD ADDED LINES (%d) ===" % len(added))
for l in added:
    print(l[:500])
