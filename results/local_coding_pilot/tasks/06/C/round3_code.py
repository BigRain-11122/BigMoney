import sys
import json
import os

def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/token_breakdown.py [token_usage.json]")
        sys.exit(2)
    
    if sys.argv[1] == "selftest":
        run_selftest()
        sys.exit(0)
    
    usage_path = sys.argv[1] if len(sys.argv) > 1 else "results/token_usage.json"
    
    try:
        with open(usage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{usage_path}' not found.", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{usage_path}'.", file=sys.stderr)
        sys.exit(2)
    
    try:
        result = process_data(data)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    
    if result['error']:
        print(result['error'], file=sys.stderr)
        sys.exit(2)
    
    print(result['summary'])
    for line in result['legs']:
        print(line)
    print(result['cross'])
    print(result['delta'])

def process_data(data):
    required_keys = ['generated', 'per_round_context', 'machines', 'total_state_tokens_est', 'total_report_tokens_est']
    for key in required_keys:
        if key not in data:
            return {'error': f"Missing required key: {key}"}
    
    if not isinstance(data['per_round_context'], dict):
        return {'error': "per_round_context must be a dictionary"}
    
    if not isinstance(data['machines'], dict):
        return {'error': "machines must be a dictionary"}
    
    if not isinstance(data['total_state_tokens_est'], int) or data['total_state_tokens_est'] is True or data['total_state_tokens_est'] is False:
        return {'error': "total_state_tokens_est must be an integer"}
    
    if not isinstance(data['total_report_tokens_est'], int) or data['total_report_tokens_est'] is True or data['total_report_tokens_est'] is False:
        return {'error': "total_report_tokens_est must be an integer"}
    
    per_round_context = data['per_round_context']
    machines = data['machines']
    total_state_tokens_est = data['total_state_tokens_est']
    total_report_tokens_est = data['total_report_tokens_est']
    
    legs = []
    malformed_count = 0
    derived_state = 0
    derived_report = 0
    
    # Context legs
    mandate = per_round_context.get('mandate_read_tokens_est', 0)
    codely = per_round_context.get('codely_read_tokens_est', 0)
    
    if not isinstance(mandate, int) or mandate is True or mandate is False:
        mandate = 0
    if not isinstance(codely, int) or codely is True or codely is False:
        codely = 0
    
    legs.append(('mandate', mandate))
    legs.append(('codely', codely))
    
    # Machine legs
    for mid, machine in machines.items():
        if not isinstance(machine, dict):
            malformed_count += 1
            continue
        
        state_tokens_est = machine.get('state_tokens_est', 0)
        report_tokens_est = machine.get('report_tokens_est', 0)
        
        if not isinstance(state_tokens_est, int) or state_tokens_est is True or state_tokens_est is False:
            state_tokens_est = 0
        if not isinstance(report_tokens_est, int) or report_tokens_est is True or report_tokens_est is False:
            report_tokens_est = 0
        
        legs.append((f"{mid}/state", state_tokens_est))
        legs.append((f"{mid}/report", report_tokens_est))
        
        derived_state += state_tokens_est
        derived_report += report_tokens_est
    
    grand = sum(token for _, token in legs)
    k = len(legs)
    
    # Cross check
    cross_state = (derived_state == total_state_tokens_est)
    cross_report = (derived_report == total_report_tokens_est)
    
    # Share pct calculation
    def half_up_round(n, grand):
        if grand == 0:
            return 0.0
        # Use integer arithmetic to ensure half-up rounding
        result = (n * 1000 + grand // 2) // grand
        return result / 10.0
    
    legs_with_pct = [(name, tokens, half_up_round(tokens, grand)) for name, tokens in legs]
    
    # Sort legs: by tokens descending, then by name ascending
    legs_sorted = sorted(legs_with_pct, key=lambda x: (-x[1], x[0]))
    
    # Build output lines
    summary = f"TOKENS grand={grand} legs={k} malformed={malformed_count} state_derived={derived_state} report_derived={derived_report}"
    
    leg_lines = [f"LEG {name} tokens={tokens} share_pct={pct:.1f}" for name, tokens, pct in legs_sorted]
    
    cross_line = f"CROSS state={'true' if cross_state else 'false'} report={'true' if cross_report else 'false'}"
    
    delta_vs_prev = data.get('delta_vs_prev')
    if delta_vs_prev and isinstance(delta_vs_prev, dict):
        state_growth = delta_vs_prev.get('state_tokens_growth', 0)
        report_growth = delta_vs_prev.get('report_tokens_growth', 0)
        mandate_growth = delta_vs_prev.get('mandate_growth', 0)
        prev_generated = delta_vs_prev.get('prev_generated', 'unknown')
        
        def sign_str(x):
            if x > 0:
                return f"+{x}"
            elif x < 0:
                return f"{x}"
            else:
                return "+0"
        
        delta_line = f"DELTA state={sign_str(state_growth)} report={sign_str(report_growth)} mandate={sign_str(mandate_growth)} vs={prev_generated}"
    else:
        delta_line = "DELTA absent"
    
    return {
        'error': None,
        'summary': summary,
        'legs': leg_lines,
        'cross': cross_line,
        'delta': delta_line
    }

def run_selftest():
    # Test cases
    test_cases = [
        # Valid case with 2 machines, context legs, and delta present
        {
            "name": "valid_2machines_with_delta",
            "input": {
                "generated": "g1",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 300,
                        "report_tokens_est": 400
                    },
                    "m2": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 600
                    }
                },
                "total_state_tokens_est": 800,
                "total_report_tokens_est": 1000,
                "delta_vs_prev": {
                    "state_tokens_growth": 100,
                    "report_tokens_growth": -50,
                    "mandate_growth": 25,
                    "prev_generated": "g0"
                }
            },
            "expected": {
                "summary": "TOKENS grand=2100 legs=6 malformed=0 state_derived=800 report_derived=1000",
                "legs": [
                    "LEG m2/report tokens=600 share_pct=28.6",
                    "LEG m1/report tokens=400 share_pct=19.0",
                    "LEG m2/state tokens=500 share_pct=23.8",
                    "LEG m1/state tokens=300 share_pct=14.3",
                    "LEG codely tokens=200 share_pct=9.5",
                    "LEG mandate tokens=100 share_pct=4.8"
                ],
                "cross": "CROSS state=true report=true",
                "delta": "DELTA state=+100 report=-50 mandate=+25 vs=g0"
            }
        },
        # Valid case with zero grand
        {
            "name": "zero_grand",
            "input": {
                "generated": "g1",
                "per_round_context": {
                    "mandate_read_tokens_est": 0,
                    "codely_read_tokens_est": 0
                },
                "machines": {},
                "total_state_tokens_est": 0,
                "total_report_tokens_est": 0,
                "delta_vs_prev": {}
            },
            "expected": {
                "summary": "TOKENS grand=0 legs=2 malformed=0 state_derived=0 report_derived=0",
                "legs": [
                    "LEG codely tokens=0 share_pct=0.0",
                    "LEG mandate tokens=0 share_pct=0.0"
                ],
                "cross": "CROSS state=true report=true",
                "delta": "DELTA absent"
            }
        },
        # Invalid: missing key
        {
            "name": "missing_key",
            "input": {
                "generated": "g1",
                "per_round_context": {},
                "machines": {}
            },
            "expected": {"error": True}
        },
        # Invalid: non-dict machines
        {
            "name": "non_dict_machines",
            "input": {
                "generated": "g1",
                "per_round_context": {},
                "machines": "invalid",
                "total_state_tokens_est": 0,
                "total_report_tokens_est": 0
            },
            "expected": {"error": True}
        },
        # Invalid: malformed machine entry
        {
            "name": "malformed_machine",
            "input": {
                "generated": "g1",
                "per_round_context": {},
                "machines": {
                    "m1": "invalid"
                },
                "total_state_tokens_est": 0,
                "total_report_tokens_est": 0
            },
            "expected": {
                "summary": "TOKENS grand=0 legs=2 malformed=1 state_derived=0 report_derived=0",
                "legs": [
                    "LEG codely tokens=0 share_pct=0.0",
                    "LEG mandate tokens=0 share_pct=0.0"
                ],
                "cross": "CROSS state=true report=true",
                "delta": "DELTA absent"
            }
        },
        # Invalid: invalid token count
        {
            "name": "invalid_token_count",
            "input": {
                "generated": "g1",
                "per_round_context": {
                    "mandate_read_tokens_est": "not_int",
                    "codely_read_tokens_est": 200
                },
                "machines": {},
                "total_state_tokens_est": 0,
                "total_report_tokens_est": 0
            },
            "expected": {
                "summary": "TOKENS grand=200 legs=2 malformed=0 state_derived=0 report_derived=0",
                "legs": [
                    "LEG codely tokens=200 share_pct=100.0",
                    "LEG mandate tokens=0 share_pct=0.0"
                ],
                "cross": "CROSS state=true report=true",
                "delta": "DELTA absent"
            }
        },
        # Cross mismatch
        {
            "name": "cross_mismatch",
            "input": {
                "generated": "g1",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 300,
                        "report_tokens_est": 400
                    }
                },
                "total_state_tokens_est": 800,  # mismatch
                "total_report_tokens_est": 1000
            },
            "expected": {
                "summary": "TOKENS grand=1000 legs=4 malformed=0 state_derived=300 report_derived=400",
                "legs": [
                    "LEG m1/report tokens=400 share_pct=40.0",
                    "LEG m1/state tokens=300 share_pct=30.0",
                    "LEG codely tokens=200 share_pct=20.0",
                    "LEG mandate tokens=100 share_pct=10.0"
                ],
                "cross": "CROSS state=false report=true",
                "delta": "DELTA absent"
            }
        },
        # Half-up rounding test
        {
            "name": "half_up_rounding",
            "input": {
                "generated": "g1",
                "per_round_context": {
                    "mandate_read_tokens_est": 5,
                    "codely_read_tokens_est": 0
                },
                "machines": {},
                "total_state_tokens_est": 5,
                "total_report_tokens_est": 0
            },
            "expected": {
                "summary": "TOKENS grand=5 legs=2 malformed=0 state_derived=0 report_derived=0",
                "legs": [
                    "LEG mandate tokens=5 share_pct=100.0",
                    "LEG codely tokens=0 share_pct=0.0"
                ],
                "cross": "CROSS state=true report=true",
                "delta": "DELTA absent"
            }
        }
    ]
    
    passed = 0
    failed = []
    
    for i, tc in enumerate(test_cases):
        try:
            result = process_data(tc['input'])
        except Exception as e:
            if 'error' in tc['expected']:
                passed += 1
                continue
            else:
                failed.append(f"Test {tc['name']}: Unexpected exception: {e}")
                continue
        
        if 'error' in tc['expected']:
            failed.append(f"Test {tc['name']}: Expected error but got result")
            continue
            
        if result['summary'] != tc['expected']['summary']:
            failed.append(f"Test {tc['name']}: Summary mismatch")
            continue
            
        if result['legs'] != tc['expected']['legs']:
            failed.append(f"Test {tc['name']}: Legs mismatch")
            continue
            
        if result['cross'] != tc['expected']['cross']:
            failed.append(f"Test {tc['name']}: Cross mismatch")
            continue
            
        if result['delta'] != tc['expected']['delta']:
            failed.append(f"Test {tc['name']}: Delta mismatch")
            continue
            
        passed += 1
    
    print(f"{passed} tests passed")
    if failed:
        for f in failed:
            print(f"FAIL: {f}")
        sys.exit(1)
    
    print("ALL PASS")

if __name__ == "__main__":
    main()
