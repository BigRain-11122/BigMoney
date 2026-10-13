import subprocess, hashlib, json, os, glob

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"

def g(*args, cwd):
    return subprocess.run(["git", "-C", cwd] + list(args), capture_output=True).stdout

# 1) group tree fetch (zero tree touch)
g("fetch", "origin", cwd=GRP)

# DEC watermark: sha256 of raw blob bytes
dec = g("show", "origin/main:docs/decisions.md", cwd=GRP)
dec_sha = hashlib.sha256(dec).hexdigest()

# ORD watermark: blob SHA-1
ord_sha = g("rev-parse", "origin/main:docs/orders.md", cwd=GRP).decode().strip()

hb = json.load(open(os.path.join(BM, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
prev_dec = hb.get("last_decisions_sha", "")
prev_ord = hb.get("last_orders_sha", "")

# 2) local orders diff
acked = set(hb.get("orders_ack", []))
files = set()
for p in glob.glob(os.path.join(BM, "fleet", "orders", "O-*.md")):
    files.add(os.path.basename(p))
unacked = sorted(files - acked)

out = {
    "dec_delta": dec_sha != prev_dec,
    "dec_sha": dec_sha,
    "prev_dec_sha": prev_dec,
    "ord_delta": ord_sha != prev_ord,
    "ord_sha": ord_sha,
    "prev_ord_sha": prev_ord,
    "unacked_local": unacked,
    "acked_count": len(acked),
    "local_orders_count": len(files),
    "ts": "2026-10-14T05:2x",
}
print(json.dumps(out, indent=1))
open(os.path.join(BM, "results", "_r984bmc_s05_probe.json"), "w").write(json.dumps(out, indent=1))
