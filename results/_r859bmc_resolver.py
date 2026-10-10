# -*- coding: utf-8 -*-
# r859 bm-c rebase race resolver: 14 shared faces, ts-audit = mine-newer all seats
# (r856 precedent family: plain faces newest-embedded-ts side + compute_audit UNION)
import json, io, subprocess, sys

PLAIN = [
    "docs/daily_report/REPORT-2026-10-11.json",
    "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for f in PLAIN:
    r = subprocess.run(["git", "checkout", "--theirs", "--", f], capture_output=True, text=True)
    assert r.returncode == 0, (f, r.stderr)

# compute_audit.json UNION (r856 law): mine-newer latest + history union both sides
CA = "results/compute_audit.json"
subprocess.run(["git", "checkout", "--theirs", "--", CA], capture_output=True)
mine = json.load(io.open(CA, "r", encoding="utf-8"))
theirs_blob = subprocess.run(["git", "show", "origin/main:" + CA],
                              capture_output=True).stdout.decode("utf-8")
theirs = json.loads(theirs_blob)
seen, hist = set(), []
for row in list(mine.get("history", [])) + list(theirs.get("history", [])):
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key in seen:
        continue
    seen.add(key)
    hist.append(row)
hist.sort(key=lambda r: r.get("ts", ""))
union = {"latest": (mine["latest"] if str(mine["latest"].get("ts", "")) >=
                    str(theirs["latest"].get("ts", "")) else theirs["latest"]),
         "history": hist}
assert len(hist) == 202, ("union history size", len(hist))
assert union["latest"]["ts"] == mine["latest"]["ts"], "latest side drift"
io.open(CA, "w", encoding="utf-8", newline="").write(
    json.dumps(union, ensure_ascii=False, indent=1) + "\n")
print("RESOLVED: 13 plain mine-newer + compute_audit UNION history=%d latest=%s (mine)"
      % (len(hist), union["latest"]["ts"]))
