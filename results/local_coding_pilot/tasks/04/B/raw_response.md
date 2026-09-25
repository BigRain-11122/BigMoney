```python
import sys
import os
import json
import re
import datetime
from typing import List, Tuple, Dict, Any

def parse_iso8601(s: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
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

def compute_aging_stats(files: List[Tuple[str, str]], now: datetime.datetime) -> Dict[str, Any]:
    stats = {
        'total': 0,
        'parse_fail': 0,
        'open': 0,
        'claimed': 0,
        'done': 0,
        'other': 0,
        'stalled48h': 0,
        'max_age_h': -1.0,
        'claimed_list': []
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
            claimed_at = parsed['claimed_at']
            age_h = -1.0
            if claimed_at is not None:
                try:
                    if claimed_at.tzinfo is None:
                        # Assume local timezone
                        local_tz = now.tzinfo
                        if local_tz:
                            claimed_at = claimed_at.replace(tzinfo=local_tz)
                    diff = (now - claimed_at).total_seconds() / 3600.0
                    age_h = round(diff, 1)
                except Exception:
                    pass

            stats['claimed_list'].append({
                'id': parsed['id'],
                'age_h': age_h,
                'machine': parsed['machine']
            })

            if age_h > 48 and age_h >= 0:
                stats['stalled48h'] += 1
            if age_h >= 0 and (stats['max_age_h'] < 0 or age_h > stats['max_age_h']):
                stats['max_age_h'] = age_h

        elif status == 'done':
            stats['done'] += 1
        else:
            stats['other'] += 1

    return stats

def format_output(stats: Dict[str, Any]) -> str:
    output_lines = []
    # Summary line
    summary = (
        f"BOARD total={stats['total']} "
        f"parse_fail={stats['parse_fail']} "
        f"open={stats['open']} "
        f"claimed={stats['claimed']} "
        f"done={stats['done']} "
        f"other={stats['other']} "
        f"stalled48h={stats['stalled48h']} "
        f"max_age_h={stats['max_age_h']:.1f}"
    )
    output_lines.append(summary)

    # Claimed items
    claimed_sorted = sorted(stats['claimed_list'], key=lambda x: (-x['age_h'], x['id']))
    for item in claimed_sorted:
        output_lines.append(f"CLAIMED {item['id']} age_h={item['age_h']:.1f} by={item['machine']}")

    return '\n'.join(output_lines)

def selftest():
    now = datetime.datetime.now(datetime.timezone.utc)
    test_cases = [
        # Test case 1: Mixed statuses including parse_fail
        [
            ("task1.json", '{"id":"task1","status":"open"}'),
            ("task2.json", '{"id":"task2","status":"claimed","claimed_at":"2024-01-01T00:00:00+08:00","claimed_by":"bm-a"}'),
            ("task3.json", '{"id":"task3","status":"done"}'),
            ("task4.json", '{"id":"task4","status":"unknown"}'),
            ("task5.json", '{"invalid": json}'),  # Invalid JSON
        ],
        # Test case 2: Aging math test (2.5h, 100h)
        [
            ("task1.json", '{"id":"task1","status":"claimed","claimed_at":"2024-01-01T00:00:00+08:00","claimed_by":"bm-a"}'),
            ("task2.json", '{"id":"task2","status":"claimed","claimed_at":"2023-12-31T00:00:00+08:00","claimed_by":"bm-b"}'),
        ]
    ]

    # Test case 1
    stats1 = compute_aging_stats(test_cases[0], now)
    assert stats1['total'] == 5
    assert stats1['parse_fail'] == 1
    assert stats1['open'] == 1
    assert stats1['claimed'] == 1
    assert stats1['done'] == 1
    assert stats1['other'] == 1
    assert stats1['stalled48h'] == 0
    assert stats1['max_age_h'] >= 0

    # Test case 2 - compute age manually to verify
    stats2 = compute_aging_stats(test_cases[1], now)
    assert stats2['claimed'] == 2
    assert stats2['stalled48h'] == 1  # One of them should be > 48h

    print("ALL PASS")
    return True

def main():
    if len(sys.argv) == 1:
        print("Usage: python board_aging.py [board_dir]")
        sys.exit(2)

    if sys.argv[1] == "selftest":
        selftest()
        sys.exit(0)

    board_dir = sys.argv[1] if len(sys.argv) > 1 else "fleet/tasks"
    if not os.path.isdir(board_dir):
        print(f"Error: Directory {board_dir} does not exist", file=sys.stderr)
        sys.exit(2)

    files = []
    for fn in os.listdir(board_dir):
        if fn.endswith(".json"):
            full_path = os.path.join(board_dir, fn)
            try:
                with open(full_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    files.append((full_path, content))
            except Exception as e:
                print(f"Error reading {fn}: {e}", file=sys.stderr)
                sys.exit(2)

    if not files:
        print(f"Error: No .json files found in {board_dir}", file=sys.stderr)
        sys.exit(2)

    now = datetime.datetime.now(datetime.timezone.utc)
    stats = compute_aging_stats(files, now)
    output = format_output(stats)
    print(output)

    if stats['stalled48h'] >= 1:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
```