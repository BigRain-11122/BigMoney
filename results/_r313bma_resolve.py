# -*- coding: utf-8 -*-
"""R313 bm-a push-collision batch resolver (rebase replay of 3788209f onto 7ce3e12e).
Canon: bigmoney-conflict-resolve SKILL.md (r188/R208/R209/R216/r312 laws).
Fail-closed: any undecidable face -> exit 2 with dump paths, no blind take-new.
"""
import json, os, re, subprocess, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob read fail %s stage %d: %s" % (path, stage, r.stderr.decode("utf-8", "replace")))
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8"))

def find_ts(d, depth=0):
    """Return (key, value-string) for the best timestamp-ish top-level key."""
    keys = ["updated_at", "generated_at", "generated", "ts", "asof", "as_of", "last_run", "run_ts", "date"]
    for k in keys:
        if isinstance(d, dict) and k in d and isinstance(d[k], str) and len(d[k]) >= 8:
            return k, d[k]
    return None, None

DUMP = os.path.join(os.environ.get("TEMP", "."), "_r313bma_conflict")
os.makedirs(DUMP, exist_ok=True)

UU = [
    "CODELY.md",
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "research/memory-archive/202609.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

report = {}
for p in UU:
    ours, theirs = blob(2, p), blob(3, p)
    entry = {"bytes_ours": len(ours), "bytes_theirs": len(theirs)}
    if p.endswith(".json"):
        try:
            do, dt = jload(ours), jload(theirs)
            ko, vo = find_ts(do)
            kt, vt = find_ts(dt)
            entry.update(ts_key=ko, ts_ours=vo, ts_theirs=vt,
                         keys_ours=sorted(do.keys())[:12] if isinstance(do, dict) else "list",
                         keys_theirs=sorted(dt.keys())[:12] if isinstance(dt, dict) else "list")
            if isinstance(do, dict) and "history" in do:
                entry["history_len"] = {"ours": len(do["history"]), "theirs": len(dt["history"])}
            if isinstance(do, dict) and "transitions" in do:
                entry["transitions_len"] = {"ours": len(do["transitions"]), "theirs": len(dt["transitions"])}
        except Exception as e:
            entry["json_error"] = repr(e)
    elif p.endswith("dashboard_status.js"):
        m = re.search(rb'"(generated|updated_at|ts)"\s*:\s*"([^"]+)"', ours)
        m2 = re.search(rb'"(generated|updated_at|ts)"\s*:\s*"([^"]+)"', theirs)
        entry.update(ts_ours=(m.group(2).decode() if m else None), ts_theirs=(m2.group(2).decode() if m2 else None))
    elif p.endswith(".md"):
        # find generated-ts line in both
        def md_ts(b):
            for mm in re.finditer(rb"(20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?)", b):
                return mm.group(1).decode()
            return None
        entry.update(md_ts_ours=md_ts(ours), md_ts_theirs=md_ts(theirs))
    # dump both sides for manual faces
    base = os.path.join(DUMP, p.replace("/", "__"))
    with open(base + ".ours", "wb") as f: f.write(ours)
    with open(base + ".theirs", "wb") as f: f.write(theirs)
    report[p] = entry

print(json.dumps(report, ensure_ascii=False, indent=1))
print("DUMP DIR:", DUMP)
