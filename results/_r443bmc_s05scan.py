import json, hashlib, subprocess, os, glob

BASE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP  = r"K:\Fluxgroup\FluxGroup"

# 1) orders ack diff-set
hb = json.load(open(os.path.join(BASE, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
files = set(os.path.basename(p) for p in glob.glob(os.path.join(BASE, "fleet", "orders", "*.md")))
unacked = sorted(files - ack)
missing = sorted(ack - files)
print("ORDERS_FILES", len(files), "ACK", len(ack), "UNACKED", len(unacked), "MISSING", len(missing))
for f in unacked: print("  UNACKED:", f)
for f in missing: print("  MISSING-IN-DIR:", f)

# 2) group-tree fresh read (zero tree touch): fetch origin + raw blob hashes
def git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                          creationflags=0x08000000)  # CREATE_NO_WINDOW

r = git(["fetch", "origin"], GRP)
if r.returncode != 0:
    print("GRP_FETCH_RC", r.returncode, r.stderr.decode("utf-8", "replace")[:200])
r = git(["show", "origin/main:docs/decisions.md"], GRP)
dec_sha = hashlib.sha256(r.stdout).hexdigest().upper()
r2 = git(["show", "origin/main:docs/orders.md"], GRP)
ord_sha = hashlib.sha1(r2.stdout).hexdigest().upper()

st = json.load(open(os.path.join(BASE, "state-bm-c.json"), encoding="utf-8"))
old_dec = st.get("last_decisions_sha", "")
old_ord = st.get("last_orders_sha", "")
print("DECISIONS_SHA", dec_sha, "MATCH" if dec_sha == old_dec else "DRIFT")
print("GORDERS_SHA", ord_sha, "MATCH" if ord_sha == old_ord else "DRIFT")
if dec_sha != old_dec:
    open(os.path.join(BASE, "results", "_r443bmc_decisions_blob.md"), "wb").write(r.stdout)
    print("  decisions blob dumped -> results/_r443bmc_decisions_blob.md for consumption")
if ord_sha != old_ord:
    open(os.path.join(BASE, "results", "_r443bmc_gorders_blob.md"), "wb").write(r2.stdout)
    print("  gorders blob dumped -> results/_r443bmc_gorders_blob.md for consumption")
