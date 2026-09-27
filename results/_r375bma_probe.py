"""r375 bm-a push-storm probe: staged-blob dual probes for the 15-UU batch.

Rebase window side law (r352): :2: == HEAD == upstream (bm-c r127 batch),
:3: == the replayed local commit (bm-a r375). Side-assert verified above.
Probes read STAGED BLOBS only (R350), never the working tree.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def wall_ts(d):
    """Hardened wall-clock probe (r100/R350): key-name normalized prefix
    match, value must be ^20xx- AND carry time-of-day; no key-excludes."""
    best = ""

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                kk = k.replace("_", "").replace("-", "").lower()
                if isinstance(v, str) and re.match(r"^20\d{2}-", v) \
                        and re.search(r"[ T]\d{2}:\d{2}", v):
                    if (kk.startswith(("generated", "updated"))
                            or kk in ("ts", "asof", "lastwrite")):
                        best = max(best, v)
                walk(v)
        elif isinstance(x, list):
            for it in x:
                walk(it)

    walk(d)
    return best


SNAP = [
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-09-28.json",
]
for f in SNAP:
    a = json.loads(blob(":2:" + f))
    b = json.loads(blob(":3:" + f))
    print(f, "| bmc:", wall_ts(a), "| bma:", wall_ts(b))

js2 = blob(":2:results/dashboard_status.js")
js3 = blob(":3:results/dashboard_status.js")


def jsts(s):
    m = re.search(r'"generated_at":\s*"([^"]+)"', s)
    return m.group(1) if m else "?"


print("dashboard_status.js | bmc:", jsts(js2), "| bma:", jsts(js3))

ca2 = json.loads(blob(":2:results/compute_audit.json"))
ca3 = json.loads(blob(":3:results/compute_audit.json"))
print("compute_audit latest.ts | bmc:", ca2.get("latest", {}).get("ts"),
      "| bma:", ca3.get("latest", {}).get("ts"),
      "| hist rows:", len(ca2.get("history", [])), "/",
      len(ca3.get("history", [])))

rs2 = json.loads(blob(":2:results/regime_state.json"))
rs3 = json.loads(blob(":3:results/regime_state.json"))
print("regime updated | bmc:", rs2.get("updated"), "| bma:", rs3.get("updated"))

au2 = json.loads(blob(":2:results/autofill_state.json"))
au3 = json.loads(blob(":3:results/autofill_state.json"))
print("autofill last_tick.ts | bmc:", au2.get("last_tick", {}).get("ts"),
      "| bma:", au3.get("last_tick", {}).get("ts"),
      "| launches:", len(au2.get("launches", [])), "/",
      len(au3.get("launches", [])))
