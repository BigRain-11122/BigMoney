import subprocess, hashlib, json, sys

FG = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def run(args, cwd):
    return subprocess.check_output(args, cwd=cwd, stderr=subprocess.STDOUT)

run(["git", "-C", FG, "fetch", "origin"], FG)
dec = run(["git", "-C", FG, "show", "origin/main:docs/decisions.md"], FG)
sha = hashlib.sha256(dec).hexdigest().upper()
with open(REPO + r"\state-bm-c.json", encoding="utf-8") as f:
    state = json.load(f)
prev = str(state.get("last_decisions_sha", "")).upper()
print("DEC_SHA=" + sha)
print("PREV_SHA=" + prev)
if sha == prev:
    print("MATCH-unchanged")
else:
    print("CHANGED")
    text = dec.decode("utf-8", errors="replace")
    print("---DEC_TAIL_4500---")
    print(text[-4500:])
    try:
        orders = run(["git", "-C", FG, "show", "origin/main:docs/orders.md"], FG).decode("utf-8", errors="replace")
        print("---ORDERS_TAIL_3000---")
        print(orders[-3000:])
    except Exception as e:
        print("orders read failed:", e)
