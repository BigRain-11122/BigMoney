"""r375 bm-a wave-2 probe: staged-blob dual probes vs bm-b r356 batch.

Rebase side law (r352): :2: == HEAD == upstream (bm-b 1bd8207a),
:3: == the replayed local commit (bm-a r375). Probes on STAGED blobs only.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def blob_json(spec):
    return json.loads(blob(spec))


def wall_ts(d):
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
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for f in SNAP:
    a = blob_json(":2:" + f)
    b = blob_json(":3:" + f)
    print(f, "| bmb:", wall_ts(a), "| bma:", wall_ts(b),
          "| snapshots:", a.get("snapshots"), "/", b.get("snapshots"))

js2, js3 = blob(":2:results/dashboard_status.js"), blob(":3:results/dashboard_status.js")


def jsts(s):
    m = re.search(r'"generated_at":\s*"([^"]+)"', s)
    return m.group(1) if m else "?"


print("dashboard_status.js | bmb:", jsts(js2), "| bma:", jsts(js3))

ca2, ca3 = blob_json(":2:results/compute_audit.json"), blob_json(":3:results/compute_audit.json")
print("compute_audit latest.ts | bmb:", ca2.get("latest", {}).get("ts"),
      "| bma:", ca3.get("latest", {}).get("ts"),
      "| hist:", len(ca2.get("history", [])), "/", len(ca3.get("history", [])))

rs2, rs3 = blob_json(":2:results/regime_state.json"), blob_json(":3:results/regime_state.json")
print("regime updated | bmb:", rs2.get("updated"), "| bma:", rs3.get("updated"))

au2, au3 = blob_json(":2:results/autofill_state.json"), blob_json(":3:results/autofill_state.json")
print("autofill last_tick.ts | bmb:", au2.get("last_tick", {}).get("ts"),
      "| bma:", au3.get("last_tick", {}).get("ts"),
      "| launches:", len(au2.get("launches", [])), "/",
      len(au3.get("launches", [])))
