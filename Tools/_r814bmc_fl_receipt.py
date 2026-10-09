# -*- coding: utf-8 -*-
"""r814 bm-c FleetLink v1.2 live receipt: /health + /status on port 8790,
version gate (MUST be 1.2 -- O-20261009-1755 bm-c install evidence),
receipt -> results/_r814bmc_fleetlink_receipt.json. Read-only HTTP probes."""
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PORT = 8790
receipt = {"order": "O-20261009-1755", "machine": "bm-c",
           "ts": datetime.now(timezone(timedelta(hours=8))).isoformat()}


def probe(path):
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d%s" % (PORT, path), timeout=5) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as ex:
        return 0, str(ex)[:200]


ok = False
for i in range(20):
    st, body = probe("/health")
    try:
        h = json.loads(body)
    except Exception:
        h = {}
    if isinstance(h, dict) and h.get("ok"):
        receipt["health"] = h
        ok = True
        break
    time.sleep(3)
st2, body2 = probe("/status")
receipt["health_rc"] = st
receipt["status_rc"] = st2
ver = str((receipt.get("health") or {}).get("version", ""))
receipt["version_seen"] = ver
receipt["version_gate_1_2"] = ver in ("1.2", "1.2.0", "v1.2")
receipt["status_body_head"] = body2[:300]
with open(R + r"\results\_r814bmc_fleetlink_receipt.json", "w",
          encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("fleetlink receipt: health_ok=%s version=%s gate=%s status_rc=%s"
      % (ok, ver, receipt["version_gate_1_2"], st2))
raise SystemExit(0 if (ok and receipt["version_gate_1_2"]) else 2)
