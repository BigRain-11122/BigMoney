# -*- coding: utf-8 -*-
"""r407 bm-b: 16-UU rebase conflict resolve (vs bm-c r196 same-window S6 twins).

Canon per SKILL.md bigmoney-conflict-resolve + r406-addendum precedent:
take-NEW whole-doc for snapshot/idempotent-derive faces (mine newer on every
ts-bearing face: 03:49-03:53 vs bm-c 03:45); UNION zero-loss for rolling
ledgers (compute_audit history, regime_state history). Raw-byte take-new
preserves producer format exactly (R209 for the js wrapper).
"""
import json
import re
import subprocess
import io

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show :{stage}:{path} failed"
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8"))

def detect_indent(b):
    for ln in b.decode("utf-8").splitlines()[1:4]:
        m = re.match(r"^( +)\"", ln)
        if m:
            return len(m.group(1))
    return 1

TS_KEYS = ("ts", "generated", "updated", "generated_at", "asof", "date")

def ts_of(d):
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str):
            return v
    return ""

def take_new(path, stage_new=3, stage_old=2):
    b_new, b_old = blob(stage_new, path), blob(stage_old, path)
    try:
        tn, to = ts_of(jload(b_new)), ts_of(jload(b_old))
    except Exception:
        tn = to = ""
    if tn and to:
        assert tn >= to, f"{path}: new side ts {tn} < old {to} -- take-new direction violated"
    with io.open(path, "wb") as f:
        f.write(b_new)
    jload(open(path, "rb").read())  # parse validation
    return f"take-new(stage{stage_new}) ts {tn or 'n/a'} >= {to or 'n/a'}"

def union_ledger(path, list_key, base_stage=3, other_stage=2, row_id="ts"):
    b_base, b_other = blob(base_stage, path), blob(other_stage, path)
    base, other = jload(b_base), jload(b_other)
    lb, lo = base.get(list_key) or [], other.get(list_key) or []
    seen, union = set(), []
    for row in lb + lo:
        key = row.get(row_id) if isinstance(row, dict) else row
        if key in seen:
            continue
        seen.add(key)
        union.append(row)
    assert len(union) >= max(len(lb), len(lo)), f"{path}: union shrink"
    out = dict(base)
    out[list_key] = union
    indent = detect_indent(b_base)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    chk = jload(open(path, "rb").read())
    assert len(chk[list_key]) == len(union)
    return f"union {list_key}: {len(lb)}+{len(lo)} -> {len(union)} (zero-loss verified), state fields take-new stage{base_stage}"

report = []

# --- rolling ledgers: union zero-loss ---
report.append(("results/compute_audit.json", union_ledger("results/compute_audit.json", "history")))
report.append(("results/regime_state.json", union_ledger("results/regime_state.json", "history", row_id="asof")))

# --- snapshots: take-new whole doc (mine = newer ts on all probed faces) ---
for p in [
    "results/update_status.json",
    "results/token_usage.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/dashboard_status.json",
    "results/daily_scorecard.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.json",
]:
    report.append((p, take_new(p)))

# --- md twins follow their json twin's side (same producer run) ---
for p in [
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.md",
]:
    b = blob(3, p)
    with io.open(p, "wb") as f:
        f.write(b)
    report.append((p, "take-new(stage3) md twin of json face"))

# --- js wrapper snapshot (R209): raw bytes take-side, wrapper preserved ---
b3 = blob(3, "results/dashboard_status.js").decode("utf-8")
b2 = blob(2, "results/dashboard_status.js").decode("utf-8")
m3 = re.search(r"\"generated\"\s*:\s*\"([^\"]+)\"", b3)
m2 = re.search(r"\"generated\"\s*:\s*\"([^\"]+)\"", b2)
g3 = m3.group(1) if m3 else "?"
g2 = m2.group(1) if m2 else "?"
assert b3.startswith("window.DASH_DATA") or "DASH_DATA" in b3[:80], "js wrapper missing"
if g3 != "?" and g2 != "?":
    assert g3 >= g2, f"dashboard_status.js new gen {g3} < old {g2}"
with io.open("results/dashboard_status.js", "wb") as f:
    f.write(blob(3, "results/dashboard_status.js"))
report.append(("results/dashboard_status.js", f"take-new(stage3) wrapper preserved, generated {g3} >= {g2}"))

for path, note in report:
    print(f"RESOLVED {path}: {note}")
print(f"total resolved: {len(report)}")
