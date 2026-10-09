# r920 S0.5 scanner: fleet orders ack diff + group DEC/ORD watermark (python raw-bytes canonical per r814/r832)
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (results/ parent)
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
out = {}

# --- 1. fleet orders ack diff ---
orders_dir = os.path.join(REPO, "fleet", "orders")
hb_path = os.path.join(REPO, "fleet", "machines", "bm-a.json")
all_orders = sorted(f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md"))
acked = set()
if os.path.exists(hb_path):
    with open(hb_path, "rb") as f:
        hb = json.loads(f.read().decode("utf-8-sig"))
    acked = set(hb.get("orders_ack", []))
unacked = [o for o in all_orders if o not in acked]  # full-name compare per r919 fix
out["all_orders"] = len(all_orders)
out["unacked"] = unacked

# --- 2. group DEC/ORD watermark via C: real-path origin blob ---
def blob_sha(path):
    r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")[:200]
    return hashlib.sha256(r.stdout).hexdigest(), None

fr = subprocess.run(["git", "-C", GROUP, "fetch", "-q", "origin"], capture_output=True)
out["group_fetch_rc"] = fr.returncode
for key, path, prev in [
    ("dec", "docs/decisions.md", "bd94a27ba4ac39bc9a05037ddcfaf693cd78126aa6189711e8f7f1848a8ac522"),
    ("ord", "docs/orders.md", "b38eaaf8aec9e64ce9d1c7caa12aa5aebc50ae1d22e0eac8745994d960052507"),
]:
    sha, err = blob_sha(path)
    out[key + "_sha"] = sha
    out[key + "_err"] = err
    out[key + "_unchanged"] = (sha == prev)

print(json.dumps(out, ensure_ascii=True, indent=1))
