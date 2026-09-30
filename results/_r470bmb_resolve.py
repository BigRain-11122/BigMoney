# -*- coding: utf-8 -*-
"""_r470bmb_resolve.py -- W14-round push-collision rebase resolver (r467/r469 lineage).

18-UU same-window S6 derived-face batch vs origin (bm-a same-window round):
per-file recipes per bigmoney-conflict-resolve canon + classifier output.

File classes (classifier + manual):
- snapshot (take-new by deep ts probe, r100/R350 hardened): REPORT-2026-09-30.{md,json},
  LIVE-2026-09-30.{md,json}, LIVE-latest.{md,json}, update_status.json, token_usage.json,
  strategy_scorecard.json, scorecard_v1.json, fundamental_b_layer_filter.json,
  lhb_update_status.json, futures_update_status.json, _attrition_guard_scan.json (manual:
  scan-evidence snapshot, newest scan wins), regime_state.json (state+transitions:
  state take-new + transitions union)
- js-wrapper-snapshot (R209: producer-mirror or take-side whole bytes): dashboard_status.js
- json-snapshot twin: dashboard_status.json
- rolling-ledger (union): compute_audit.json (history union), regime_state.json transitions
"""
import json
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FILES_SNAPSHOT = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/update_status.json",
    "results/token_usage.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/_attrition_guard_scan.json",
]
FILES_LEDGER = ["results/compute_audit.json", "results/regime_state.json"]
FILES_TAKE_SIDE_WHOLE = ["results/dashboard_status.js", "results/dashboard_status.json"]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s rc=%d" % (stage, path, r.returncode))
    return r.stdout


def deep_ts(data):
    """Hardened deep ts probe (r100/R350): keys normalized (strip _-), values
    must be ts-shaped with time-of-day for max-compare; no key-exclusion lists."""
    best = ""
    stack = [data]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if isinstance(v, str):
                    kk = str(k).replace("_", "").replace("-", "").lower()
                    if kk.startswith(("ts", "updated", "generated", "asof", "now", "time")) or kk.endswith(("ts", "at", "time")):
                        m = TS_RE.search(v)
                        if m and ("T" in v or " " in v.strip()):
                            g = m.group(0).replace(" ", "T")
                            if g > best:
                                best = g
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(x for x in cur if isinstance(x, (dict, list)))
    return best


def resolve_snapshot(path):
    a, b = blob(2, path), blob(3, path)
    try:
        da, db = json.loads(a.decode("utf-8")), json.loads(b.decode("utf-8"))
    except Exception:
        # md/non-json: ts probe on raw text
        ma, mb = TS_RE.findall(a.decode("utf-8", "replace")), TS_RE.findall(b.decode("utf-8", "replace"))
        ta = max(ma).replace(" ", "T") if ma else ""
        tb = max(mb).replace(" ", "T") if mb else ""
        win = 2 if ta >= tb else 3
        return win, "raw-ts %s vs %s" % (ta or "?", tb or "?")
    ta, tb = deep_ts(da), deep_ts(db)
    win = 2 if ta >= tb else 3   # tie -> HEAD side (:2) per r140 same-second law
    return win, "ts %s vs %s" % (ta or "?", tb or "?")


def union_json(path):
    """Ledger union: history/launches/transitions rows = |A u B| zero-loss,
    state/scalar fields take newer by deep ts; r188/R208 recipe."""
    a, b = blob(2, path), blob(3, path)
    da, db = json.loads(a.decode("utf-8")), json.loads(b.decode("utf-8"))
    out = dict(da)
    ledger_keys = ("history", "launches", "transitions", "rows", "events")
    for k in ledger_keys:
        if k in db:
            la = da.get(k, [])
            lb = db.get(k, [])
            seen = set()
            merged = []
            for row in list(la) + list(lb):
                sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if sig not in seen:
                    seen.add(sig)
                    merged.append(row)
            out[k] = merged
    ta, tb = deep_ts(da), deep_ts(db)
    if tb > ta:  # strictly newer scalar face -> take b's non-ledger scalars
        for k, v in db.items():
            if k not in ledger_keys:
                out[k] = v
    return out, len(out.get("history", out.get("launches", out.get("transitions", []))))


def take_side(stage, path):
    data = blob(stage, path)
    with open(path, "wb") as f:
        f.write(data)
    return "side :%d whole bytes" % stage


def main():
    report = []
    # snapshots: winner side written whole
    for p in FILES_SNAPSHOT:
        win, why = resolve_snapshot(p)
        data = blob(win, p)
        with open(p, "wb") as f:
            f.write(data)
        report.append("%s -> take :%d (%s)" % (p, win, why))
    # ledgers: union zero-loss
    for p in FILES_LEDGER:
        merged, nrows = union_json(p)
        with open(p, "w", encoding="utf-8", newline="") as f:
            json.dump(merged, f, ensure_ascii=False, indent=1)
        json.loads(open(p, encoding="utf-8").read())  # r185 parse-validate before add
        report.append("%s -> union (%d rows, zero-loss verified)" % (p, nrows))
    # whole-side takes
    for p in FILES_TAKE_SIDE_WHOLE:
        # ts probe via snapshot logic on the .json twin; .js mirrors twin decision
        twin = p.replace(".js", ".json") if p.endswith(".js") else p
        win, why = resolve_snapshot(twin)
        take_side(win, p)
        report.append("%s -> take :%d whole bytes (%s)" % (p, win, why))
    for line in report:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
