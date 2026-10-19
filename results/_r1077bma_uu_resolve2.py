"""r1077 bm-a UU resolver #2 (rebase step-2 replay, dual-S6-write family, r965 recipe):
- REPORT-2026-10-19.json/.md : daily twins -> take newer generated_at side (mine 10:49:19), md same-side
- compute_audit.json        : history union dedupe + latest newer-wins
- regime_state.json         : latest-take-newer (updated field), history union
- token_usage.json          : per-machine union newer-wins + generated max
- update_status.json        : newer updated side (mine)
- _attrition_guard_scan.json: newer ts side (mine)
- fundamental_b_layer_filter.json: newer updated side (mine)
Rebase semantics: ours=HEAD(origin/bm-c), theirs=my commit being replayed.
"""
import json
import re
import subprocess
import sys

MINE = "7ec8eaafc6"  # my r1077 commit being replayed


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    return r.stdout


def jload(rev, path):
    try:
        return json.loads(blob(rev, path))
    except Exception:
        return None


def write(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    json.load(open(path, encoding="utf-8"))
    print("resolved", path)


bad = 0

# 1) daily report twins: take newer generated_at
o = jload("HEAD", "docs/daily_report/REPORT-2026-10-19.json")
m = jload(MINE, "docs/daily_report/REPORT-2026-10-19.json")
side = m if (m or {}).get("generated_at", "") >= (o or {}).get("generated_at", "") else o
print("report side generated_at:", side.get("generated_at"))
write("docs/daily_report/REPORT-2026-10-19.json", side)
for rev in ("HEAD", MINE):
    pass
# md twin: same side as json decision
md_side_rev = MINE if side is m else "HEAD"
r = subprocess.run(["git", "show", f"{md_side_rev}:docs/daily_report/REPORT-2026-10-19.md"], capture_output=True)
open("docs/daily_report/REPORT-2026-10-19.md", "wb").write(r.stdout)
txt = open("docs/daily_report/REPORT-2026-10-19.md", encoding="utf-8").read()
assert ">>>>>>>" not in txt and "<<<<<<<" not in txt
print("resolved docs/daily_report/REPORT-2026-10-19.md (side", md_side_rev[:8], ")")

# 2) compute_audit: history union + latest newer-wins
o = jload("HEAD", "results/compute_audit.json")
m = jload(MINE, "results/compute_audit.json")
hist = {json.dumps(h, sort_keys=True, ensure_ascii=False): h for h in o.get("history", [])}
for h in m.get("history", []):
    hist.setdefault(json.dumps(h, sort_keys=True, ensure_ascii=False), h)
merged_hist = sorted(hist.values(), key=lambda h: str(h.get("ts", h.get("time", ""))))
latest = m.get("latest") if str(m.get("latest", {}).get("ts", "")) >= str(o.get("latest", {}).get("ts", "")) else o.get("latest")
merged = {"latest": latest, "history": merged_hist}
write("results/compute_audit.json", merged)

# 3) regime_state: latest-take-newer + history union
o = jload("HEAD", "results/regime_state.json")
m = jload(MINE, "results/regime_state.json")
newer = m if str(m.get("updated", "")) >= str(o.get("updated", "")) else o
oh = {json.dumps(h, sort_keys=True, ensure_ascii=False): h for h in o.get("history", [])}
for h in m.get("history", []):
    oh.setdefault(json.dumps(h, sort_keys=True, ensure_ascii=False), h)
newer = dict(newer)
newer["history"] = sorted(oh.values(), key=lambda h: str(h.get("asof", h.get("ts", ""))))
write("results/regime_state.json", newer)

# 4) token_usage: per-machine union newer-wins + generated max
o = jload("HEAD", "results/token_usage.json")
m = jload(MINE, "results/token_usage.json")
machines = {}
for src in (o, m):
    for k, v in (src.get("machines") or {}).items():
        machines[k] = v  # later dict (mine) wins on equal keys; both are per-machine snapshots
out = dict(m)
out["machines"] = machines
out["generated"] = max(str(o.get("generated", "")), str(m.get("generated", "")))
write("results/token_usage.json", out)

# 5) update_status: newer updated
o = jload("HEAD", "results/update_status.json")
m = jload(MINE, "results/update_status.json")
write("results/update_status.json", m if str(m.get("updated", "")) >= str(o.get("updated", "")) else o)

# 6) attrition guard scan: newer ts
o = jload("HEAD", "results/_attrition_guard_scan.json")
m = jload(MINE, "results/_attrition_guard_scan.json")
write("results/_attrition_guard_scan.json", m if str(m.get("ts", "")) >= str(o.get("ts", "")) else o)

# 7) b_layer_filter: newer updated
o = jload("HEAD", "results/fundamental_b_layer_filter.json")
m = jload(MINE, "results/fundamental_b_layer_filter.json")
write("results/fundamental_b_layer_filter.json", m if str(m.get("updated", "")) >= str(o.get("updated", "")) else o)

# stage all
files = [
    "docs/daily_report/REPORT-2026-10-19.json",
    "docs/daily_report/REPORT-2026-10-19.md",
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
]
for p in files:
    r = subprocess.run(["git", "add", "--", p], capture_output=True, text=True)
    if r.returncode != 0:
        print("ADD-FAIL", p, r.stderr[:200])
        bad += 1
print("STAGED-OK" if bad == 0 else f"BAD={bad}")
sys.exit(1 if bad else 0)
