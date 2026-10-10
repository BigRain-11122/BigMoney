"""r830 bm-c S0.5 facts sweep (clone of r829 sweep + inbox scan + repo ahead/behind)."""
import subprocess, hashlib, json, os, re

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = os.path.join(ROOT, "results", "_r835bmc_s05_facts2.json")

def run(args, cwd=None):
    return subprocess.run(args, capture_output=True, cwd=cwd)

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

state_path = os.path.join(ROOT, "state-bm-c.json")
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)
wm_dec = state.get("last_decisions_sha", "")
wm_ord = state.get("last_orders_sha", "")

dec_delta = (dec_sha is not None) and (dec_sha != wm_dec)
ord_delta = (ord_sha is not None) and (ord_sha != wm_ord)

orders_dir = os.path.join(ROOT, "fleet", "orders")
order_files = sorted([f for f in os.listdir(orders_dir) if re.match(r"O-.*\.md$", f)])
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
acked = set(hb.get("orders_ack", []) or [])
unacked = [f for f in order_files if f not in acked]

# inbox: unprocessed messages addressed to bm-c or ALL
inbox_dir = os.path.join(ROOT, "fleet", "inbox")
inbox = []
if os.path.isdir(inbox_dir):
    for f in sorted(os.listdir(inbox_dir)):
        if not (f.lower().endswith((".md", ".json", ".txt"))):
            continue
        p = os.path.join(inbox_dir, f)
        if os.path.isfile(p):
            try:
                txt = open(p, "r", encoding="utf-8", errors="replace").read(4000)
            except Exception:
                txt = ""
            if ("bm-c" in txt) or ("ALL" in txt):
                inbox.append(f)

# bigmoney repo ahead/behind vs origin
br = run(["git", "-C", ROOT, "fetch", "origin"])
behind = run(["git", "-C", ROOT, "rev-list", "--count", "HEAD..origin/main"])
ahead = run(["git", "-C", ROOT, "rev-list", "--count", "origin/main..HEAD"])

facts = {
    "round": "r830",
    "ts": subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Date -Format o"],
                          capture_output=True).stdout.decode("utf-8", "replace").strip(),
    "group_fetch_note": fetch_note,
    "dec_sha256": dec_sha,
    "ord_sha1": ord_sha,
    "wm_dec": wm_dec,
    "wm_ord": wm_ord,
    "dec_delta": dec_delta,
    "ord_delta": ord_delta,
    "orders_total": len(order_files),
    "orders_unacked": unacked,
    "inbox_pending": inbox,
    "repo_fetch_rc": br.returncode,
    "repo_behind": behind.stdout.decode("utf-8", "replace").strip(),
    "repo_ahead": ahead.stdout.decode("utf-8", "replace").strip(),
    "errors": [e for e in (dec_err, ord_err) if e],
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print(json.dumps(facts, ensure_ascii=False, indent=1))

