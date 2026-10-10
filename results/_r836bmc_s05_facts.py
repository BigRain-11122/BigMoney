import subprocess, hashlib, json, os, glob, time, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"

def run(args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, p.stdout, p.stderr

facts = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}

# group tree fetch (zero tree touch, blob reads only)
rc_f, so, se = run(["git", "-C", GRP, "fetch", "origin"])
facts["grp_fetch_rc"] = rc_f
if rc_f != 0:
    facts["grp_fetch_err"] = se.decode("utf-8", "replace")[:500]

rc_rev_dec, dec_blob, _ = run(["git", "-C", GRP, "rev-parse", "origin/main:docs/decisions.md"])
rc_rev_ord, ord_blob, _ = run(["git", "-C", GRP, "rev-parse", "origin/main:docs/orders.md"])
rc_d, dec, _ = run(["git", "-C,GRP".replace(",GRP", ""), "-C", GRP, "show", "origin/main:docs/decisions.md"])
rc_o, ordb, _ = run(["git", "-C", GRP, "show", "origin/main:docs/orders.md"])

facts["dec_blob"] = dec_blob.decode().strip()
facts["ord_blob"] = ord_blob.decode().strip()
facts["dec_sha256"] = hashlib.sha256(dec).hexdigest() if rc_d == 0 else None
facts["ord_sha1"] = hashlib.sha1(ordb).hexdigest() if rc_o == 0 else None

OLD_DEC = "34cf2538a7a4a8a97b07c56dc582238ec4fb8c49376a934ba0bcad0200266997"
OLD_ORD = "b31f0381c08ab51f26c82b044b1aa40fb7bd956d"

if facts["dec_sha256"] and facts["dec_sha256"] != OLD_DEC:
    rc_dd, ddiff, derr = run(["git", "-C", GRP, "diff", OLD_DEC, facts["dec_blob"]])
    facts["dec_delta"] = True
    facts["dec_diff"] = ddiff.decode("utf-8", "replace")[:9000]
else:
    facts["dec_delta"] = False

if facts["ord_sha1"] and facts["ord_sha1"] != OLD_ORD:
    rc_od, odiff, oerr = run(["git", "-C", GRP, "diff", OLD_ORD, facts["ord_blob"]])
    facts["ord_delta"] = True
    facts["ord_diff"] = odiff.decode("utf-8", "replace")[:9000]
else:
    facts["ord_delta"] = False

# fleet orders ack diff
order_files = sorted(glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md")))
order_ids = [os.path.basename(f)[:-3] for f in order_files]
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
acked = hb.get("orders_ack", [])
if isinstance(acked, dict):
    acked = list(acked.keys())
acked_set = set(acked)
unacked = [o for o in order_ids if o not in acked_set]
facts["orders_total"] = len(order_ids)
facts["acked_count"] = len(acked)
facts["unacked"] = unacked
facts["ack_ghost"] = [a for a in acked if a not in set(order_ids)][:20]

out = os.path.join(ROOT, "results", "_r836bmc_s05_facts.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)

brief = {k: facts.get(k) for k in ("ts", "grp_fetch_rc", "dec_sha256", "ord_sha1", "dec_delta", "ord_delta", "orders_total", "acked_count", "unacked", "ack_ghost")}
print(json.dumps(brief, ensure_ascii=True))
