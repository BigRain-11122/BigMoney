"""D-19 fresh-read check (bm-a recipe: temp partial clone, raw-bytes sha256 per r292 law)."""
import hashlib
import os
import subprocess
import sys

TMP = os.path.join(os.environ.get("TEMP", "."), "fg-dec-bma")
REPO = "git@github.com:BigRain-11122/FluxGroup.git"
LAST_SHA = "ED4E0EABF941B4299A6F26B243082EE74A83517B462D352D9C047F95A49A1F07"

if not os.path.isdir(os.path.join(TMP, ".git")):
    subprocess.check_call(["git", "clone", "--depth", "1", "--filter=blob:none",
                           "--no-checkout", REPO, TMP], stdout=subprocess.DEVNULL)
else:
    subprocess.check_call(["git", "-C", TMP, "fetch", "origin"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

dec = subprocess.check_output(["git", "-C", TMP, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(dec).hexdigest().upper()
print("decisions_sha:", sha)
print("state_watermark:", LAST_SHA)
print("MATCH" if sha == LAST_SHA else "CHANGED -- consume dispatch board + new decision lines")

orders = subprocess.check_output(["git", "-C", TMP, "show", "origin/main:docs/orders.md"])
o_sha = hashlib.sha256(orders).hexdigest().upper()
print("orders_sha:", o_sha)
# print tail of dispatch board lines mentioning bigmoney/quant if changed
text = orders.decode("utf-8", "replace")
lines = text.splitlines()
idx = None
for i, l in enumerate(lines):
    if "派工通告板" in l:
        idx = i
if idx is not None:
    tail = "\n".join(lines[idx:idx + 40])
    hits = [l for l in tail.splitlines() if ("BigMoney" in l or "quant" in l or "bm-" in l)]
    print("dispatch_board_bigmoney_lines:", hits if hits else "none-in-first-40")
