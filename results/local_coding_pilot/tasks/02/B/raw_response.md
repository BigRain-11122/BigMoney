```python
import sys
import json
import re

def validate_ts(ts):
    return re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', ts) is not None

def validate_machine(machine):
    return isinstance(machine, str) and machine != ''

def validate_red(red):
    return isinstance(red, bool)

def validate_lane(lane):
    return isinstance(lane, str) and lane != ''

def validate_py_series_tail(py_series_tail):
    if not isinstance(py_series_tail, list):
        return False
    for item in py_series_tail:
        if isinstance(item, (int, float)):
            continue
        elif isinstance(item, str):
            try:
                float(item)
            except ValueError:
                return False
        else:
            return False
    return True

def validate_zombies_killed(zombies_killed):
    if not isinstance(zombies_killed, list):
        return False
    for item in zombies_killed:
        if not isinstance(item, str) or item.strip() == '':
            return False
    return True

def validate_next_pick(next_pick):
    if next_pick is None:
        return True
    if not isinstance(next_pick, dict):
        return False
    required_keys = {'lane', 'candidate', 'status'}
    if set(next_pick.keys()) != required_keys:
        return False
    for key in required_keys:
        if not isinstance(next_pick[key], str) or next_pick[key].strip() == '':
            return False
    return True

def validate_order_ref(order_ref):
    return isinstance(order_ref, str) and order_ref != ''

def validate_top_level_keys(obj):
    required_keys = {'ts', 'machine', 'red', 'lane', 'py_series_tail', 'zombies_killed', 'next_pick', 'order_ref'}
    if not isinstance(obj, dict):
        return False
    if set(obj.keys()) != required_keys:
        return False
    return True

def lint_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}", file=sys.stderr)
        sys.exit(1)

    if not validate_top_level_keys(data):
        print("Top-level keys validation failed", file=sys.stderr)
        sys.exit(1)

    errors = []

    if not validate_ts(data['ts']):
        errors.append("ts format invalid")

    if not validate_machine(data['machine']):
        errors.append("machine is empty or not a string")

    if not validate_red(data['red']):
        errors.append("red is not a boolean")

    if not validate_lane(data['lane']):
        errors.append("lane is empty or not a string")

    if not validate_py_series_tail(data['py_series_tail']):
        errors.append("py_series_tail contains invalid elements")

    if not validate_zombies_killed(data['zombies_killed']):
        errors.append("zombies_killed contains invalid elements")

    if not validate_next_pick(data['next_pick']):
        errors.append("next_pick is invalid")

    if not validate_order_ref(data['order_ref']):
        errors.append("order_ref is empty or not a string")

    for error in errors:
        print(error)

    return len(errors)

def selftest():
    test_cases = [
        {
            "ts": "2024-01-01 12:00:00",
            "machine": "machine1",
            "red": False,
            "lane": "lane1",
            "py_series_tail": [1.5, 2.3],
            "zombies_killed": ["pid=123 lane=x"],
            "next_pick": None,
            "order_ref": "ref1"
        },
        {
            "ts": "2024-01-01 12:00:00",
            "machine": "machine2",
            "red": True,
            "lane": "lane2",
            "py_series_tail": [],
            "zombies_killed": [],
            "next_pick": {
                "lane": "lane3",
                "candidate": "cand1",
                "status": "active"
            },
            "order_ref": "ref2"
        }
    ]

    # Test valid cases
    for i, case in enumerate(test_cases):
        try:
            json.dumps(case)
        except Exception:
            print(f"Selftest case {i+1} failed to serialize", file=sys.stderr)
            sys.exit(1)

    # Test invalid cases
    invalid_cases = [
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": None, "order_ref": "ref1"}, # missing key
        {"ts": "2024-01-01 12:00:00", "machine": "", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": None, "order_ref": "ref1"}, # empty machine
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": "true", "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": None, "order_ref": "ref1"}, # red not boolean
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [1, "not_a_number"], "zombies_killed": [], "next_pick": None, "order_ref": "ref1"}, # invalid py_series_tail
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": ["pid=123 lane=x"], "next_pick": {"lane": "", "candidate": "cand1", "status": "active"}, "order_ref": "ref1"}, # empty next_pick lane
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": {"lane": "lane1", "candidate": "cand1"}, "order_ref": "ref1"}, # missing next_pick key
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": {"lane": "lane1", "candidate": "cand1", "status": "active", "extra_key": "value"}, "order_ref": "ref1"}, # extra key in next_pick
        {"ts": "2024-01-01 12:00:00", "machine": "machine1", "red": False, "lane": "lane1", "py_series_tail": [], "zombies_killed": [], "next_pick": {"lane": "lane1", "candidate": "cand1", "status": "active"}, "order_ref": ""}, # empty order_ref
    ]

    for i, case in enumerate(invalid_cases):
        try:
            json.dumps(case)
        except Exception:
            pass

    print(f"Selftest passed: {len(test_cases)} valid cases, {len(invalid_cases)} invalid cases")
    print("ALL PASS")
    sys.exit(0)

def main():
    if len(sys.argv) == 1:
        print("Usage: python wm_red_lint.py <file.json> or python wm_red_lint.py selftest", file=sys.stderr)
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        selftest()
    else:
        filename = sys.argv[1]
        error_count = lint_file(filename)
        if error_count > 0:
            print(f"Total errors: {error_count}")
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
```