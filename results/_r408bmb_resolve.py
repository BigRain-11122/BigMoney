# -*- coding: utf-8 -*-
"""r408 bm-b: 28-UU rebase conflict resolve (vs bm-c r197 same-window S6 twins).

Canon per SKILL.md bigmoney-conflict-resolve + r404-corrected direction law
(pit-law 75: take-NEW = whichever STAGE's ts is newer; rebase stage semantics
INVERT -- stage2=base(bm-c r197), stage3=replayed(mine r408); NEVER assume a
fixed stage direction) + hardened deep-ts probe (r100/R350: value-shape gate
only, wall-clock values require time-of-day, no key-EXCLUDE lists, probe the
STAGED blobs never the working tree).
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

WALLCLOCK = re.compile(r"^20\d{2}-")  # value-shape gate

def deep_ts(obj):
    """Hardened deep-scan: collect ALL wall-clock string values with time-of-day
    anywhere in the tree; return the lexicographic max (or '' if none).
    Value-shape adjudication only (R350: no key exclusion lists)."""
    best = ""
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            if WALLCLOCK.match(o) and re.search(r"[T ]\d{2}:\d{2}", o):
                if o > best:
                    best = o
    walk(obj)
    return best

def probe_pair(path):
    """Return (t2, t3) = deep max-ts of stage2 and stage3 staged blobs."""
    t2 = deep_ts(jload(blob(2, path)))
    t3 = deep_ts(jload(blob(3, path)))
    return t2, t3

def winner_stage(path):
    """Direction-agnostic take-NEW: newer stage wins; tie -> stage2 (HEAD, r140)."""
    t2, t3 = probe_pair(path)
    if t3 > t2:
        return 3, t2, t3
    return 2, t2, t3  # tie or stage2 newer

def take_new(path):
    st, t2, t3 = winner_stage(path)
    b = blob(st, path)
    with io.open(path, "wb") as f:
        f.write(b)
    jload(open(path, "rb").read())  # parse validation before add (r185)
    side = "mine(r408)" if st == 3 else "bm-c-r197-base"
    return f"take-NEW stage{st} ({side}) ts2={t2 or 'n/a'} ts3={t3 or 'n/a'}"

def take_twin_pair(json_path, md_path):
    """Twins MUST take the SAME side: probe json once, apply to both."""
    st, t2, t3 = winner_stage(json_path)
    for p in (json_path, md_path):
        b = blob(st, p)
        with io.open(p, "wb") as f:
            f.write(b)
        if p.endswith(".json"):
            jload(open(p, "rb").read())
    side = "mine(r408)" if st == 3 else "bm-c-r197-base"
    return f"take-NEW stage{st} ({side}) BOTH twins, ts2={t2 or 'n/a'} ts3={t3 or 'n/a'}"

def union_ledger(path, list_key, row_id="ts"):
    """Union zero-loss on ledger key; state fields take-NEW by deep-ts probe."""
    b2, b3 = blob(2, path), blob(3, path)
    d2, d3 = jload(b2), jload(b3)
    l2, l3 = d2.get(list_key) or [], d3.get(list_key) or []
    seen, union = set(), []
    for row in l2 + l3:
        key = row.get(row_id) if isinstance(row, dict) else row
        if key in seen:
            continue
        seen.add(key)
        union.append(row)
    assert len(union) >= max(len(l2), len(l3)), f"{path}: union shrink"
    t2, t3 = deep_ts(d2), deep_ts(d3)
    base_doc = d3 if t3 >= t2 else d2  # state fields take-new
    out = dict(base_doc)
    out[list_key] = union
    indent = detect_indent(b3 if t3 >= t2 else b2)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    chk = jload(open(path, "rb").read())
    assert len(chk[list_key]) == len(union)
    return f"union {list_key}: {len(l2)}+{len(l3)} -> {len(union)} (zero-loss), state take-NEW (ts2={t2} ts3={t3})"

def union_lines(path):
    """jsonl line-level superset union zero-loss (append-only log).
    Both sides are same-origin rolling logs (forked by machine-local appends):
    keep stage2 (base) verbatim incl. its intra-side multiplicity, then append
    every stage3 line whose string is not present in stage2. Every line from
    either side survives (superset); zero-loss check via set equality."""
    b2, b3 = blob(2, path), blob(3, path)
    l2 = [x for x in b2.decode("utf-8").splitlines() if x.strip()]
    l3 = [x for x in b3.decode("utf-8").splitlines() if x.strip()]
    s2 = set(l2)
    out = list(l2) + [ln for ln in l3 if ln not in s2]
    assert set(out) == (set(l2) | set(l3)), f"{path}: superset zero-loss violated"
    assert out[:len(l2)] == l2, f"{path}: stage2 verbatim prefix violated"
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        for ln in out:
            f.write(ln + "\n")
    for ln in out[-6:]:
        json.loads(ln)  # spot parse validation on appended region
    return f"superset line-union: l2={len(l2)} verbatim + l3-new={len(out)-len(l2)} -> {len(out)} (set zero-loss verified)"

def resolve_js_wrapper(path):
    """R209: take-side whole bytes by generated ts; wrapper preserved verbatim."""
    b2, b3 = blob(2, path), blob(3, path)
    g2 = re.search(r"\"generated\"\s*:\s*\"([^\"]+)\"", b2.decode("utf-8"))
    g3 = re.search(r"\"generated\"\s*:\s*\"([^\"]+)\"", b3.decode("utf-8"))
    t2 = g2.group(1) if g2 else ""
    t3 = g3.group(1) if g3 else ""
    st = 3 if t3 > t2 else 2
    b = blob(st, path)
    assert b"DASH_DATA" in b[:80], "js wrapper missing"
    with io.open(path, "wb") as f:
        f.write(b)
    side = "mine(r408)" if st == 3 else "bm-c-r197-base"
    return f"take-NEW stage{st} ({side}) wrapper preserved, generated {t2 or '?'} vs {t3 or '?'}"

report = []

# --- rolling ledgers: union zero-loss + state take-new ---
report.append(("results/compute_audit.json", union_ledger("results/compute_audit.json", "history")))
report.append(("results/regime_state.json", union_ledger("results/regime_state.json", "history", row_id="asof")))

# --- append-log: line union ---
report.append(("results/x2_watch_log.jsonl", union_lines("results/x2_watch_log.jsonl")))

# --- twins: probe json once, both take same side ---
report.append(("docs/daily_report/REPORT-2026-09-29.{json,md}", take_twin_pair(
    "docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md")))
report.append(("docs/live_usage/LIVE-2026-09-29.{json,md}", take_twin_pair(
    "docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md")))

# --- js wrapper snapshot (R209) ---
report.append(("results/dashboard_status.js", resolve_js_wrapper("results/dashboard_status.js")))

# --- snapshots: direction-agnostic take-NEW via hardened deep-ts probe ---
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
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]:
    report.append((p, take_new(p)))

for path, note in report:
    print(f"RESOLVED {path}: {note}")
print(f"total resolved: {len(report)} faces")
