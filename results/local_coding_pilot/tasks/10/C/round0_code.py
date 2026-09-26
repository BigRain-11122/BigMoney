import json
import os
import sys
from collections import OrderedDict

def lint(machines):
    """
    :param machines: dict[str, str|None] - keys=machine names, values=file contents or None
    :return: dict with keys:
        - machines: dict[str, dict] - per-machine results
        - pass_count: int
        - n: int
        - lines: list[str]
    """
    result = {
        'machines': {},
        'pass_count': 0,
        'n': len(machines),
        'lines': []
    }

    def render_epoch(v, typ):
        if v is None:
            return '-'
        if typ == 'int':
            return str(v)
        elif typ == 'bool':
            return 'true' if v else 'false'
        elif typ == 'str':
            return json.dumps(v)
        elif typ == 'float':
            return repr(v)
        elif typ == 'other':
            return json.dumps(v)
        else:
            return '-'

    def render_epoch_pos(v):
        if v is None:
            return '-'
        elif v:
            return 'yes'
        else:
            return 'no'

    def render_clock(v):
        if v is None:
            return 'missing'
        elif isinstance(v, str) and 'T' in v:
            return 'ok'
        else:
            return 'bad'

    for name in sorted(machines.keys()):
        text = machines[name]
        state = 'missing'
        epoch_type = None
        epoch = None
        epoch_pos = None
        clock = None
        verdict = 'FAIL'

        if text is not None:
            try:
                # Strip BOM if present
                if text.startswith('\ufeff'):
                    text = text[1:]
                data = json.loads(text)
                if not isinstance(data, dict):
                    state = 'bad_json'
                else:
                    state = 'ok'
                    # Handle heartbeat_epoch_utc
                    if 'heartbeat_epoch_utc' not in data:
                        epoch_type = 'missing'
                        epoch = '-'
                        epoch_pos = '-'
                    else:
                        val = data['heartbeat_epoch_utc']
                        if isinstance(val, bool):
                            epoch_type = 'bool'
                            epoch = val
                            epoch_pos = '-'
                        elif isinstance(val, str):
                            epoch_type = 'str'
                            epoch = val
                            epoch_pos = '-'
                        elif isinstance(val, float):
                            epoch_type = 'float'
                            epoch = val
                            epoch_pos = '-'
                        elif isinstance(val, int):
                            epoch_type = 'int'
                            epoch = val
                            epoch_pos = 'yes' if val > 0 else 'no'
                        else:
                            epoch_type = 'other'
                            epoch = val
                            epoch_pos = '-'

                    # Handle clock_read
                    if 'clock_read' not in data:
                        clock = 'missing'
                    elif isinstance(data['clock_read'], str):
                        if 'T' in data['clock_read']:
                            clock = 'ok'
                        else:
                            clock = 'bad'
                    else:
                        clock = 'bad'

                    # Compute verdict
                    if (state == 'ok' and 
                        epoch_type == 'int' and 
                        epoch_pos == 'yes' and 
                        clock == 'ok'):
                        verdict = 'PASS'
        else:
            state = 'missing'
            epoch_type = None
            epoch = None
            epoch_pos = None
            clock = None

        # Render values for output
        r_epoch = render_epoch(epoch, epoch_type) if epoch_type is not None else '-'
        r_epoch_pos = render_epoch_pos(epoch_pos)
        r_clock = render_clock(clock)

        result['machines'][name] = {
            'state': state,
            'epoch_type': epoch_type or 'missing',
            'epoch': r_epoch,
            'epoch_pos': r_epoch_pos,
            'clock': r_clock,
            'verdict': verdict
        }

        # Build line
        line = f"MACHINE {name} state={state} epoch_type={epoch_type or 'missing'} epoch={r_epoch} epoch_pos={r_epoch_pos} clock={r_clock} verdict={verdict}"
        result['lines'].append(line)

        if verdict == 'PASS':
            result['pass_count'] += 1

    # Add final verdict line
    result['lines'].append(f"VERDICT pass={result['pass_count']}/{result['n']}")

    return result


def selftest():
    test_cases = [
        {
            "name": "all_pass",
            "machines": {
                "bm-a": '{"machine_id":"bm-a","heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-b": '{"machine_id":"bm-b","heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26T02:02:46+08:00"}',
                "bm-c": '{"machine_id":"bm-c","heartbeat_epoch_utc":1790257907,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            "expected_pass_count": 3,
            "expected_n": 3,
            "expected_lines": [
                'MACHINE bm-a state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-b state=ok epoch_type=int epoch=1790359366 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-c state=ok epoch_type=int epoch=1790257907 epoch_pos=yes clock=ok verdict=PASS',
                'VERDICT pass=3/3'
            ]
        },
        {
            "name": "epoch_type_mismatch",
            "machines": {
                "bm-a": '{"heartbeat_epoch_utc":"1790359975","clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-b": '{"heartbeat_epoch_utc":true,"clock_read":"2026-09-26T02:02:46+08:00"}',
                "bm-c": '{"heartbeat_epoch_utc":1790359366.0,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            "expected_pass_count": 0,
            "expected_n": 3,
            "expected_lines": [
                'MACHINE bm-a state=ok epoch_type=str epoch="1790359975" epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-b state=ok epoch_type=bool epoch=true epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=float epoch=1790359366.0 epoch_pos=- clock=ok verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        {
            "name": "structural_issues",
            "machines": {
                "bm-a": None,
                "bm-b": '{oops',
                "bm-c": '{"machine_id":"bm-c"}'
            },
            "expected_pass_count": 0,
            "expected_n": 3,
            "expected_lines": [
                'MACHINE bm-a state=missing epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-b state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=missing epoch=- epoch_pos=- clock=missing verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        {
            "name": "clock_and_epoch_pos",
            "machines": {
                "bm-a": '{"heartbeat_epoch_utc":1790359975,"clock_read":123}',
                "bm-b": '{"heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26 02:02:46+08:00"}',
                "bm-c": '{"heartbeat_epoch_utc":0,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            "expected_pass_count": 0,
            "expected_n": 3,
            "expected_lines": [
                'MACHINE bm-a state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=bad verdict=FAIL',
                'MACHINE bm-b state=ok epoch_type=int epoch=1790359366 epoch_pos=yes clock=bad verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=int epoch=0 epoch_pos=no clock=ok verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        {
            "name": "boundary_cases",
            "machines": {
                "bm-a": '{"heartbeat_epoch_utc":false,"clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-b": '{"heartbeat_epoch_utc":null,"clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-c": '{"heartbeat_epoch_utc":"","clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-d": '{}',
                "bm-e": '{"heartbeat_epoch_utc":4611686018427387904,"clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-f": '\ufeff{"heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}',
                "bm-g": '[1,2]',
                "bm-h": '"x"',
                "bm-i": '123',
                "bm-j": 'null'
            },
            "expected_pass_count": 1,
            "expected_n": 10,
            "expected_lines": [
                'MACHINE bm-a state=ok epoch_type=bool epoch=false epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-b state=ok epoch_type=other epoch=null epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=str epoch="" epoch_pos=- clock=bad verdict=FAIL',
                'MACHINE bm-d state=ok epoch_type=missing epoch=- epoch_pos=- clock=missing verdict=FAIL',
                'MACHINE bm-e state=ok epoch_type=int epoch=4611686018427387904 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-f state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-g state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-h state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-i state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-j state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'VERDICT pass=2/10'
            ]
        }
    ]

    all_passed = True
    for case in test_cases:
        result = lint(case["machines"])
        if result['pass_count'] != case["expected_pass_count"]:
            print(f"FAILED: {case['name']} - Expected pass count {case['expected_pass_count']}, got {result['pass_count']}")
            all_passed = False
        elif result['n'] != case["expected_n"]:
            print(f"FAILED: {case['name']} - Expected n {case['expected_n']}, got {result['n']}")
            all_passed = False
        else:
            # Compare lines
            if len(result['lines']) != len(case["expected_lines"]):
                print(f"FAILED: {case['name']} - Line count mismatch")
                all_passed = False
            else:
                for i, expected_line in enumerate(case["expected_lines"]):
                    if result['lines'][i] != expected_line:
                        print(f"FAILED: {case['name']} - Line {i} mismatch")
                        print(f"  Expected: {expected_line}")
                        print(f"  Got:      {result['lines'][i]}")
                        all_passed = False
                        break

    if all_passed:
        print("ALL PASS")
        return 0
    else:
        return 1


def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/hb_epoch_lint.py [machines_dir]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        exit(selftest())
    else:
        machines_dir = sys.argv[1]
        if not os.path.isdir(machines_dir):
            print(f"Error: {machines_dir} is not a directory", file=sys.stderr)
            sys.exit(2)

        machines = {}
        for filename in sorted(os.listdir(machines_dir)):
            if not filename.endswith('.json'):
                continue
            name = filename[:-5]  # Remove .json suffix
            path = os.path.join(machines_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
            except Exception:
                text = None
            machines[name] = text

        result = lint(machines)

        for line in result['lines']:
            print(line)

        if result['n'] > 0 and result['pass_count'] == result['n']:
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
