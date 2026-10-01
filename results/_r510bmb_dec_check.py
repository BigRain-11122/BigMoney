"""r510 bm-b D-19 decisions water-mark check (r481 temp-partial-clone recipe,
r292 raw-bytes SHA-256, r503 upper()-normalized compare)."""
import hashlib
import os
import subprocess
import sys

D = os.path.join(os.environ["TEMP"], "fg-dec-bmb")


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True)


r = sh(["git", "-C", D, "rev-parse", "--git-dir"])
if r.returncode != 0:
    sh(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
        "git@github.com:BigRain-11122/FluxGroup.git", D])
sh(["git", "-C", D, "fetch", "origin"])
blob = sh(["git", "-C", D, "show", "origin/main:docs/decisions.md"])
if blob.returncode != 0:
    print("FETCH-FAIL", blob.stderr.decode("utf-8", "replace")[:200])
    sys.exit(2)
sha = hashlib.sha256(blob.stdout).hexdigest().upper()
state = open("state.json", "rb").read().decode("utf-8")
import json
st = json.loads(state)
prev = str(st.get("last_decisions_sha", "")).upper()
print("new_sha =", sha)
print("prev_sha =", prev)
print("MATCH-unchanged" if sha == prev else "CHANGED-new-decisions")
orders = sh(["git", "-C", D, "show", "origin/main:docs/orders.md"])
if orders.returncode == 0:
    txt = orders.stdout.decode("utf-8", "replace")
    lines = [ln for ln in txt.splitlines()
             if ("BigMoney" in ln or "bigmoney" in ln or "quant" in ln)
             and ln.strip().startswith(("-", "*", "["))]
    print("orders_md_bigmoney_lines:", len(lines))
    for ln in lines[-15:]:
        print("  |", ln.strip()[:160])
