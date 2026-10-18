# -*- coding: utf-8 -*-
"""r1056 rebase UU resolver: runtime shared probe faces, newer-wins (r1028/r1049/r1051 recipe).

UU faces = both machines regenerated the same deterministic probe face in the same window.
Resolution law: compare embedded ts (ts/updated/generated/now keys, ISO or space format);
newer side wins. Text snapshot (.md) = longer side wins (superset probe). Unparseable ->
origin (HEAD) side. Logs the pick per face for the round report.
"""
import json
import re
import subprocess
import sys

UU = [
    "docs/daily_report/REPORT-2026-10-18.json",
    "docs/daily_report/REPORT-2026-10-18.md",
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/_r686bmb_orders_fresh.md",
    "results/compute_audit.json",
    "results/d19_watermark.json",
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/watermark_red.json",
]

TS_RE = re.compile(r'"(?:ts|updated|generated|now|updated_at)"\s*:\s*"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})')


def stage_text(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def best_ts(text):
    hits = TS_RE.findall(text)
    if not hits:
        return None
    return max(f"{d} {t}" for d, t in hits)


picks = []
for p in UU:
    ours = stage_text(2, p)   # origin/HEAD side
    theirs = stage_text(3, p)  # my commit side
    to, tt = best_ts(ours), best_ts(theirs)
    if to and tt:
        side = "theirs" if tt > to else "ours"
        why = f"ts {to} vs {tt}"
    elif p.endswith(".md"):
        side = "theirs" if theirs.count("\n") > ours.count("\n") else "ours"
        why = f"lines {ours.count(chr(10))} vs {theirs.count(chr(10))}"
    else:
        side = "ours"
        why = "unparseable->origin"
    flag = "--theirs" if side == "theirs" else "--ours"
    subprocess.run(["git", "checkout", flag, p], check=True)
    subprocess.run(["git", "add", p], check=True)
    picks.append(f"{p}: {side} ({why})")

print("\n".join(picks))
bad = []
for p in UU:
    body = open(p, encoding="utf-8", errors="replace").read()
    if "<<<<<<< HEAD" in body or ">>>>>>> " in body:
        bad.append(p)
if bad:
    print("MARKER RESIDUE:", bad)
    sys.exit(1)
try:
    for p in UU:
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8").read())
except Exception as e:
    print("JSON VALIDATION FAIL:", e)
    sys.exit(1)
print("RESOLVE-OK all faces marker-free and json-valid")
