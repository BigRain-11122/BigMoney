# r524 bm-a: D-19 group decisions watermark check (r481 temp partial-clone
# recipe -- bm-a has no K: group tree; raw-blob sha256, upper-normalized
# compare per r503 law).
import hashlib
import json
import os
import subprocess
import sys

TMP = os.path.join(os.environ["TEMP"], "fg-dec-bma")
REPO = "git@github.com:BigRain-11122/FluxGroup.git"

if not os.path.isdir(os.path.join(TMP, ".git")):
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                    "--no-checkout", REPO, TMP], check=True,
                   capture_output=True)
subprocess.run(["git", "-C", TMP, "fetch", "origin"], check=True,
               capture_output=True)
raw = subprocess.check_output(
    ["git", "-C", TMP, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(raw).hexdigest().upper()

st_path = os.path.join("state-bm-a.json")
st = json.load(open(st_path, encoding="utf-8"))
prev = (st.get("last_decisions_sha") or "").upper()

print("group decisions blob sha256:", sha)
print("state watermark          :", prev)
if sha == prev:
    print("MATCH-unchanged: zero action (decisions)")
    sys.exit(0)
print("CHANGED: consuming dispatch-board rows + new decision lines")
# show the doc for the consuming step (stdout, next command parses it)
sys.stdout.write(raw.decode("utf-8", errors="replace"))
