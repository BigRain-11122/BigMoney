"""_r459bmb_resolve.py -- bm-b r459 rebase collision resolver (single batch).

Stage :2: = origin/main tip after 5 new commits (bm-c r267/r268 + bm-a r469 + orders + autofill);
stage :3: = my r459 closing commit cf5cc84fa (S6 38-leg re-run 12:26 + W13/BP2 products).
Mechanical per SKILL.md recipes: twins/snapshots take-new by deep-ts (groups keep same side);
ledgers union zero-loss; marks/x2 append-log union; CODELY memory-union (prefix-identity +
direct-concat suffixes, origin-first chronological); runnable_pool cross-flip merge
(origin SLOT-10 done + mine W13-JUDGE done, verified only-2-entries-differ preflight).
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


def union_log(p):
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


# ---- CODELY.md: memory-union (prefix-identity + direct-concat, origin-first) ----
base = blob(":1:CODELY.md")
o = blob(":2:CODELY.md")
m = blob(":3:CODELY.md")
assert o.startswith(base) and m.startswith(base), "CODELY prefix-identity FAIL = manual review"
new_codely = base + o[len(base):] + m[len(base):]
assert "<<<<<<<" not in new_codely and new_codely.count("[2026-09-30 r459 bm-b]") == 1
with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write(new_codely)
report.append(("CODELY.md", f"memory-union concat (base {len(base)} + origin {len(o)-len(base)} + mine {len(m)-len(base)} chars)"))

# ---- runnable_pool.json: cross-flip merge (origin SLOT-10 done + mine W13-JUDGE done) ----
pc = json.loads(blob(":2:results/runnable_pool.json"))
pm = json.loads(blob(":3:results/runnable_pool.json"))
ec = {e["id"]: e for e in pc["entries"]}
em = {e["id"]: e for e in pm["entries"]}
assert set(ec) == set(em) and len(ec) == 139
diffs = sorted(k for k in ec if ec[k] != em[k])
assert diffs == ["INNOVATION-QUOTA-SLOT-10", "TRIAL-LABOR-W13-JUDGE"], f"unexpected diff set: {diffs}"
assert em["TRIAL-LABOR-W13-JUDGE"]["status"] == "done" and ec["INNOVATION-QUOTA-SLOT-10"]["status"] == "done"
merged_entries = [em[e["id"]] if e["id"] in ("TRIAL-LABOR-W13-JUDGE",) else e for e in pc["entries"]]
out_pool = dict(pc)
out_pool["entries"] = merged_entries
statuses = {e["id"]: e["status"] for e in merged_entries}
assert statuses["TRIAL-LABOR-W13-JUDGE"] == "done" and statuses["INNOVATION-QUOTA-SLOT-10"] == "done"
json.loads(json.dumps(out_pool))
with open("results/runnable_pool.json", "w", encoding="utf-8", newline="") as f:
    json.dump(out_pool, f, ensure_ascii=False, indent=1)
report.append(("results/runnable_pool.json", "cross-flip merge: SLOT-10 done (origin bm-c r267) + W13-JUDGE done (mine r459), 139 entries zero loss"))

# ---- twin groups (same-side discipline) ----
take_group(["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"])
take_group(["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])
take_group(["results/dashboard_status.js", "results/dashboard_status.json"])
take_group(["results/scorecard_v1.json", "results/strategy_scorecard.json"])
take_group(["results/paper_export/export-2026-09-29.json", "results/paper_export/latest.json"])

# ---- single snapshots ----
for p in ["results/_attrition_guard_scan.json", "results/daily_scorecard.json",
          "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json", "results/t35_open_fill_verify.json",
          "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
          "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
          "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
          "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json"]:
    take_new(p)

# ---- ledgers ----
union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")
union_log("results/paper/marks/marks-20260930.jsonl")
union_log("results/x2_watch_log.jsonl")

print("=== _r459bmb_resolve.py (r459 closing replay, 34 UU) ===")
for p, note in report:
    print(f"{p} | {note}")
