"""r565 bm-b D-19 decisions watermark check (r481 bm-b recipe: temp partial clone, r292 raw-bytes SHA law)."""
import subprocess, os, sys, hashlib, json

TMP = os.path.join(os.environ.get("TEMP", r"C:\Users\Administrator\AppData\Local\Temp"), "fg-dec-bmb")
REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, capture_output=True, cwd=cwd)
    if check and r.returncode != 0:
        print("CMD_FAIL:", cmd[:6], "rc=", r.returncode, r.stderr.decode("utf-8", "replace")[:300])
        sys.exit(2)
    return r

if not os.path.isdir(os.path.join(TMP, ".git")):
    run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
         "git@github.com:BigRain-11122/FluxGroup.git", TMP])
run(["git", "-C", TMP, "fetch", "origin"], check=False)  # fetch failure = transient family, fail-open per Step0Preflight

dec = run(["git", "-C", TMP, "show", "origin/main:docs/decisions.md"]).stdout
sha = hashlib.sha256(dec).hexdigest().upper()
state = json.load(open(os.path.join(REPO, "state.json"), encoding="utf-8"))
old = state.get("last_decisions_sha", "").upper()
print("decisions_sha_new:", sha)
print("decisions_sha_old:", old)
print("MATCH" if sha == old else "CHANGED")

# CEO pending-orders physical file section (same fresh-read law)
orders = run(["git", "-C", TMP, "show", "origin/main:docs/orders.md"]).stdout.decode("utf-8", "replace")
lines = [l for l in orders.splitlines() if "BigMoney" in l or "quant" in l or "本司" in l or "股票炉" in l]
print("--- orders.md lines touching BigMoney/quant (last 15) ---")
for l in lines[-15:]:
    print(l[:200])
print("ORDERS_LINES_SHOWN")
