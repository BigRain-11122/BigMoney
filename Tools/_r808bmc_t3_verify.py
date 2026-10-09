# -*- coding: utf-8 -*-
"""r808 bm-c T3 verification (tech-queue J18b collector wall):
1) _collector_wall_state() real-data readout (17 rows, honest degradation);
2) full build() payload wiring assertion (data.collector_wall present + counts);
3) dashboard.html inline-script extraction -> node --check syntax gate (r807 T2
   verification canon)."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

from monitor import build_status as bs

wall = bs._collector_wall_state()
print("WALL:", json.dumps(wall["text"], ensure_ascii=False))
for r in wall["rows"]:
    print("  %-14s lane=%-4s status=%-4s age=%-6s cutoff=%-10s %s" % (
        r["id"], r["lane"], r["status"], r["age_min"], r["cutoff"], r["text"][:40]))
assert wall["present"] and wall["n_total"] == 18, "wall must carry 18 rows"
assert all(k in wall for k in ("n_ok", "n_warn", "n_bad", "n_none")), "count keys"

payload = bs.build()
cw = payload.get("data", {}).get("collector_wall")
assert cw and cw["n_total"] == 18 and cw["rows"], "payload wiring missing"
print("BUILD-OK collector_wall wired: n_ok=%s n_warn=%s n_bad=%s n_none=%s"
      % (cw["n_ok"], cw["n_warn"], cw["n_bad"], cw["n_none"]))

html = open(os.path.join(ROOT, "dashboard.html"), encoding="utf-8").read()
m = re.search(r"<script>(.*?)</script>", html, re.S)
assert m, "inline script block not found"
js_path = os.path.join(ROOT, "results", "_r808bmc_dash_script.js")
with open(js_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(m.group(1))
r = subprocess.run(["node", "--check", js_path], capture_output=True,
                   creationflags=CNW, timeout=60)
print("NODE-CHECK rc=%d %s" % (r.returncode,
      (r.stderr or b"").decode("utf-8", "replace")[:200]))
assert r.returncode == 0, "dashboard inline script syntax FAIL"
assert "collector_wall" in m.group(1), "render face not consuming wall"
print("T3-VERIFY ALL PASS")
