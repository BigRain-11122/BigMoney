import json
import os
import sys
from collections import OrderedDict

def lint(machines):
    """
    :param machines: dict[str, str|None] - machine name -> file content or None (missing)
    :return: dict with keys:
        - machines: dict[str, dict] - each machine's fields
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

    def render_epoch(v, t):
        if v is None:
            return '-'
        if t == 'int':
            return str(v)
        elif t == 'bool':
            return 'true' if v else 'false'
        elif t == 'str':
            return json.dumps(v)
        elif t == 'float':
            return repr(v)
        elif t == 'other':
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
        machine_result = {
            'state': 'missing',
            'epoch_type': None,
            'epoch': None,
            'epoch_pos': None,
            'clock': None,
            'verdict': 'FAIL'
        }

        if text is None:
            machine_result['state'] = 'missing'
        else:
            try:
                # Strip BOM
                if text.startswith('\ufeff'):
                    text = text[1:]
                data = json.loads(text)
                if not isinstance(data, dict):
                    machine_result['state'] = 'bad_json'
                else:
                    machine_result['state'] = 'ok'

                    # Handle heartbeat_epoch_utc
                    epoch_val = data.get('heartbeat_epoch_utc')
                    if epoch_val is None:
                        machine_result['epoch_type'] = 'missing'
                    elif isinstance(epoch_val, bool):
                        machine_result['epoch_type'] = 'bool'
                        machine_result['epoch'] = epoch_val
                        machine_result['epoch_pos'] = '-'
                    elif isinstance(epoch_val, str):
                        machine_result['epoch_type'] = 'str'
                        machine_result['epoch'] = epoch_val
                        machine_result['epoch_pos'] = '-'
                    elif isinstance(epoch_val, float):
                        machine_result['epoch_type'] = 'float'
                        machine_result['epoch'] = epoch_val
                        machine_result['epoch_pos'] = '-'
                    elif isinstance(epoch_val, int):
                        machine_result['epoch_type'] = 'int'
                        machine_result['epoch'] = epoch_val
                        machine_result['epoch_pos'] = 'yes' if epoch_val > 0 else 'no'
                    else:
                        machine_result['epoch_type'] = 'other'
                        machine_result['epoch'] = epoch_val
                        machine_result['epoch_pos'] = '-'

                    # Handle clock_read
                    clock_val = data.get('clock_read')
                    if clock_val is None:
                        machine_result['clock'] = 'missing'
                    elif isinstance(clock_val, str):
                        machine_result['clock'] = 'ok' if 'T' in clock_val else 'bad'
                    else:
                        machine_result['clock'] = 'bad'

                    # Verdict logic
                    if (machine_result['state'] == 'ok' and
                            machine_result['epoch_type'] == 'int' and
                            machine_result['epoch_pos'] == 'yes' and
                            machine_result['clock'] == 'ok'):
                        machine_result['verdict'] = 'PASS'
                        result['pass_count'] += 1

            except Exception:
                machine_result['state'] = 'bad_json'

        # Render fields
        epoch_type = machine_result['epoch_type']
        epoch = machine_result['epoch']
        epoch_pos = machine_result['epoch_pos']
        clock = machine_result['clock']
        verdict = machine_result['verdict']

        if machine_result['state'] in ('missing', 'bad_json'):
            epoch_type = '-'
            epoch = '-'
            epoch_pos = '-'
            clock = '-'

        line = (
            f"MACHINE {name} "
            f"state={machine_result['state']} "
            f"epoch_type={epoch_type or '-'} "
            f"epoch={render_epoch(epoch, epoch_type)} "
            f"epoch_pos={render_epoch_pos(epoch_pos)} "
            f"clock={render_clock(clock)} "
            f"verdict={verdict}"
        )
        result['lines'].append(line)
        result['machines'][name] = machine_result

    return result


def selftest():
    test_cases = [
        # Test case 1: All PASS
        {
            'name': 'all_pass',
            'input': {
                'bm-a': '{"machine_id":"bm-a","heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-b': '{"machine_id":"bm-b","heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26T02:02:46+08:00"}',
                'bm-c': '{"machine_id":"bm-c","heartbeat_epoch_utc":1790257907,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            'expected_pass_count': 3,
            'expected_n': 3,
            'expected_lines': [
                'MACHINE bm-a state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-b state=ok epoch_type=int epoch=1790359366 epoch_pos=yes clock=ok verdict=PASS',
                'MACHINE bm-c state=ok epoch_type=int epoch=1790257907 epoch_pos=yes clock=ok verdict=PASS',
                'VERDICT pass=3/3'
            ]
        },
        # Test case 2: epoch type family
        {
            'name': 'epoch_type_family',
            'input': {
                'bm-a': '{"heartbeat_epoch_utc":"1790359975","clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-b': '{"heartbeat_epoch_utc":true,"clock_read":"2026-09-26T02:02:46+08:00"}',
                'bm-c': '{"heartbeat_epoch_utc":1790359366.0,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            'expected_pass_count': 0,
            'expected_n': 3,
            'expected_lines': [
                'MACHINE bm-a state=ok epoch_type=str epoch="1790359975" epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-b state=ok epoch_type=bool epoch=true epoch_pos=- clock=ok verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=float epoch=1790359366.0 epoch_pos=- clock=ok verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        # Test case 3: structure family
        {
            'name': 'structure_family',
            'input': {
                'bm-a': None,
                'bm-b': '{oops',
                'bm-c': '{"machine_id":"bm-c"}'
            },
            'expected_pass_count': 0,
            'expected_n': 3,
            'expected_lines': [
                'MACHINE bm-a state=missing epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-b state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=missing epoch=- epoch_pos=- clock=missing verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        # Test case 4: clock and epoch_pos
        {
            'name': 'clock_epoch_pos',
            'input': {
                'bm-a': '{"heartbeat_epoch_utc":1790359975,"clock_read":123}',
                'bm-b': '{"heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26 02:02:46+08:00"}',
                'bm-c': '{"heartbeat_epoch_utc":0,"clock_read":"2026-09-24T21:51:47+08:00"}'
            },
            'expected_pass_count': 0,
            'expected_n': 3,
            'expected_lines': [
                'MACHINE bm-a state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=bad verdict=FAIL',
                'MACHINE bm-b state=ok epoch_type=int epoch=1790359366 epoch_pos=yes clock=bad verdict=FAIL',
                'MACHINE bm-c state=ok epoch_type=int epoch=0 epoch_pos=no clock=ok verdict=FAIL',
                'VERDICT pass=0/3'
            ]
        },
        # Test case 5: boundary cases
        {
            'name': 'boundary_cases',
            'input': {
                'bm-a': '{"heartbeat_epoch_utc":false,"clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-b': '{"heartbeat_epoch_utc":null,"clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-c': '{"heartbeat_epoch_utc":"","clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-d': '{}',
                'bm-e': '{"heartbeat_epoch_utc":4611686018427387904,"clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-f': '\ufeff{"heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}',
                'bm-g': '[1,2]',
                'bm-h': '"x"',
                'bm-i': '123',
                'bm-j': 'null'
            },
            'expected_pass_count': 1,
            'expected_n': 10,
            'expected_lines': [
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
                'VERDICT pass=1/10'
            ]
        }
    ]

    all_passed = True
    for case in test_cases:
        result = lint(case['input'])
        if result['pass_count'] != case['expected_pass_count']:
            print(f"FAILED: {case['name']} - expected pass count {case['expected_pass_count']}, got {result['pass_count']}")
            all_passed = False
        elif result['n'] != case['expected_n']:
            print(f"FAILED: {case['name']} - expected n {case['expected_n']}, got {result['n']}")
            all_passed = False
        else:
            lines_match = True
            for i, line in enumerate(case['expected_lines']):
                if result['lines'][i] != line:
                    print(f"FAILED: {case['name']} - line {i} mismatch")
                    print(f"  Expected: {line}")
                    print(f"  Got:      {result['lines'][i]}")
                    lines_match = False
            if not lines_match:
                all_passed = False

    if all_passed:
        print("ALL PASS")
        return 0
    else:
        return 1


def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/hb_epoch_lint.py [machines_dir]")
        sys.exit(2)
    elif sys.argv[1] == 'selftest':
        sys.exit(selftest())
    else:
        machines_dir = sys.argv[1]
        if not os.path.isdir(machines_dir):
            print(f"Error: {machines_dir} is not a directory", file=sys.stderr)
            sys.exit(2)

        machines = {}
        for filename in sorted(os.listdir(machines_dir)):
            if not filename.endswith('.json'):
                continue
            name = filename[:-5]
            path = os.path.join(machines_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
                machines[name] = text
            except Exception:
                machines[name] = None

        result = lint(machines)
        for line in result['lines']:
            print(line)

        if result['n'] > 0 and result['pass_count'] == result['n']:
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
