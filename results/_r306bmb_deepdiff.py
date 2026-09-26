# -*- coding: utf-8 -*-
"""r306 bm-b: deep-diff stage2(bm-a base) vs stage3(bm-b r305) for all UU files.
Read-only. Prints differing JSON paths (capped). For RAW files: line diff."""
import subprocess, json

UU_ALL = [
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/x2_watch_log.jsonl",
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None

META_PATHS = ("generated", "generated_at", "ts", "elapsed_sec", "updated_at", "now_iso",
              "heartbeat_epoch_utc", "last_seen", "clock_read")

def walk(a, b, path, out, depth=0):
    if depth > 8:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((path + [k], "ONLY-B(theirs)", None))
            elif k not in b:
                out.append((path + [k], "ONLY-A(ours)", None))
            else:
                walk(a[k], b[k], path + [k], out, depth + 1)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, "LEN %d vs %d" % (len(a), len(b)), None))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + [i], out, depth + 1)
    else:
        if a != b:
            out.append((path, repr(a)[:70], repr(b)[:70]))

for p in UU_ALL:
    s2, s3 = blob(2, p), blob(3, p)
    print("=" * 10, p)
    if s2 is None or s3 is None:
        print("  MISSING STAGE BLOB s2=%s s3=%s" % (s2 is not None, s3 is not None))
        continue
    if p.endswith((".md", ".js", ".jsonl")) or p.endswith("dashboard_status.js"):
        l2, l3 = s2.decode("utf-8", "replace").splitlines(), s3.decode("utf-8", "replace").splitlines()
        if l2 == l3:
            print("  IDENTICAL")
        else:
            import difflib
            dl = [d for d in difflib.unified_diff(l2, l3, lineterm="", n=0)]
            print("  %d diff lines (showing up to 20):" % len(dl))
            for d in dl[:20]:
                print("   ", d[:150])
        continue
    try:
        j2, j3 = json.loads(s2.decode("utf-8")), json.loads(s3.decode("utf-8"))
    except Exception as e:
        print("  JSON-PARSE-FAIL", repr(e))
        continue
    out = []
    walk(j2, j3, [], out)
    if not out:
        print("  IDENTICAL")
        continue
    meta_only = True
    for path, va, vb in out:
        leaf = path[-1] if path else "?"
        if not (isinstance(leaf, str) and leaf in META_PATHS):
            meta_only = False
    print("  %d differing paths, meta_only=%s" % (len(out), meta_only))
    for path, va, vb in out[:25]:
        print("    %s | A(ours/bm-a)=%s | B(theirs/bm-b)=%s" % (".".join(map(str, path)), va, vb))
    if len(out) > 25:
        print("    ... %d more" % (len(out) - 25))
print("DEEP-DIFF-DONE")
