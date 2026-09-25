```python
import sys
import os
import json
import datetime

LEGS = [
    {"name": "ah_panel", "status_file": "ah_panel_status.json", "ts_field": "ts"},
    {"name": "daily", "status_file": "update_status.json", "ts_field": "updated"},
    {"name": "fundamental", "status_file": "fundamental_status.json", "ts_field": "updated"},
    {"name": "lhb", "status_file": "lhb_update_status.json", "ts_field": "updated"},
    {"name": "moneyflow", "status_file": "moneyflow_update_status.json", "ts_field": "ts"},
    {"name": "regime", "status_file": "regime_state.json", "ts_field": "updated"},
    {"name": "token_meter", "status_file": "token_usage.json", "ts_field": "generated"}
]

def parse_ts(ts_str):
    if not isinstance(ts_str, str):
        return None
    if len(ts_str) > 60:
        ts_str = ts_str[:60]
    try:
        # Try both formats: with space or T
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.datetime.strptime(ts_str, fmt)
            except ValueError:
                continue
        # If no format matches, check if it has decimal seconds
        if "." in ts_str:
            # Try to strip decimal part and parse
            base = ts_str.split(".")[0]
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.datetime.strptime(base, fmt)
                except ValueError:
                    continue
        return None
    except Exception:
        return None

def digest(observations, now=None):
    if now is None:
        now = datetime.datetime.now()
    result = []
    counts = {"ok": 0, "missing": 0, "bad": 0, "stale": 0}
    
    for name, src_basename, raw_text_or_None, ts_field in observations:
        status = "missing"
        age_h = "-"
        stale = 0
        ts_render = "absent"
        
        if raw_text_or_None is None:
            status = "missing"
        else:
            try:
                data = json.loads(raw_text_or_None)
                if not isinstance(data, dict):
                    status = "missing"
                elif ts_field not in data:
                    status = "bad_ts"
                    ts_render = "absent"
                elif not isinstance(data[ts_field], str):
                    status = "bad_ts"
                    ts_render = "nonstr"
                else:
                    parsed_ts = parse_ts(data[ts_field])
                    if parsed_ts is None:
                        status = "bad_ts"
                        ts_render = data[ts_field]
                    else:
                        status = "ok"
                        age_h = int((now - parsed_ts).total_seconds() // 3600)
                        stale = 1 if age_h >= 24 and age_h >= 0 else 0
                        ts_render = data[ts_field]
            except Exception:
                status = "missing"

        if status == "ok":
            counts["ok"] += 1
        elif status == "bad_ts":
            counts["bad"] += 1
        elif status == "missing":
            counts["missing"] += 1

        if status == "ok" and age_h != "-":
            counts["stale"] += stale

        result.append({
            "name": name,
            "src": src_basename,
            "status": status,
            "age_h": age_h,
            "ts": ts_render,
            "stale": stale
        })

    # Sort legs: status order (ok, bad_ts, missing), then age_h desc, then name asc
    def sort_key(item):
        status_order = {"ok": 0, "bad_ts": 1, "missing": 2}
        return (
            status_order[item["status"]],
            -item["age_h"] if isinstance(item["age_h"], int) else float('-inf'),
            item["name"]
        )

    result.sort(key=sort_key)

    head_line = f"FRESHNESS legs={len(LEGS)} ok={counts['ok']} missing={counts['missing']} bad={counts['bad']} stale={counts['stale']} now={now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    return {
        "head": head_line,
        "legs": result
    }

def selftest():
    now = datetime.datetime(2026, 9, 26, 12, 0, 0)
    
    # Test case 1: All ok legs with different ages
    obs1 = [
        ("ah_panel", "ah_panel_status.json", '{"ts": "2026-09-25 13:00:00"}', "ts"),
        ("daily", "update_status.json", '{"updated": "2026-09-25 13:00:00"}', "updated"),
        ("fundamental", "fundamental_status.json", '{"updated": "2026-09-26 11:00:00"}', "updated"),
        ("lhb", "lhb_update_status.json", '{"updated": "2026-09-26 11:30:00"}', "updated"),
        ("moneyflow", "moneyflow_update_status.json", '{"ts": "2026-09-26 11:50:00"}', "ts"),
    ]
    res1 = digest(obs1, now)
    assert res1["head"] == "FRESHNESS legs=7 ok=5 missing=0 bad=0 stale=2 now=2026-09-26 12:00:00"
    assert len(res1["legs"]) == 5
    assert [l["age_h"] for l in res1["legs"]] == [49, 25, 1, 0, 0]
    
    # Test case 2: Mixed statuses
    obs2 = [
        ("ah_panel", "ah_panel_status.json", '{"ts": "2026-09-25 13:00:00"}', "ts"),
        ("daily", "update_status.json", '{"updated": 5}', "updated"),
        ("fundamental", "fundamental_status.json", '{"updated": "2026-09-25 13:00:00"}', "updated"),
    ]
    res2 = digest(obs2, now)
    assert res2["head"] == "FRESHNESS legs=7 ok=1 missing=0 bad=1 stale=0 now=2026-09-26 12:00:00"
    
    # Boundary tests
    obs3 = [
        ("ah_panel", "ah_panel_status.json", None, "ts"),
        ("daily", "update_status.json", '{"updated": "[1,2]"}', "updated"),
        ("fundamental", "fundamental_status.json", '{"updated": "2026-09-26"}', "updated"),
        ("lhb", "lhb_update_status.json", '{"updated": 5}', "updated"),
        ("moneyflow", "moneyflow_update_status.json", '{"ts": "2026-09-25 13:00:00"}', "ts"),
        ("regime", "regime_state.json", '{"updated": "2026-09-25 13:00:00"}', "updated"),
    ]
    res3 = digest(obs3, now)
    assert res3["head"] == "FRESHNESS legs=7 ok=1 missing=1 bad=3 stale=0 now=2026-09-26 12:00:00"
    
    print("ALL PASS")
    return 0

def main():
    if len(sys.argv) == 1:
        print("Usage: python leg_freshness.py [results_dir [now_str]]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        selftest()
        sys.exit(0)
    
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    now_str = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.isdir(results_dir):
        print(f"Error: {results_dir} is not a directory", file=sys.stderr)
        sys.exit(2)
    
    try:
        now = datetime.datetime.now()
        if now_str:
            now = datetime.datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Error: Invalid now_str format. Expected YYYY-MM-DD HH:MM:SS", file=sys.stderr)
        sys.exit(2)

    observations = []
    for leg in LEGS:
        path = os.path.join(results_dir, leg["status_file"])
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                raw_text = f.read()
        except Exception:
            raw_text = None
        observations.append((leg["name"], leg["status_file"], raw_text, leg["ts_field"]))

    result = digest(observations, now)
    print(result["head"])
    for leg in result["legs"]:
        print(f"LEG {leg['name']} age_h={leg['age_h']} ts={leg['ts']} status={leg['status']} stale={leg['stale']} src={leg['src']}")
    
    # Exit code logic
    exit_code = 0
    for leg in result["legs"]:
        if leg["status"] != "ok":
            exit_code = 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
```