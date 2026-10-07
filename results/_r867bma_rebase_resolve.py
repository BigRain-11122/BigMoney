# -*- coding: utf-8 -*-
"""r867 bm-a rebase-close resolver: 14 UU shared regen faces.
Law: r440 (regenerable shared faces deep-ts take-new) + r866/r738 (md twins
take-local-by-generated_at using the face OWN ts key -- ISO T-strings sort
above space-separated ts, so probe each face's own key format) + r327/r329
(md/json twins byte-coupled: both faces resolve to the SAME side).
Zero-loss check: every picked side logged; conflict markers scanned."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FILES = [
    "docs/daily_report/REPORT-2026-10-08.json", "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json", "docs/live_usage/LIVE-2026-10-08.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/regime_state.json",
    "results/token_usage.json", "results/update_status.json",
]


def side(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def ts_of(path, text):
    # probe the face OWN key (r866 law: ISO T vs space-separated -- regex both)
    m = re.search(r'"(?:ts|generated_at|generated)"\s*:\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    m = re.search(r'"(?:ts|generated_at|generated)"\s*:\s*([0-9.]+)', text)
    if m:
        return m.group(1)
    m = re.search(r'- (?:generated|ts)[：:]\s*([0-9T:.\-+ ]+)', text)
    if m:
        return m.group(1).strip()
    return ""


def pick(path):
    ours, theirs = side(2, path), side(3, path)
    assert ours is not None and theirs is not None, path
    # marker scan safety
    for name, t in (("ours", ours), ("theirs", theirs)):
        assert "<<<<<<<" not in t and ">>>>>>>" not in t, (path, name, "markers inside stage side")
    to, tt = ts_of(path, ours), ts_of(path, theirs)
    # byte-identical fast path
    if ours == theirs:
        return "identical", ours
    take_ours = to >= tt  # tie -> ours (our S6 chain, r866 precedent)
    return ("ours" if take_ours else "theirs"), (ours if take_ours else theirs)


TWIN_MAP = {
    "docs/daily_report/REPORT-2026-10-08.md": "docs/daily_report/REPORT-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md": "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

resolved = {}
for p in FILES:
    verdict, content = pick(p)
    resolved[p] = (verdict, content)
    print(p, "->", verdict, "| ts ours/theirs:", ts_of(p, side(2, p) or ""), "/", ts_of(p, side(3, p) or ""))

# twin coupling: force the .json to the SAME side as its .md (r327/r329)
for md, js in TWIN_MAP.items():
    v_md, c_md = resolved[md]
    v_js, c_js = resolved[js]
    if v_md != v_js:
        forced = side(2, js) if v_md == "ours" else side(3, js)
        resolved[js] = (v_md, forced)
        print("TWIN COUPLE: %s forced to %s (follows %s)" % (js, v_md, md))

for p, (verdict, content) in resolved.items():
    io.open(p, "wb").write(content.encode("utf-8"))

# verify: no markers anywhere, all parse where json
for p, (verdict, content) in resolved.items():
    assert "<<<<<<<" not in content and ">>>>>>>" not in content, p
    if p.endswith(".json"):
        json.loads(content)  # parse gate
print("RESOLVER DONE: 14 faces, twins coupled, markers zero, json parse OK")
