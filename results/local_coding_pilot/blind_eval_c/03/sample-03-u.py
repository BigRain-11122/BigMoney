import sys
import json
import os

def load_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to read {path}: {e}", file=sys.stderr)
        sys.exit(2)

def get_or_default(obj, key, default):
    return obj.get(key, default)

def digest_status(data):
    # Parse panel
    panel = get_or_default(data, 'panel', None)
    if not isinstance(panel, dict):
        print("ERROR: panel must be an object", file=sys.stderr)
        sys.exit(2)

    mode = get_or_default(data, 'mode', 'unknown')
    enum_fails = get_or_default(data, 'enum_fails', [])
    mismatch = get_or_default(data, 'mismatch', {})

    # Extract panel fields
    complete = get_or_default(panel, 'complete', False)
    universe = get_or_default(panel, 'universe', -1)
    attempted = get_or_default(panel, 'attempted', -1)
    last_pass_date = get_or_default(panel, 'last_pass_date', None)
    max_collected = get_or_default(panel, 'max_collected', None)

    # Validate panel fields
    if not isinstance(complete, bool):
        complete = False  # fallback for invalid type

    if universe != attempted:
        return "INCOMPLETE"

    if panel.get('fails') or panel.get('mismatches'):
        return "DATA_ISSUE"

    if enum_fails:
        return "ENUM_FAIL"

    if mismatch:
        return "ENUM_FAIL"

    return "OK"

def format_digest(verdict, universe, attempted, cutoff, enum_fails_len, mismatch_len):
    return f"OPT-LANE {verdict} universe={universe} attempted={attempted} cutoff={cutoff} enum_fails={enum_fails_len} mismatch={mismatch_len}"

def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/opt_lane_digest.py <file.json> | selftest", file=sys.stderr)
        sys.exit(2)

    arg = sys.argv[1]
    if arg == "selftest":
        # Test cases
        test_cases = [
            # OK case with max_collected
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02'
                    }
                },
                'expected': 'OK'
            },
            # INCOMPLETE case
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 99,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02'
                    }
                },
                'expected': 'INCOMPLETE'
            },
            # DATA_ISSUE due to fails
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02',
                        'fails': ['error1']
                    }
                },
                'expected': 'DATA_ISSUE'
            },
            # ENUM_FAIL due to enum_fails
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': ['error1'],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02'
                    }
                },
                'expected': 'ENUM_FAIL'
            },
            # ENUM_FAIL due to mismatch
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {'key': 'value'},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02'
                    }
                },
                'expected': 'ENUM_FAIL'
            },
            # PANEL missing
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {},
                    'panel': None
                },
                'expected': 'ERROR'
            },
            # max_collected is null, fallback to last_pass_date
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': [],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': None
                    }
                },
                'expected': 'OK'
            },
            # Short-circuit test: DATA_ISSUE takes precedence over ENUM_FAIL
            {
                'data': {
                    'mode': 'spawn',
                    'enum_fails': ['error1'],
                    'mismatch': {},
                    'panel': {
                        'complete': True,
                        'universe': 100,
                        'attempted': 100,
                        'last_pass_date': '2024-01-01',
                        'max_collected': '2024-01-02',
                        'fails': ['fail1']
                    }
                },
                'expected': 'DATA_ISSUE'
            }
        ]

        passed = 0
        failed = []

        for i, tc in enumerate(test_cases):
            try:
                result = digest_status(tc['data'])
                if tc['expected'] == 'ERROR':
                    # Should have exited with code 2
                    failed.append(f"Test {i+1}: Expected error but got verdict '{result}'")
                elif result == tc['expected']:
                    passed += 1
                else:
                    failed.append(f"Test {i+1}: Expected '{tc['expected']}', got '{result}'")
            except SystemExit as e:
                if tc['expected'] == 'ERROR':
                    passed += 1
                else:
                    failed.append(f"Test {i+1}: Unexpected exit code {e.code}")

        print(f"{passed} / {len(test_cases)} tests passed")
        if failed:
            for f in failed:
                print(f"FAIL: {f}")
            sys.exit(1)
        else:
            print("ALL PASS")
            sys.exit(0)

    elif len(sys.argv) > 2:
        print("Usage: python scripts/opt_lane_digest.py <file.json> | selftest", file=sys.stderr)
        sys.exit(2)

    else:
        path = sys.argv[1]
        data = load_json_file(path)

        if not isinstance(data, dict):
            print(f"ERROR: Root must be an object in {path}", file=sys.stderr)
            sys.exit(2)

        verdict = digest_status(data)

        # Extract panel fields for output
        panel = get_or_default(data, 'panel', {})
        universe = get_or_default(panel, 'universe', -1)
        attempted = get_or_default(panel, 'attempted', -1)
        last_pass_date = get_or_default(panel, 'last_pass_date', None)
        max_collected = get_or_default(panel, 'max_collected', None)

        cutoff = max_collected if max_collected is not None else last_pass_date
        if cutoff is None:
            cutoff = "na"

        enum_fails = get_or_default(data, 'enum_fails', [])
        mismatch = get_or_default(data, 'mismatch', {})

        print(format_digest(
            verdict,
            universe,
            attempted,
            cutoff,
            len(enum_fails),
            len(mismatch)
        ))

        if verdict != "OK":
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
