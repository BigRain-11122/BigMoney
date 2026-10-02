# r402 probe: D-19 decisions SHA (group repo, bytes-space per state method note) + watermark red face
import hashlib
import json
import subprocess

b = subprocess.check_output(
    ["git", "-C", "K:/Fluxgroup/FluxGroup", "show", "origin/main:docs/decisions.md"])
print("decisions_sha256 =", hashlib.sha256(b).hexdigest().upper())
prev = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/state-bm-c.json"))
print("state_last_sha  =", prev["last_decisions_sha"])
print("SHA_MATCH =", hashlib.sha256(b).hexdigest().upper() == prev["last_decisions_sha"])
w = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/results/watermark_red.json"))
print("watermark red =", w.get("red"), "| reason =", w.get("reason", ""),
      "| next_pick =", str(w.get("next_pick"))[:160])
