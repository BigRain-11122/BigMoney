# r823 bm-c S0.5 facts sweep: group DEC/ORD watermark compare + unacked orders + fleet tasks open scan
# facts-driven, sha PROGRAMMATIC from state file, ZERO literal constants (r583 law)
import subprocess, hashlib, json, os, glob

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"
OUT = os.path.join(BM, "results", "_r823bmc_s05_facts.json")

def run(args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, p.stdout, p.stderr

facts = {}
# 1) group fetch (SSH primary leg)
rc, so, se = run(["git", "-C", GRP, "fetch", "origin"])
facts["fetch_rc"] = rc
facts["fetch_err"] = se.decode("utf-8", "replace")[:300]

# 2) decisions.md blob -> SHA-256
rc, so, se = run(["git", "-C", GRP, "show", "origin/main:docs/decisions.md"])
facts["dec_rc"] = rc
dec_b = so if rc == 0 else b""
facts["dec_sha256"] = hashlib.sha256(dec_b).hexdigest() if rc == 0 else None

# 3) orders.md blob -> SHA-1 (ALGORITHM PIN r537)
rc, so, se = run(["git", "-C", GRP, "show", "origin/main:docs/orders.md"])
facts["ord_rc"] = rc
ord_b = so if rc == 0 else b""
facts["ord_sha1"] = hashlib.sha1(ord_b).hexdigest() if rc == 0 else None

# 4) compare against state watermarks
with open(os.path.join(BM, "state-bm-c.json"), encoding="utf-8") as f:
    st = json.load(f)
facts["dec_delta"] = bool(facts["dec_sha256"] and facts["dec_sha256"] != st.get("last_decisions_sha"))
facts["ord_delta"] = bool(facts["ord_sha1"] and facts["ord_sha1"] != st.get("last_orders_sha"))

# 5) relevant new rows on delta
if facts["dec_delta"]:
    txt = dec_b.decode("utf-8", "replace")
    rows = [l.strip() for l in txt.splitlines()
            if ("BigMoney" in l or "bigmoney" in l or "quant" in l)
            and ("20261010" in l or "2026-10-10" in l or "D-20261010" in l)]
    facts["dec_rows_relevant"] = rows[-25:]
if facts["ord_delta"]:
    txt = ord_b.decode("utf-8", "replace")
    rows = [l.strip() for l in txt.splitlines()
            if ("bm-c" in l or "BigMoney" in l or "bigmoney" in l or "quant" in l)
            and "20261010" in l]
    facts["ord_rows_relevant"] = rows[-30:]

# 6) bigmoney fleet/orders unacked diff (heartbeat ack set = canonical)
hb_path = os.path.join(BM, "fleet", "machines", "bm-c.json")
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
ack = set(hb.get("orders_ack", []))
files = set(os.listdir(os.path.join(BM, "fleet", "orders")))
facts["unacked_orders"] = sorted(files - ack)

# 7) fleet tasks open/claimable scan
open_tasks = []
for p in glob.glob(os.path.join(BM, "fleet", "tasks", "*.json")):
    try:
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
        if t.get("status") == "open":
            open_tasks.append({"file": os.path.basename(p), "id": t.get("id", ""), "to": t.get("assigned_to", t.get("to", ""))})
    except Exception as e:
        open_tasks.append({"file": os.path.basename(p), "err": str(e)[:80]})
facts["fleet_tasks_open"] = open_tasks

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps({k: facts.get(k) for k in
      ["fetch_rc", "dec_delta", "ord_delta", "dec_sha256", "ord_sha1",
       "unacked_orders", "fleet_tasks_open"]}, ensure_ascii=False))
