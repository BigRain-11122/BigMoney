"""r829 continuation S0.5 facts sweep (fresh, post-rebase onto origin tip 60918094d)."""
import subprocess, hashlib, json, os, re, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = os.path.join(ROOT, "results", "_r829bmc_s05_facts2.json")

def run(args, cwd=None):
    return subprocess.run(args, capture_output=True, cwd=cwd)

# 1. fetch group tree (non-fatal on failure -> last-good origin/main ref)
fr = run(["git", "-C", GROUP, "fetch", "origin"])
fetch_rc = fr.returncode
fetch_note = ("fetch rc=%d" % fetch_rc) + ((" stderr=" + fr.stderr.decode("utf-8", "replace")[:200]) if fr.returncode else "")

def blob_sha(path, algo):
    r = run(["git", "-C", GROUP, "show", "origin/main:" + path])
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")[:200]
    b = r.stdout
    h = hashlib.sha256(b).hexdigest() if algo == "sha256" else hashlib.sha1(b).hexdigest()
    return h, None

dec_sha, dec_err = blob_sha("docs/decisions.md", "sha256")
ord_sha, ord_err = blob_sha("docs/orders.md", "sha1")

# 2. state watermarks
state_path = os.path.join(ROOT, "state-bm-c.json")
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)
wm_dec = state.get("last_decisions_sha", "")
wm_ord = state.get("last_orders_sha", "")

dec_delta = (dec_sha is not None) and (dec_sha != wm_dec)
ord_delta = (ord_sha is not None) and (ord_sha != wm_ord)

# 3. orders diff: fleet/orders/*.md vs heartbeat orders_ack
orders_dir = os.path.join(ROOT, "fleet", "orders")
order_files = sorted([f for f in os.listdir(orders_dir) if re.match(r"O-.*\.md$", f)])
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
acked = set(hb.get("orders_ack", []) or [])
unacked = [f for f in order_files if f not in acked]

facts = {
    "round": "r829-cont",
    "ts": subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Date -Format o"],
                          capture_output=True).stdout.decode("utf-8", "replace").strip(),
    "fetch_note": fetch_note,
    "dec_sha256": dec_sha,
    "ord_sha1": ord_sha,
    "wm_dec": wm_dec,
    "wm_ord": wm_ord,
    "dec_delta": dec_delta,
    "ord_delta": ord_delta,
    "orders_total": len(order_files),
    "orders_unacked": unacked,
    "errors": [e for e in (dec_err, ord_err) if e],
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps(facts, ensure_ascii=False, indent=1))
