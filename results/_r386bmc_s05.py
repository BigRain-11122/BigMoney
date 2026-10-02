# r386 bm-c S0.5: orders full-set difference (r367 law) + D-19 decisions watermark + group orders.md
import subprocess, os, re, json, hashlib, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
NO_WINDOW = 0x08000000

def git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=NO_WINDOW)
    if r.returncode != 0:
        print("GIT-FAIL", args, r.stderr.strip())
    return r.stdout

def git_bytes(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, creationflags=NO_WINDOW)
    return r.stdout

# 1. orders full-set difference
orders_dir = os.path.join(REPO, "fleet", "orders")
all_orders = sorted([f[:-3] for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md")])
hb_path = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
acked = hb.get("orders_ack", [])
pending = [o for o in all_orders if o not in acked]
print("ORDERS-TOTAL", len(all_orders), "ACKED", len(acked), "PENDING", len(pending))
for p in pending:
    print("PENDING-ORDER", p)

# 2. D-19 decisions watermark (raw-blob bytes SHA-256, r292/r503 laws: case-insensitive compare)
git(["fetch", "origin"], GROUP)
blob = git_bytes(["show", "origin/main:docs/decisions.md"], GROUP)
sha = hashlib.sha256(blob).hexdigest().upper()
state = json.load(open(os.path.join(REPO, "state-bm-c.json"), encoding="utf-8"))
prev = state.get("last_decisions_sha", "").upper()
print("D19-SHA", sha)
print("D19-PREV", prev)
print("D19-VERDICT", "MATCH" if sha == prev else "CHANGED")
if sha != prev:
    text = blob.decode("utf-8", errors="replace")
    # print dispatch board block + tail 60 lines for consumption
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "派工通告板" in ln:
            print("=== DISPATCH BOARD from line", i + 1, "===")
            print("\n".join(lines[i:i + 40]))
            break
    print("=== TAIL 40 ===")
    print("\n".join(lines[-40:]))

# 3. group orders.md CEO physical-items section (orders involving BigMoney/quant)
oblob = git_bytes(["show", "origin/main:docs/orders.md"], GROUP)
otext = oblob.decode("utf-8", errors="replace")
print("=== GROUP ORDERS.MD (lines w/ BigMoney|quant|量化|实盘) ===")
for ln in otext.splitlines():
    if re.search(r"BigMoney|quant|量化|实盘", ln):
        print(ln[:300])
