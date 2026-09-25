```python
import sys
import json
import os

def read_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to read {path}: {e}", file=sys.stderr)
        sys.exit(2)

def get_or_default(obj, key, default):
    return obj.get(key, default)

def validate_panel(panel):
    if not isinstance(panel, dict):
        return False
    required_keys = ['complete', 'universe', 'attempted']
    for k in required_keys:
        if k not in panel:
            return False
    if not isinstance(panel['complete'], bool):
        return False
    if not isinstance(panel['universe'], int) or not isinstance(panel['attempted'], int):
        return False
    return True

def get_cutoff(panel):
    max_collected = get_or_default(panel, 'max_collected', None)
    if max_collected is not None:
        return max_collected
    last_pass_date = get_or_default(panel, 'last_pass_date', None)
    if last_pass_date is not None:
        return last_pass_date
    return "na"

def digest_status(data):
    mode = get_or_default(data, 'mode', 'unknown')
    enum_fails = get_or_default(data, 'enum_fails', [])
    mismatch = get_or_default(data, 'mismatch', {})
    panel = get_or_default(data, 'panel', None)

    if not isinstance(panel, dict):
        print("ERROR: panel key missing or not an object", file=sys.stderr)
        sys.exit(2)

    if not validate_panel(panel):
        print("ERROR: Invalid panel structure", file=sys.stderr)
        sys.exit(2)

    complete = panel['complete']
    universe = panel['universe']
    attempted = panel['attempted']

    if not complete or universe != attempted:
        return "INCOMPLETE"

    fails = get_or_default(panel, 'fails', [])
    mismatches = get_or_default(panel, 'mismatches', [])

    if fails or mismatches:
        return "DATA_ISSUE"

    if enum_fails:
        return "ENUM_FAIL"

    if mismatch:
        return "ENUM_FAIL"

    return "OK"

def format_output(verdict, universe, attempted, cutoff, enum_fails_len, mismatch_len):
    u = universe if universe is not None else -1
    a = attempted if attempted is not None else -1
    c = cutoff
    n1 = len(enum_fails_len) if isinstance(enum_fails_len, list) else 0
    n2 = len(mismatch_len) if isinstance(mismatch_len, dict) else 0
    return f"OPT-LANE {verdict} universe={u} attempted={a} cutoff={c} enum_fails={n1} mismatch={n2}"

def selftest():
    test_cases = [
        # OK case with all fields present and max_collected not null
        {
            "name": "OK case",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02"
                }
            },
            "expected_verdict": "OK"
        },
        # INCOMPLETE case
        {
            "name": "INCOMPLETE case",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 99,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02"
                }
            },
            "expected_verdict": "INCOMPLETE"
        },
        # ENUM_FAIL due to non-empty enum_fails
        {
            "name": "ENUM_FAIL due to enum_fails",
            "data": {
                "mode": "spawn",
                "enum_fails": ["error1"],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02"
                }
            },
            "expected_verdict": "ENUM_FAIL"
        },
        # ENUM_FAIL due to non-empty mismatch
        {
            "name": "ENUM_FAIL due to mismatch",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {"key": "value"},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02"
                }
            },
            "expected_verdict": "ENUM_FAIL"
        },
        # DATA_ISSUE due to non-empty fails
        {
            "name": "DATA_ISSUE due to fails",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02",
                    "fails": ["fail1"]
                }
            },
            "expected_verdict": "DATA_ISSUE"
        },
        # DATA_ISSUE due to non-empty mismatches
        {
            "name": "DATA_ISSUE due to mismatches",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": "2024-01-02",
                    "mismatches": ["mismatch1"]
                }
            },
            "expected_verdict": "DATA_ISSUE"
        },
        # Invalid panel structure
        {
            "name": "Invalid panel",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": "not_a_dict"
            },
            "expected_verdict": "ERROR"
        },
        # max_collected is null, fallback to last_pass_date
        {
            "name": "Fallback to last_pass_date",
            "data": {
                "mode": "spawn",
                "enum_fails": [],
                "mismatch": {},
                "panel": {
                    "complete": True,
                    "universe": 100,
                    "attempted": 100,
                    "last_pass_date": "2024-01-01",
                    "max_collected": None
                }
            },
            "expected_verdict": "OK"
        }
    ]

    passed = 0
    failed = []

    for i, case in enumerate(test_cases):
        try:
            verdict = digest_status(case["data"])
            if verdict == case["expected_verdict"]:
                passed += 1
            else:
                failed.append(f"Test {i+1} ({case['name']}): expected {case['expected_verdict']}, got {verdict}")
        except SystemExit as e:
            if case["expected_verdict"] == "ERROR":
                passed += 1
            else:
                failed.append(f"Test {i+1} ({case['name']}): unexpected exit code {e.code}")

    print(f"{passed} / {len(test_cases)} tests passed")
    if failed:
        for f in failed:
            print(f"FAIL: {f}")
        sys.exit(1)
    else:
        print("ALL PASS")
        sys.exit(0)

def main():
    if len(sys.argv) == 1:
        print("Usage: python opt_lane_digest.py <file.json> | selftest", file=sys.stderr)
        sys.exit(2)
    
    arg = sys.argv[1]
    
    if arg == "selftest":
        selftest()
    else:
        data = read_json_file(arg)
        if not isinstance(data, dict):
            print("ERROR: Root element must be an object", file=sys.stderr)
            sys.exit(2)
        
        verdict = digest_status(data)
        panel = get_or_default(data, 'panel', {})
        universe = get_or_default(panel, 'universe', None)
        attempted = get_or_default(panel, 'attempted', None)
        cutoff = get_cutoff(panel)
        enum_fails = get_or_default(data, 'enum_fails', [])
        mismatch = get_or_default(data, 'mismatch', {})

        output_line = format_output(verdict, universe, attempted, cutoff, enum_fails, mismatch)
        print(output_line)
        
        if verdict == "OK":
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
```