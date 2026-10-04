# -*- coding: utf-8 -*-
"""r680 bm-a merge resolver: 7 UU faces (CODELY block-union + 6 regen twins ts-freshness).
Laws: r675 CODELY block-append recipe (origin full text + incremental append, dedup on
increment only, origin-structure-not-reduced assertion); r662 take-new ts_norm compare;
t35 twin already resolved (ours 14:14:43). MERGE_HEAD in place (not yet committed)."""
import json
import re
import subprocess
import sys

def side_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_norm(s):
    if not s:
        return ""
    return str(s).replace("T", " ")[:19]

def find_ts(obj):
    """Best-effort freshness key from a JSON regen face."""
    if not isinstance(obj, dict):
        return ""
    for k in ("ts", "generated", "generated_at", "asof", "updated", "cutoff"):
        if k in obj and obj[k]:
            return ts_norm(obj[k])
    return ""

REGEN_FACES = [
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]

report = {}

# --- 1) CODELY.md block-union ---
path = "CODELY.md"
ours = side_bytes("HEAD", path).decode("utf-8")
theirs = side_bytes("MERGE_HEAD", path).decode("utf-8")
if not ours.endswith("\n"):
    ours += "\n"
if not theirs.endswith("\n"):
    theirs += "\n"
# incremental = lines in ours not present in theirs (exact-line, keep order)
ours_lines = ours.splitlines(keepends=True)
theirs_set = set(theirs.splitlines(keepends=True))
increment = [l for l in ours_lines if l not in theirs_set]
merged = theirs + "".join(increment)
# assertions per r675 recipe
assert merged.startswith(theirs[:200]), "origin prefix not preserved"
orig_n = len(theirs.splitlines())
merged_n = len(merged.splitlines())
assert merged_n >= orig_n, f"origin structure shrank {orig_n}->{merged_n}"
for probe in ("r680 bm-a", "lhb_detail 列位陷阱", "块缓冲 stdout"):
    assert probe in merged, f"my entry missing: {probe}"
    assert merged.count(probe) >= 1
# dedup check: no exact duplicate line introduced by increment that already in theirs
dup = [l for l in increment if l.strip() and theirs.count(l) > 0]
assert not dup, f"duplicate increment lines: {dup[:2]}"
open(path, "w", encoding="utf-8", newline="").write(merged)
report[path] = {"resolution": "block-union origin+increment",
                "origin_lines": orig_n, "merged_lines": merged_n,
                "increment_lines": len(increment)}

# --- 2) regen twins: ts-freshness ---
for path in REGEN_FACES:
    ob, tb = side_bytes("HEAD", path), side_bytes("MERGE_HEAD", path)
    if ob is None or tb is None:
        report[path] = {"resolution": "side-missing", "ours": ob is not None, "theirs": tb is not None}
        continue
    if path.endswith(".js"):
        # js regen: extract ts via regex
        m1 = re.search(r'generated["\']?\s*[:=]\s*["\']([^"\']+)', ob.decode("utf-8", "replace"))
        m2 = re.search(r'generated["\']?\s*[:=]\s*["\']([^"\']+)', tb.decode("utf-8", "replace"))
        t1, t2 = ts_norm(m1.group(1) if m1 else ""), ts_norm(m2.group(1) if m2 else "")
        pick = "ours" if (not t2) or (t1 and t1 >= t2) else "theirs"
        content = ob if pick == "ours" else tb
        # marker safety: chosen side must contain no conflict markers
        assert b"<<<<<<<" not in content, f"{path} chosen side has markers"
        open(path, "wb").write(content)
        report[path] = {"resolution": f"ts-freshness {pick}", "ours_ts": t1, "theirs_ts": t2}
        continue
    try:
        o = json.loads(ob.decode("utf-8", "replace"))
        t = json.loads(tb.decode("utf-8", "replace"))
    except Exception as ex:
        report[path] = {"resolution": "parse-fail-ours-fallback", "err": str(ex)[:80]}
        open(path, "wb").write(ob)
        continue
    t1, t2 = find_ts(o), find_ts(t)
    if t1 and t2:
        pick = "ours" if ts_norm(t1) >= ts_norm(t2) else "theirs"
    else:
        pick = "ours"  # host=bm-a faces per r378; ours regenerated 14:1x post-S6
    content = ob if pick == "ours" else tb
    assert b"<<<<<<<" not in content, f"{path} chosen side has markers"
    open(path, "wb").write(content)
    report[path] = {"resolution": f"ts-freshness {pick}", "ours_ts": t1, "theirs_ts": t2}

print(json.dumps(report, ensure_ascii=False, indent=1))
