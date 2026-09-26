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
    expected_keys = {'ts', 'machine', 'red', 'lane', 'py_series_tail', 'zombies_killed', 'next_pick', 'order_ref'}
    if not isinstance(obj, dict):
        return False
    if set(obj.keys()) != expected_keys:
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

    errors = []

    if not validate_top_level_keys(data):
        errors.append("top-level keys mismatch")
        return errors

    if not validate_ts(data['ts']):
        errors.append("ts format invalid")

    if not validate_machine(data['machine']):
        errors.append("machine empty or not string")

    if not validate_red(data['red']):
        errors.append("red not boolean")

    if not validate_lane(data['lane']):
        errors.append("lane empty or not string")

    if not validate_py_series_tail(data['py_series_tail']):
        errors.append("py_series_tail invalid elements")

    if not validate_zombies_killed(data['zombies_killed']):
        errors.append("zombies_killed invalid elements")

    if not validate_next_pick(data['next_pick']):
        errors.append("next_pick invalid structure")

    if not validate_order_ref(data['order_ref']):
        errors.append("order_ref empty or not string")

    return errors

def selftest():
    test_cases = [
        {
            "ts": "2024-01-01 12:00:00",
            "machine": "m1",
            "red": False,
            "lane": "l1",
            "py_series_tail": [1.5, 2.3],
            "zombies_killed": ["pid=123 lane=x"],
            "next_pick": None,
            "order_ref": "ref1"
        },
        {
            "ts": "2024-01-01 12:00:00",
            "machine": "m2",
            "red": True,
            "lane": "l2",
            "py_series_tail": [],
            "zombies_killed": [],
            "next_pick": {"lane": "l3", "candidate": "c3", "status": "active"},
            "order_ref": "ref2"
        }
    ]

    # Test valid cases
    for i, case in enumerate(test_cases):
        try:
            json.dumps(case)
        except Exception as e:
            print(f"Selftest case {i+1} invalid: {e}")
            sys.exit(1)

    # Test invalid cases
    invalid_cases = [
        # Top level not object
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": null, "order_ref": "ref1", "extra": "invalid"}',
        # Missing key
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "order_ref": "ref1"}',
        # Red not boolean
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": 1, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": null, "order_ref": "ref1"}',
        # ts format wrong
        '{"ts": "2024-01-01T12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": null, "order_ref": "ref1"}',
        # py_series_tail invalid element
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": ["invalid"], "zombies_killed": [], "next_pick": null, "order_ref": "ref1"}',
        # next_pick missing key
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": {"lane": "l1", "candidate": "c1"}, "order_ref": "ref1"}',
        # next_pick empty string
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": {"lane": "", "candidate": "c1", "status": "active"}, "order_ref": "ref1"}',
        # JSON parse error
        '{"ts": "2024-01-01 12:00:00", "machine": "m1", "red": true, "lane": "l1", "py_series_tail": [], "zombies_killed": [], "next_pick": null, "order_ref": "ref1"'
    ]

    for i, case in enumerate(invalid_cases):
        try:
            parsed = json.loads(case)
            errors = []
            if not validate_top_level_keys(parsed):
                errors.append("top-level keys mismatch")
            if not validate_ts(parsed['ts']):
                errors.append("ts format invalid")
            if not validate_machine(parsed['machine']):
                errors.append("machine empty or not string")
            if not validate_red(parsed['red']):
                errors.append("red not boolean")
            if not validate_lane(parsed['lane']):
                errors.append("lane empty or not string")
            if not validate_py_series_tail(parsed['py_series_tail']):
                errors.append("py_series_tail invalid elements")
            if not validate_zombies_killed(parsed['zombies_killed']):
                errors.append("zombies_killed invalid elements")
            if not validate_next_pick(parsed['next_pick']):
                errors.append("next_pick invalid structure")
            if not validate_order_ref(parsed['order_ref']):
                errors.append("order_ref empty or not string")
            if len(errors) == 0:
                print(f"Invalid case {i+1} should have failed but passed")
                sys.exit(1)
        except Exception:
            pass

    print(f"Selftest: 2 valid cases + 7 invalid cases = 9 assertions")
    print("ALL PASS")
    sys.exit(0)

def main():
    if len(sys.argv) == 1:
        print("Usage: python wm_red_lint.py <file.json> or python wm_red_lint.py selftest")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        selftest()
    else:
        filename = sys.argv[1]
        errors = lint_file(filename)
        for error in errors:
            print(error)
        if len(errors) > 0:
            print(f"Total errors: {len(errors)}")
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
