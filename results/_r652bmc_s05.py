import subprocess, hashlib, json, os, re

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"

def git(*args, cwd=None):
    r = subprocess.run(["git", "-C", cwd or ROOT] + list(args),
                       capture_output=True)
    return r.returncode, r.stdout, r.stderr

# group tree fresh fetch (D-20260930-19 law: never read working-tree copy)
rc, _, err = git("fetch", "origin", cwd=GRP)
fetch_rc = rc
rc, dec, err1 = git("show", "origin/main:docs/decisions.md", cwd=GRP)
rc, ordb, err2 = git("show", "origin/main:docs/orders.md", cwd=GRP)
dec_sha = hashlib.sha256(dec).hexdigest().upper() if dec else "MISSING"
ord_sha = hashlib.sha1(ordb).hexdigest().upper() if ordb else "MISSING"

# fleet orders ack diff
orders = sorted(f for f in os.listdir(os.path.join(ROOT, "fleet", "orders"))
                if f.startswith("O-") and f.endswith(".md"))
hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = [o for o in orders if o not in ack]

# state watermarks
st = json.load(open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8"))
prev_dec = st.get("last_decisions_sha", "")
prev_ord = st.get("last_orders_sha", "")

# inbox unread
inbox_dir = os.path.join(ROOT, "fleet", "inbox")
inbox = sorted(f for f in os.listdir(inbox_dir) if f.endswith(".md") or f.endswith(".json")) if os.path.isdir(inbox_dir) else []

facts = {
    "round": 652,
    "fetch_rc": fetch_rc,
    "dec_sha": dec_sha, "prev_dec_sha": prev_dec, "dec_delta": dec_sha != prev_dec,
    "ord_sha": ord_sha, "prev_ord_sha": prev_ord, "ord_delta": ord_sha != prev_ord,
    "dec_bytes": len(dec), "ord_bytes": len(ordb),
    "fleet_orders_total": len(orders), "unacked": unacked,
    "inbox_unread": inbox,
    "shape_assert": bool(re.fullmatch(r"[0-9A-F]{64}", dec_sha)) and bool(re.fullmatch(r"[0-9A-F]{40}", ord_sha)),
}
out = os.path.join(ROOT, "results", "_r652bmc_s05_facts.json")
json.dump(facts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: facts[k] for k in ("dec_sha","dec_delta","ord_sha","ord_delta","fleet_orders_total","unacked","inbox_unread","shape_assert")}, ensure_ascii=False))
