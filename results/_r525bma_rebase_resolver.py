"""r525 bm-a rebase conflict resolver (bm-b r513 same-window closeout collision).
Canon: bigmoney-conflict-resolve skill. Handles the non-ALL_FACES faces:
- CODELY.md memory-union (base-prefix identity assertion + direct-concat both suffixes)
- twin-regen families (REPORT-2026-10-01, LIVE-2026-10-01, LIVE-latest): json ts probe
  on STAGED blobs (:2: origin-side vs :3: replay-side), SAME side for all twins,
  md faces byte-copied from the chosen side's blob (r329: md is not JSON)
- snapshot faces (fundamental_b_layer_filter, _attrition_guard_scan): take-new by inner ts
Probes parse JSON from git show bytes (r500 law: never treat bytes as str for probing).
"""
import json
import subprocess
import sys

def blob(rev, path):
    return subprocess.check_output(["git", "show", f"{rev}{path}"])

def jparse(raw):
    return json.loads(raw.decode("utf-8"))

def deep_ts(obj, found):
    """Deep-scan for wall-clock ts values (r311 law: true ts lives in nested paths)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and ("ts" in kk or "generated" in kk or "updated" in kk):
                if len(v) >= 19 and v[:4] in ("2025", "2026") and ("T" in v[10:11+1] or v[10] in " "):
                    found.append(v)
            deep_ts(v, found)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, found)

def newest_ts(raw):
    found = []
    deep_ts(jparse(raw), found)
    found = [f.replace("T", " ")[:19] for f in found]
    return max(found) if found else ""

ok = True

# ---- 1) CODELY.md memory-union ----
path = "CODELY.md"
base = blob(":1:", path).decode("utf-8")
ours = blob(":2:", path).decode("utf-8")   # origin/bm-b side (landed first)
theirs = blob(":3:", path).decode("utf-8") # my replay side (later-comer)
assert ours.startswith(base), "CODELY.md origin-side is not pure-append (prefix identity FAIL)"
assert theirs.startswith(base), "CODELY.md replay-side is not pure-append (prefix identity FAIL)"
suf_ours = ours[len(base):]
suf_theirs = theirs[len(base):]
assert suf_ours.strip() and suf_theirs.strip(), "empty suffix side"
merged = base + suf_ours + suf_theirs
assert len(merged.encode("utf-8")) == len(base.encode("utf-8")) + len(suf_ours.encode("utf-8")) + len(suf_theirs.encode("utf-8")), "byte math FAIL"
open(path, "w", encoding="utf-8", newline="").write(merged)
print(f"[memory-union] CODELY.md: base {len(base.encode('utf-8'))}B + bm-b suffix {len(suf_ours.encode('utf-8'))}B + bma suffix {len(suf_theirs.encode('utf-8'))}B = {len(merged.encode('utf-8'))}B, zero-loss concat")

# ---- 2) twin families: probe json staged blobs, same side for all twins ----
FAMILIES = {
    "docs/daily_report/REPORT-2026-10-01": ["docs/daily_report/REPORT-2026-10-01.json", "docs/daily_report/REPORT-2026-10-01.md"],
    "docs/live_usage/LIVE-2026-10-01": ["docs/live_usage/LIVE-2026-10-01.json", "docs/live_usage/LIVE-2026-10-01.md"],
    "docs/live_usage/LIVE-latest": ["docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"],
}
for stem, twins in FAMILIES.items():
    jpath = stem + ".json"
    t2, t3 = newest_ts(blob(":2:", jpath)), newest_ts(blob(":3:", jpath))
    if not t2 and not t3:
        side = ":3:"  # both probes empty -> r500 law: sample adjudication; both faces same-day idempotent regen, replay-side = later wall clock by commit order
        note = "both-probes-empty -> commit-order (replay side)"
    else:
        side = ":2:" if t2 > t3 else ":3:"
        note = f"ts {t2 or '-'} vs {t3 or '-'}"
    for tw in twins:
        raw = blob(side, tw)
        open(tw, "wb").write(raw)
        if tw.endswith(".json"):
            jparse(raw)  # parse-verify
    print(f"[twin] {stem}: side {side} ({note}), all twins byte-copied same side")

# ---- 3) snapshot faces take-new ----
for snap in ["results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json"]:
    t2, t3 = newest_ts(blob(":2:", snap)), newest_ts(blob(":3:", snap))
    side = ":2:" if t2 >= t3 else ":3:"  # same-second tie -> HEAD/origin side (r140)
    raw = blob(side, snap)
    jparse(raw)
    open(snap, "wb").write(raw)
    print(f"[snapshot] {snap}: side {side} (ts {t2 or '-'} vs {t3 or '-'})")

print("RESOLVER DONE (parse-verified all json)")
