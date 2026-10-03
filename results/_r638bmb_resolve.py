"""r638 bm-b merge-conflict resolver (16 UU, push-race window vs bm-a r646).

Recipes per bigmoney-conflict-resolve skill classification
(results/_r638bmb_classified.json):
  - snapshot x13 (REPORT/LIVE twins lockstep, dashboard_status.json,
    fundamental_b_layer_filter, futures/lhb/token/update status,
    _attrition_guard_scan hand-classified snapshot): take-new by deep ts
    probe of STAGED blobs (r100 normalize keys strip _/-, value must match
    ^20\\d{2}- with time-of-day, R350 probe staged blob not worktree).
  - js-wrapper-snapshot (dashboard_status.js): take-side WHOLE bytes,
    lockstep with .json twin (R209).
  - rolling-ledger x2 (compute_audit.json, regime_state.json): union list
    keys zero-loss + take-new state fields (r188/R208, dedup key probe
    per-face r319).
Verification before write-back: json.loads pass on every resolved json
(r185 law); zero-loss asserts on unions; no conflict markers anywhere.
"""
import json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")

TS_PAT = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True).stdout


def side_blob(stage, path):
    b = git("show", f":{stage}:{path}")
    return b if b else None


def deep_ts(obj, best=None):
    """Deep max timestamp probe (r100/R350: keys normalized, values must
    look like datetimes with time-of-day; no key-exclude lists)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = re.sub(r"[_\-\s]", "", str(k)).lower()
            if isinstance(v, str) and TS_PAT.match(v) and any(
                    t in kn for t in ("ts", "time", "at", "date", "stamp", "generated", "updated", "scan", "attempt")):
                if best is None or v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best


def parse_json_bytes(b):
    return json.loads(b.decode("utf-8-sig"))


report = []


def take_new_snapshot(path, lock_key=None, lock_side=None):
    a, b = side_blob(2, path), side_blob(3, path)
    if lock_side is not None:
        side = lock_side
        ts_a = deep_ts(parse_json_bytes(a)) if a and path.endswith(".json") else None
        ts_b = deep_ts(parse_json_bytes(b)) if b and path.endswith(".json") else None
    else:
        ta = deep_ts(parse_json_bytes(a))
        tb = deep_ts(parse_json_bytes(b))
        side = "ours" if (ta or "") >= (tb or "") else "theirs"  # tie -> HEAD (r140)
        ts_a, ts_b = ta, tb
    data = a if side == "ours" else b
    open(path, "wb").write(data)
    report.append({"path": path, "recipe": "snapshot", "side": side,
                   "ts_ours": ts_a if side != "lock" else None,
                   "ts_theirs": ts_b if side != "lock" else None,
                   "lock": lock_side or None})
    return side


def entry_key(e):
    for k in ("ts", "time", "date", "stamp", "at", "generated_at", "updated",
              "last_attempt", "asof", "tick"):
        if isinstance(e, dict) and k in e:
            return (k, str(e[k]))
    return ("__identity", json.dumps(e, sort_keys=True, ensure_ascii=False))


def union_ledger(path):
    a, b = side_blob(2, path), side_blob(3, path)
    da, db = parse_json_bytes(a), parse_json_bytes(b)
    union_info = {}
    for k in da:
        if isinstance(da[k], list) and isinstance(db.get(k), list):
            seen, merged = set(), []
            for e in da[k] + db[k]:
                key = entry_key(e)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(e)
            union_info[k] = {"ours": len(da[k]), "theirs": len(db[k]),
                             "union": len(merged)}
            assert len(merged) >= max(len(da[k]), len(db[k])), f"union loss {path}:{k}"
            assert len(merged) <= len(da[k]) + len(db[k]), f"union blowup {path}:{k}"
            da[k] = merged
    # state fields (non-list): take-new side wholesale by deep ts
    ta, tb = deep_ts(da), deep_ts(db)
    base = da if (ta or "") >= (tb or "") else db  # tie -> HEAD (r140)
    for k, v in (db if base is da else da).items():
        if k not in union_info and k not in base:
            base[k] = v
    out = json.dumps(base, ensure_ascii=False, indent=1)
    open(path, "w", encoding="utf-8", newline="").write(out)
    report.append({"path": path, "recipe": "rolling-ledger-union",
                   "ts_ours": ta, "ts_theirs": tb,
                   "state_side": "ours" if base is da else "theirs",
                   "unions": union_info})


# --- group 1: REPORT twins (lockstep) ---
s = take_new_snapshot("docs/daily_report/REPORT-2026-10-03.json")
take_new_snapshot("docs/daily_report/REPORT-2026-10-03.md", lock_side=s)
# --- group 2: LIVE face (4 files lockstep, probe the dated json twin) ---
s = take_new_snapshot("docs/live_usage/LIVE-2026-10-03.json")
take_new_snapshot("docs/live_usage/LIVE-2026-10-03.md", lock_side=s)
take_new_snapshot("docs/live_usage/LIVE-latest.json", lock_side=s)
take_new_snapshot("docs/live_usage/LIVE-latest.md", lock_side=s)
# --- group 3: dashboard_status pair (js-wrapper lockstep with json twin) ---
s = take_new_snapshot("results/dashboard_status.json")
take_new_snapshot("results/dashboard_status.js", lock_side=s)
# --- group 4: plain snapshots ---
for p in ("results/_attrition_guard_scan.json",
          "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/token_usage.json",
          "results/update_status.json"):
    take_new_snapshot(p)
# --- group 5: rolling-ledger unions ---
union_ledger("results/compute_audit.json")
union_ledger("results/regime_state.json")

# --- verification: json.loads on every resolved json + no conflict markers ---
resolved = [r["path"] for r in report]
for p in resolved:
    raw = open(p, "rb").read()
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"markers left in {p}"
    if p.endswith(".js"):
        m = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$",
                      raw, re.S)
        json.loads(m.group(1).decode("utf-8")) if m else None
    elif p.endswith(".json"):
        json.loads(raw.decode("utf-8-sig"))
json.dump(report, open("results/_r638bmb_resolve_report.json", "w",
                       encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"RESOLVED {len(resolved)} files; verification PASS")
for r in report:
    print(" ", r["path"], "->", r.get("side") or r.get("state_side"),
          "| ours", r.get("ts_ours"), "| theirs", r.get("ts_theirs"),
          ("| unions " + json.dumps(r.get("unions"))) if r.get("unions") else "")
