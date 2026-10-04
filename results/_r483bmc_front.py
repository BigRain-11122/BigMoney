"""r483 bm-c front probe: orders diff + D-19 group dual-hash + fleet tasks
+ watermark red flag. All git via subprocess with CREATE_NO_WINDOW (U060).
Output: results/_r483bmc_front.json"""
import json
import os
import subprocess
import hashlib

CNW = 0x08000000
OUT = {}
REPO = os.getcwd()
GRP = r"K:\Fluxgroup\FluxGroup"


def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                       creationflags=CNW)
    return r


# 1) orders diff (same-shape full-filename sets, r477/r646 law)
r = git(["ls-tree", "--name-only", "origin/main", "fleet/orders/"], REPO)
orders = set(l.strip().split("/")[-1] for l in
             r.stdout.decode("utf-8", "replace").splitlines()
             if l.strip().endswith(".md"))
ack = set(json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
          ["orders_ack"])
unacked = sorted(orders - ack)
OUT["orders_total"] = len(orders)
OUT["orders_unacked"] = unacked

# 2) D-19 group decisions (SHA-256) + group orders.md (SHA-1), raw-blob law
r = git(["fetch", "origin"], GRP)
OUT["grp_fetch_rc"] = r.returncode
if r.returncode == 0:
    for path, key, algo in [("docs/decisions.md", "dec", "sha256"),
                            ("docs/orders.md", "grp_orders", "sha1")]:
        b = git(["show", "origin/main:" + path], GRP)
        if b.returncode != 0:
            OUT[key + "_err"] = b.stderr.decode("utf-8", "replace")[:200]
            continue
        h = hashlib.new(algo)
        h.update(b.stdout)
        OUT[key + "_sha"] = h.hexdigest().upper()
state = json.load(open("state-bm-c.json", encoding="utf-8"))
OUT["d19_match"] = (OUT.get("dec_sha") == state.get("last_decisions_sha"))
OUT["grp_orders_match"] = (OUT.get("grp_orders_sha") == state.get(
    "last_orders_sha"))

# 3) fleet tasks open scan
tk_dir = os.path.join(REPO, "fleet", "tasks")
open_t = []
for fn in sorted(os.listdir(tk_dir)):
    if not fn.endswith(".json"):
        continue
    try:
        t = json.load(open(os.path.join(tk_dir, fn), encoding="utf-8"))
    except Exception as e:
        open_t.append({"file": fn, "err": str(e)[:80]})
        continue
    st = t.get("status")
    if st in ("open",):
        open_t.append({"file": fn, "id": t.get("task_id") or t.get("id"),
                       "status": st, "title": str(t.get("title"))[:120]})
OUT["tasks_open"] = open_t

# 4) watermark red flag (local face, gitignored)
wm_path = os.path.join(REPO, "results", "watermark_red.json")
if os.path.exists(wm_path):
    wm = json.load(open(wm_path, encoding="utf-8"))
    OUT["watermark_red"] = bool(wm.get("red"))
    OUT["watermark_why"] = str(wm.get("why", wm.get("reason", "")))[:300]
else:
    OUT["watermark_red"] = None
    OUT["watermark_why"] = "watermark_red.json absent"

with open("results/_r483bmc_front.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print(json.dumps(OUT, ensure_ascii=False, indent=1))
