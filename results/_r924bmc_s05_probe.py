# r924 bm-c S0.5 probe: fleet orders diff + group-tree DEC/ORD watermark dual-check
# method PIN (r583/r865 law): DEC = python raw-blob bytes SHA-256; ORD = git rev-parse blob SHA-1
import json, hashlib, subprocess, os, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP  = r"K:\Fluxgroup\FluxGroup"
out = {"round": 924, "machine": "bm-c"}

# 1) fleet\orders diff vs heartbeat orders_ack
ack = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
acked = set(ack.get("orders_ack", []))
files = sorted(f for f in os.listdir(os.path.join(ROOT, "fleet", "orders")) if f.startswith("O-") and f.endswith(".md"))
unacked = [f for f in files if f not in acked]
out["orders_files"] = len(files)
out["orders_unacked"] = unacked

# 2) group-tree fetch + dual watermark
def git(args):
    r = subprocess.run(["git", "-C", GRP] + args, capture_output=True)
    return r.returncode, r.stdout, r.stderr

rc, _, err = git(["fetch", "origin"])
out["grp_fetch_rc"] = rc
if rc != 0:
    out["grp_fetch_err"] = err.decode("utf-8", "replace")[:300]

rc, so, se = git(["show", "origin/main:docs/decisions.md"])
if rc == 0:
    dec_sha = hashlib.sha256(so).hexdigest()
    out["dec_sha"] = dec_sha
    out["dec_delta"] = dec_sha != ack.get("last_decisions_sha", "")
else:
    out["dec_error"] = se.decode("utf-8", "replace")[:300]

rc, so, se = git(["rev-parse", "origin/main:docs/orders.md"])
if rc == 0:
    ord_sha = so.decode().strip()
    out["ord_sha"] = ord_sha
    out["ord_delta"] = ord_sha != ack.get("last_orders_sha", "")
else:
    out["ord_error"] = se.decode("utf-8", "replace")[:300]

# 3) if ORD delta, extract new rows region for manual review (tail rows)
if out.get("ord_delta"):
    rc, so, se = git(["show", "origin/main:docs/orders.md"])
    if rc == 0:
        text = so.decode("utf-8", "replace")
        out["ord_tail"] = text[-3000:]

with open(os.path.join(ROOT, "results", "_r924bmc_s05_probe.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "ord_tail"}, ensure_ascii=False))
