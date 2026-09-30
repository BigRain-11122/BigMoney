"""_r458bmb_resolve2.py -- bm-b r458 rebase collision resolver (step 3/3: r458 closing-commit replay batch).

Stage :2: = union'd post-r457-replay + frozen-r458 state (origin 11:05 faces won batch-1);
stage :3: = my r458 closing commit (S6 33-leg outputs 11:18-11:27 = NEWEST faces everywhere).
All mechanical: twins/snapshots take-m by deep-ts; ledgers union zero-loss; marks union.
dashboard_status.js = js-wrapper-snapshot class (take-side whole bytes, grouped with
its .json twin per SKILL R209); scorecard_v1.json + strategy_scorecard.json grouped
(same-run faces). No CODELY / fundamental_status in this batch (r458 closing commit
did not touch them).
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")


WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
report = []


def deep_ts(obj):
    best = ""
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)):
                    nk = str(k).lower().replace("_", "").replace("-", "")
                    if any(p in nk for p in ("ts", "generated", "updated", "asof",
                                             "attempt", "scanned", "written")):
                        s = str(v)
                        if WALL.match(s) and s > best:
                            best = s
                else:
                    scan(v)
        elif isinstance(o, list):
            for it in o:
                scan(it)
    scan(obj)
    return best


def ts_of_text(text):
    m = re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", text)
    return m.group(0) if m else ""


def take_group(paths):
    ts_by_side = {"c": "", "m": ""}
    for p in paths:
        t = blob(":2:" + p)
        try:
            ts_by_side["c"] = max(ts_by_side["c"], deep_ts(json.loads(t)))
        except Exception:
            ts_by_side["c"] = max(ts_by_side["c"], ts_of_text(t))
        t = blob(":3:" + p)
        try:
            ts_by_side["m"] = max(ts_by_side["m"], deep_ts(json.loads(t)))
        except Exception:
            ts_by_side["m"] = max(ts_by_side["m"], ts_of_text(t))
    winner = "m" if ts_by_side["m"] >= ts_by_side["c"] else "c"
    for p in paths:
        data = blob((":3:" if winner == "m" else ":2:") + p)
        if p.endswith(".json"):
            json.loads(data)
        if p.endswith(".js"):
            assert "window.DASH_DATA" in data and "<<<<<<<" not in data
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(data)
        report.append((p, f"take-{winner} group (c={ts_by_side['c'] or '-'} m={ts_by_side['m'] or '-'})"))
    return winner


def take_new(p):
    ts_c = deep_ts(json.loads(blob(":2:" + p)))
    ts_m = deep_ts(json.loads(blob(":3:" + p)))
    winner = "m" if ts_m >= ts_c else "c"
    data = blob((":3:" if winner == "m" else ":2:") + p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append((p, f"take-{winner} (c={ts_c} m={ts_m})"))


def union_ledger(p, ledger_key, ident):
    dc = json.loads(blob(":2:" + p))
    dm = json.loads(blob(":3:" + p))
    hc, hm = dc[ledger_key], dm[ledger_key]
    seen, merged = set(), []
    for row in hc + hm:
        key = row[ident]
        if key not in seen:
            seen.add(key)
            merged.append(row)
    merged.sort(key=lambda r: str(r[ident]))
    ts_c, ts_m = deep_ts(dc), deep_ts(dm)
    src = dm if ts_m >= ts_c else dc
    out = dict(src)
    out[ledger_key] = merged
    json.loads(json.dumps(out))
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, f"union {len(hc)}+{len(hm)}->{len(merged)} on {ledger_key}/{ident}, state take-{'m' if ts_m >= ts_c else 'c'}"))


def union_marks(p):
    lc = [ln for ln in blob(":2:" + p).splitlines() if ln.strip()]
    lm = [ln for ln in blob(":3:" + p).splitlines() if ln.strip()]
    seen, merged = set(), []
    for ln in lc + lm:
        if ln not in seen:
            seen.add(ln)
            merged.append(ln)
    def tskey(ln):
        try:
            return str(json.loads(ln).get("ts", ""))
        except Exception:
            return ""
    merged.sort(key=tskey)
    for ln in merged:
        json.loads(ln)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(merged) + "\n")
    report.append((p, f"append-log union {len(lc)}+{len(lm)}->{len(merged)} lines, sorted by ts"))


take_group(["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"])
take_group(["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])
take_group(["results/dashboard_status.js", "results/dashboard_status.json"])
take_group(["results/scorecard_v1.json", "results/strategy_scorecard.json"])

for p in ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/token_usage.json", "results/update_status.json"]:
    take_new(p)

union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")
union_marks("results/paper/marks/marks-20260930.jsonl")

print("=== _r458bmb_resolve2.py (batch 2: r458 closing replay) ===")
for p, note in report:
    print(f"{p} | {note}")
