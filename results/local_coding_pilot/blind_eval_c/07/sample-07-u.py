import sys
import os
import json
import datetime
import re

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
    # Accept both "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DDTHH:MM:SS"
    try:
        # Try to parse with T separator first
        if 'T' in ts_str:
            dt = datetime.datetime.fromisoformat(ts_str)
        else:
            # Try parsing with space separator
            dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        return dt
    except ValueError:
        return None

def digest(observations, now=None):
    if now is None:
        now = datetime.datetime.now()
    results = []
    total_ok = 0
    total_missing = 0
    total_bad = 0
    total_stale = 0

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
                else:
                    ts_value = data.get(ts_field)
                    if ts_value is None:
                        status = "bad_ts"
                        ts_render = "absent"
                    elif not isinstance(ts_value, str):
                        status = "bad_ts"
                        ts_render = "nonstr"
                    else:
                        parsed_dt = parse_ts(ts_value)
                        if parsed_dt is None:
                            status = "bad_ts"
                            ts_render = ts_value
                        else:
                            status = "ok"
                            age_h = int((now - parsed_dt).total_seconds() // 3600)
                            ts_render = ts_value
                            stale = 1 if age_h >= 24 and age_h >= 0 else 0
            except json.JSONDecodeError:
                status = "missing"

        if status == "ok":
            total_ok += 1
        elif status == "bad_ts":
            total_bad += 1
        elif status == "missing":
            total_missing += 1

        results.append({
            "name": name,
            "src_basename": src_basename,
            "status": status,
            "age_h": age_h,
            "stale": stale,
            "ts_render": ts_render
        })

    # Sort results
    def sort_key(item):
        status_order = {"ok": 0, "bad_ts": 1, "missing": 2}
        return (
            status_order[item["status"]],
            -item["age_h"] if isinstance(item["age_h"], int) else 0,
            item["name"]
        )

    results.sort(key=sort_key)

    # Count stale
    total_stale = sum(1 for r in results if r["stale"])

    header = f"FRESHNESS legs={len(LEGS)} ok={total_ok} missing={total_missing} bad={total_bad} stale={total_stale} now={now.strftime('%Y-%m-%d %H:%M:%S')}"

    lines = [header]
    for r in results:
        lines.append(
            f"LEG {r['name']} age_h={r['age_h']} ts={r['ts_render']} status={r['status']} stale={r['stale']} src={r['src_basename']}"
        )

    return {
        "lines": lines,
        "total_ok": total_ok,
        "total_missing": total_missing,
        "total_bad": total_bad,
        "total_stale": total_stale
    }

def selftest():
    now = datetime.datetime.now()
    test_cases = [
        # Case 1: All OK legs with different ages (49h, 25h, 1h, 0h, 0h)
        {
            "name": "all_ok",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-24 07:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":"2026-09-25 01:00:00"}', "updated"),
                ("fundamental", "fundamental_status.json", '{"updated":"2026-09-26 01:00:00"}', "updated"),
                ("lhb", "lhb_update_status.json", '{"updated":"2026-09-26 01:00:00"}', "updated"),
                ("moneyflow", "moneyflow_update_status.json", '{"ts":"2026-09-26 01:00:00"}', "ts")
            ],
            "expected": {
                "total_ok": 5,
                "total_missing": 0,
                "total_bad": 0,
                "total_stale": 2
            }
        },
        # Case 2: Mixed status (1 ok + 1 bad_ts + 1 missing)
        {
            "name": "mixed_status",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-25 01:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":123}', "updated"),
                ("fundamental", "fundamental_status.json", '{}', "updated")
            ],
            "expected": {
                "total_ok": 1,
                "total_missing": 0,
                "total_bad": 2,
                "total_stale": 0
            }
        },
        # Case 3: Missing, bad_ts, ok
        {
            "name": "missing_bad_ok",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-25 01:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":123}', "updated"),
                ("fundamental", "fundamental_status.json", None, "updated")
            ],
            "expected": {
                "total_ok": 1,
                "total_missing": 1,
                "total_bad": 1,
                "total_stale": 0
            }
        },
        # Case 4: Bad ts field missing
        {
            "name": "ts_field_missing",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-25 01:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":"2026-09-25 01:00:00"}', "updated"),
                ("fundamental", "fundamental_status.json", '{"other_field":"value"}', "updated")
            ],
            "expected": {
                "total_ok": 2,
                "total_missing": 0,
                "total_bad": 1,
                "total_stale": 0
            }
        },
        # Case 5: Invalid JSON
        {
            "name": "invalid_json",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-25 01:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":"2026-09-25 01:00:00"', "updated"),
                ("fundamental", "fundamental_status.json", '{"updated":"2026-09-25 01:00:00"}', "updated")
            ],
            "expected": {
                "total_ok": 2,
                "total_missing": 0,
                "total_bad": 1,
                "total_stale": 0
            }
        },
        # Case 6: Future timestamp
        {
            "name": "future_timestamp",
            "observations": [
                ("ah_panel", "ah_panel_status.json", '{"ts":"2026-09-27 01:00:00"}', "ts"),
                ("daily", "update_status.json", '{"updated":"2026-09-25 01:00:00"}', "updated")
            ],
            "expected": {
                "total_ok": 2,
                "total_missing": 0,
                "total_bad": 0,
                "total_stale": 0
            }
        }
    ]

    passed = 0
    failed = []

    for case in test_cases:
        result = digest(case["observations"], now)
        expected = case["expected"]
        if (
            result["total_ok"] == expected["total_ok"] and
            result["total_missing"] == expected["total_missing"] and
            result["total_bad"] == expected["total_bad"] and
            result["total_stale"] == expected["total_stale"]
        ):
            passed += 1
        else:
            failed.append({
                "name": case["name"],
                "expected": expected,
                "actual": {
                    "total_ok": result["total_ok"],
                    "total_missing": result["total_missing"],
                    "total_bad": result["total_bad"],
                    "total_stale": result["total_stale"]
                }
            })

    print(f"{passed} / {len(test_cases)} selftests passed")
    if failed:
        for f in failed:
            print(f"FAIL: {f['name']}")
            print(f"  Expected: {f['expected']}")
            print(f"  Actual:   {f['actual']}")
        sys.exit(1)
    else:
        print("ALL PASS")
        sys.exit(0)

def main():
    if len(sys.argv) == 1:
        print("Usage: leg_freshness.py [results_dir [now_str]]")
        sys.exit(2)

    if sys.argv[1] == "selftest":
        selftest()

    results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
    now_str = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.isdir(results_dir):
        print(f"ERROR: results_dir '{results_dir}' does not exist or is not a directory", file=sys.stderr)
        sys.exit(2)

    try:
        now = datetime.datetime.now()
        if now_str:
            now = datetime.datetime.strptime(now_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("ERROR: Invalid now_str format. Must be YYYY-MM-DD HH:MM:SS", file=sys.stderr)
        sys.exit(2)

    observations = []
    for leg in LEGS:
        path = os.path.join(results_dir, leg["status_file"])
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                raw_text = f.read()
        except (FileNotFoundError, IOError):
            raw_text = None

        observations.append((leg["name"], leg["status_file"], raw_text, leg["ts_field"]))

    result = digest(observations, now)
    for line in result["lines"]:
        print(line)

    exit_code = 0
    if result["total_missing"] > 0 or result["total_bad"] > 0:
        exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
