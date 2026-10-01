import hashlib
import json
import os
import subprocess
import sys

TMP = os.path.join(os.environ.get("TEMP", r"C:\Users\Administrator\AppData\Local\Temp"),
                   "fg-dec-bmb")
URL = "git@github.com:BigRain-11122/FluxGroup.git"


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd} rc={r.returncode}: {r.stderr[:300]}")
    return r


if not os.path.isdir(os.path.join(TMP, ".git")):
    run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout",
         URL, TMP])
run(["git", "fetch", "origin"], cwd=TMP)

blob = run(["git", "show", "origin/main:docs/decisions.md"], cwd=TMP).stdout
sha = hashlib.sha256(blob).hexdigest().upper()

state_path = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json"
with open(state_path, encoding="utf-8") as f:
    state = json.load(f)
prev = (state.get("last_decisions_sha") or "").upper()

print("remote decisions sha:", sha)
print("state watermark sha :", prev)
if sha == prev:
    print("VERDICT: MATCH-unchanged (zero action)")
else:
    print("VERDICT: CHANGED — consuming new decision rows")
    text = blob.decode("utf-8", errors="replace")
    lines = text.splitlines()
    print("total lines:", len(lines))
    print("--- tail 60 lines ---")
    for ln in lines[-60:]:
        print(ln)
