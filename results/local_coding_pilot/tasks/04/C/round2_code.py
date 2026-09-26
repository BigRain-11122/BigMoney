import sys
import os
import json
import datetime
from typing import List, Tuple, Dict, Any

def parse_iso8601(s: str) -> datetime.datetime:
    try:
        dt = datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            # Assume local timezone if no timezone info
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        return None

def get_machine_from_claimed_by(claimed_by: str) -> str:
    if not claimed_by:
        return ""
    return claimed_by.split()[0]

def process_file(filename: str, content: str, now: datetime.datetime) -> Dict[str, Any]:
    result = {
        'id': os.path.splitext(os.path.basename(filename))[0],
        'status': 'unknown',
        'claimed_at': None,
        'claimed_by': '',
        'parse_fail': False
    }

    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            result['parse_fail'] = True
            return result

        result['id'] = data.get('id', result['id'])
        result['status'] = data.get('status', 'unknown')
        claimed_by = data.get('claimed_by', '')
        result['claimed_by'] = claimed_by
        machine = get_machine_from_claimed_by(claimed_by)
        result['machine'] = machine

        claimed_at_str = data.get('claimed_at')
        if claimed_at_str:
            result['claimed_at'] = parse_iso8601(claimed_at_str)
        else:
            result['claimed_at'] = None
    except Exception:
        result['parse_fail'] = True

    return result

def calculate_age_h(claimed_at: datetime.datetime, now: datetime.datetime) -> float:
    if claimed_at is None:
        return -1.0
    try:
        diff = now - claimed_at
        return round(diff.total_seconds() / 3600.0, 1)
    except Exception:
        return -1.0

def run_selftest():
    # Use fixed time for reproducible tests
    now = datetime.datetime(2026, 9, 26, 0, 15, 0, tzinfo=datetime.timezone.utc)
    
    test_cases = [
        # Test case 1: Mixed statuses with parse_fail
        (
            [
                ("task1.json", '{"id":"task1","status":"open"}'),
                ("task2.json", '{"id":"task2","status":"claimed","claimed_at":"2026-09-25T00:00:00+08:00","claimed_by":"bm-a"}'),
                ("task3.json", '{"id":"task3","status":"done"}'),
                ("task4.json", '{"id":"task4","status":"other"}'),
                ("task5.json", '{"invalid":json}'),  # Invalid JSON
            ],
            {
                'total': 5,
                'parse_fail': 1,
                'open': 1,
                'claimed': 1,
                'done': 1,
                'other': 1,
                'stalled48h': 0,
                'max_age_h': 24.0
            }
        ),
        # Test case 2: Aging math precision
        (
            [
                ("task1.json", '{"id":"task1","status":"claimed","claimed_at":"2026-09-25T00:00:00+08:00","claimed_by":"bm-a"}'),
                ("task2.json", '{"id":"task2","status":"claimed","claimed_at":"2026-09-20T12:00:00+08:00","claimed_by":"bm-b"}'),
            ],
            {
                'total': 2,
                'parse_fail': 0,
                'open': 0,
                'claimed': 2,
                'done': 0,
                'other': 0,
                'stalled48h': 1,  # 2026-09-20T12:00:00+08:00 is more than 48h ago
                'max_age_h': 108.0
            }
        ),
    ]

    # Boundary and invalid cases
    boundary_cases = [
        # claimed_at missing
        ("task_missing_claimed_at.json", '{"id":"task1","status":"claimed"}', -1.0),
        # invalid JSON
        ("task_invalid.json", '{"invalid":json}', None),
        # top level not object
        ("task_not_object.json", '["array"]', None),
        # claimed_by with whitespace
        ("task_machine.json", '{"id":"task1","status":"claimed","claimed_at":"2026-09-25T00:00:00+00:00","claimed_by":"bm-a (OS iteration loop, round 195; ...)"}', 24.0),
        # claimed_at invalid
        ("task_invalid_claimed_at.json", '{"id":"task1","status":"claimed","claimed_at":"invalid-date"}', -1.0),
        # status other
        ("task_other_status.json", '{"id":"task1","status":"unknown"}', 0),
    ]

    passed = 0
    total_tests = len(test_cases) + len(boundary_cases)

    for i, (files, expected) in enumerate(test_cases):
        result = process_files(files, now)
        if result == expected:
            passed += 1
        else:
            print(f"Test case {i+1} failed: got {result}, expected {expected}")
            return False

    for i, (filename, content, expected_age) in enumerate(boundary_cases):
        result = process_files([(filename, content)], now)
        if expected_age is None:
            # For invalid cases, we only check that parse_fail is incremented
            if result['parse_fail'] == 1 and 'parse_fail' in result:
                passed += 1
        else:
            # For age calculation tests, we need to check the claimed items manually
            pass

    print(f"{passed}/{total_tests} assertions passed")
    if passed == total_tests:
        print("ALL PASS")
        return True
    else:
        print("Some assertions failed")
        return False

def process_files(files: List[Tuple[str, str]], now: datetime.datetime) -> Dict[str, Any]:
    stats = {
        'total': 0,
        'parse_fail': 0,
        'open': 0,
        'claimed': 0,
        'done': 0,
        'other': 0,
        'stalled48h': 0,
        'max_age_h': -1.0,
        'claimed_items': []
    }

    for filename, content in files:
        parsed = process_file(filename, content, now)
        stats['total'] += 1
        if parsed['parse_fail']:
            stats['parse_fail'] += 1
            continue

        status = parsed['status']
        if status == 'open':
            stats['open'] += 1
        elif status == 'claimed':
            stats['claimed'] += 1
            age_h = calculate_age_h(parsed['claimed_at'], now)
            machine = parsed['machine']
            stats['claimed_items'].append((parsed['id'], age_h, machine))
            if age_h > 48.0 and age_h >= 0:
                stats['stalled48h'] += 1
            if age_h > stats['max_age_h']:
                stats['max_age_h'] = age_h
        elif status == 'done':
            stats['done'] += 1
        else:
            stats['other'] += 1

    # Sort claimed items by age descending, then id ascending
    stats['claimed_items'].sort(key=lambda x: (-x[1], x[0]))

    return stats

def main():
    if len(sys.argv) == 1:
        print("Usage: python board_aging.py [board_dir]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        success = run_selftest()
        sys.exit(0 if success else 1)

    board_dir = sys.argv[1] if len(sys.argv) > 1 else "fleet/tasks"
    if not os.path.isdir(board_dir):
        print(f"Error: directory '{board_dir}' does not exist", file=sys.stderr)
        sys.exit(2)

    files = []
    for f in os.listdir(board_dir):
        if f.endswith(".json"):
            path = os.path.join(board_dir, f)
            try:
                with open(path, 'r', encoding='utf-8-sig') as fd:
                    content = fd.read()
                    files.append((path, content))
            except Exception as e:
                print(f"Error reading file '{path}': {e}", file=sys.stderr)
                sys.exit(2)

    if not files:
        print(f"Error: no .json files found in '{board_dir}'", file=sys.stderr)
        sys.exit(2)

    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    stats = process_files(files, now)

    # Print summary line
    print(
        f"BOARD total={stats['total']} parse_fail={stats['parse_fail']} "
        f"open={stats['open']} claimed={stats['claimed']} done={stats['done']} "
        f"other={stats['other']} stalled48h={stats['stalled48h']} max_age_h={stats['max_age_h']:.1f}"
    )

    # Print claimed items
    for id_, age_h, machine in stats['claimed_items']:
        print(f"CLAIMED {id_} age_h={age_h:.1f} by={machine}")

    sys.exit(0 if stats['stalled48h'] == 0 else 1)

if __name__ == "__main__":
    main()
