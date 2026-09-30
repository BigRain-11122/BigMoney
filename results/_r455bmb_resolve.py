"""_r455bmb_resolve.py -- bm-b r455 rebase collision resolver (vs bm-c r263, 19 UU).

Recipes per bigmoney-conflict-resolve SKILL.md:
- snapshot twins (REPORT / LIVE / DASH groups): deep-ts probe per member,
  group takes ONE side (max wall-clock ts; r98/r99/r100/r439bmb law).
- plain snapshots: take-new by deep-ts probe (R208/r100/R350 hardened:
  recursive scan, key normalized stripping _/-, wall-clock values must
  carry time-of-day, NO key-exclude tables).
- _attrition_guard_scan.json (classifier UNKNOWN): manual adjudication =
  scan-evidence snapshot, take-new by ts (r454 bm-b precedent).
- rolling-ledger (compute_audit history / regime_state history): union by
  identity key zero-loss + take-new state fields (r188/R208).
- CODELY.md: NOT a pure append on bm-b side (in-place hot-cold reorg) ->
  manual merge: keep bm-b reorg verbatim + re-insert bm-c's single appended
  r263 entry after the r455-merged pointer line (both intents preserved).
Parse-verify every JSON before writing; byte-diff evidence printed.
"""
import subprocess
import sys
import re

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")


WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def deep_ts(obj):
    """Hardened wall-clock probe: recursive, normalized keys, no excludes."""
    best = ""
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)):
                    nk = str(k).lower().replace("_", "").replace("-", "")
                    if any(nk.startswith(p) or p in nk for p in
                           ("ts", "generated", "updated", "asof", "attempt", "scanned", "written")):
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


import json

report = []


def take_group(paths):
    """Group of twin files: probe both blobs of every member, one side wins all."""
    ts_by_side = {"c": "", "m": ""}
    for p in paths:
        try:
            dc = json.loads(blob(":2:" + p))
            ts_by_side["c"] = max(ts_by_side["c"], deep_ts(dc))
        except Exception:
            pass
        try:
            dm = json.loads(blob(":3:" + p))
            ts_by_side["m"] = max(ts_by_side["m"], deep_ts(dm))
        except Exception:
            pass
    winner = "m" if ts_by_side["m"] >= ts_by_side["c"] else "c"
    for p in paths:
        spec = ":3:" + p if winner == "m" else ":2:" + p
        data = blob(spec)
        if p.endswith(".json"):
            json.loads(data)  # parse-verify
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(data)
        report.append((p, f"take-{winner} (c={ts_by_side['c'] or '-'} m={ts_by_side['m'] or '-'})"))
    return winner


def take_new(p):
    ts_c = deep_ts(json.loads(blob(":2:" + p)))
    ts_m = deep_ts(json.loads(blob(":3:" + p)))
    winner = "m" if ts_m >= ts_c else "c"
    data = blob(":3:" + p if winner == "m" else ":2:" + p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append((p, f"take-{winner} (c={ts_c} m={ts_m})"))


def union_ledger(p, ledger_key, ident, state_take_new=True):
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
    out = dict(src)  # state fields take-new
    out[ledger_key] = merged
    json.loads(json.dumps(out))  # parse-verify round-trip
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, f"union {len(hc)}+{len(hm)}->{len(merged)} on {ledger_key}/{ident}, state take-{'m' if ts_m >= ts_c else 'c'}"))


def resolve_codely():
    mine = blob(":3:CODELY.md")          # bm-b reorg face
    theirs_line = None
    for ln in blob(":2:CODELY.md").splitlines():
        if ln.startswith("- [2026-09-30 r263 bm-c]"):
            theirs_line = ln
    assert theirs_line, "bm-c r263 entry not found on origin side"
    anchor = "- 冷层指针（r455 合并"
    out, inserted = [], False
    for ln in mine.splitlines(keepends=True):
        out.append(ln)
        if not inserted and ln.startswith(anchor):
            if not theirs_line.endswith("\n"):
                theirs_line += "\n"
            out.append(theirs_line)
            inserted = True
    assert inserted, "r455 pointer anchor not found in bm-b face"
    data = "".join(out)
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append(("CODELY.md", f"manual merge: bm-b reorg kept + bm-c r263 line re-inserted after r455 pointer ({len(data)}B)"))


# -- groups (twins same side) --
take_group(["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"])
take_group(["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])
take_group(["results/dashboard_status.json", "results/dashboard_status.js"])

# -- plain snapshots --
for p in ["results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json", "results/token_usage.json",
          "results/update_status.json", "results/_attrition_guard_scan.json"]:
    take_new(p)

# -- rolling ledgers --
union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")

# -- CODELY manual merge --
resolve_codely()

print("=== _r455bmb_resolve.py ===")
for p, note in report:
    print(f"{p} | {note}")
