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
        print(f"Error processing data: {e}", file=sys.stderr)
        sys.exit(2)
    
    if isinstance(result, dict):
        # Normal output
        grand = result['grand']
        legs = result['legs']
        malformed = result['malformed']
        derived_state = result['derived_state']
        derived_report = result['derived_report']
        leg_list = result['legs_list']
        delta_vs_prev = result.get('delta_vs_prev', {})
        
        print(f"TOKENS grand={grand} legs={legs} malformed={malformed} state_derived={derived_state} report_derived={derived_report}")
        
        for name, tokens, share_pct in leg_list:
            print(f"LEG {name} tokens={tokens} share_pct={share_pct:.1f}")
        
        cross_state = derived_state == result['total_state_tokens_est']
        cross_report = derived_report == result['total_report_tokens_est']
        print(f"CROSS state={str(cross_state).lower()} report={str(cross_report).lower()}")
        
        if delta_vs_prev and isinstance(delta_vs_prev, dict):
            prev = delta_vs_prev.get('prev_generated', 'unknown')
            s = delta_vs_prev.get('state_tokens_growth', 0)
            r = delta_vs_prev.get('report_tokens_growth', 0)
            m = delta_vs_prev.get('mandate_growth', 0)
            print(f"DELTA state={sign(s)} report={sign(r)} mandate={sign(m)} vs={prev}")
        else:
            print("DELTA absent")
    else:
        # Error case
        print(result, file=sys.stderr)
        sys.exit(2)

def sign(n):
    if n > 0:
        return f"+{n}"
    elif n < 0:
        return f"{n}"
    else:
        return "+0"

def process_data(data):
    required_keys = ['generated', 'per_round_context', 'machines', 'total_state_tokens_est', 'total_report_tokens_est']
    
    for key in required_keys:
        if key not in data:
            return f"Missing required key: {key}"
    
    per_round_context = data['per_round_context']
    machines = data['machines']
    total_state_tokens_est = data['total_state_tokens_est']
    total_report_tokens_est = data['total_report_tokens_est']
    
    if not isinstance(per_round_context, dict):
        return "per_round_context must be a dictionary"
    
    if not isinstance(machines, dict):
        return "machines must be a dictionary"
    
    if not isinstance(total_state_tokens_est, int) or total_state_tokens_est < 0:
        return "total_state_tokens_est must be a non-negative integer"
    
    if not isinstance(total_report_tokens_est, int) or total_report_tokens_est < 0:
        return "total_report_tokens_est must be a non-negative integer"
    
    # Process context legs
    mandate = per_round_context.get("mandate_read_tokens_est", 0)
    codely = per_round_context.get("codely_read_tokens_est", 0)
    
    if not isinstance(mandate, int) or mandate < 0:
        mandate = 0
    
    if not isinstance(codely, int) or codely < 0:
        codely = 0
    
    # Process machine legs
    malformed_count = 0
    leg_dict = {}
    
    derived_state = 0
    derived_report = 0
    
    for mid, machine in machines.items():
        if not isinstance(machine, dict):
            malformed_count += 1
            continue
        
        state_tokens_est = machine.get("state_tokens_est", 0)
        report_tokens_est = machine.get("report_tokens_est", 0)
        
        if not isinstance(state_tokens_est, int) or state_tokens_est < 0:
            state_tokens_est = 0
        
        if not isinstance(report_tokens_est, int) or report_tokens_est < 0:
            report_tokens_est = 0
        
        derived_state += state_tokens_est
        derived_report += report_tokens_est
        
        leg_dict[f"{mid}/state"] = state_tokens_est
        leg_dict[f"{mid}/report"] = report_tokens_est
    
    # Add context legs
    leg_dict["mandate"] = mandate
    leg_dict["codely"] = codely
    
    # Compute grand total and number of legs
    grand_total = sum(leg_dict.values())
    num_legs = len(leg_dict)
    
    # Compute share_pct for each leg
    leg_list = []
    for name, tokens in leg_dict.items():
        if grand_total == 0:
            share_pct = 0.0
        else:
            # Half-up rounding
            share_x10 = (tokens * 1000 + grand_total // 2) // grand_total
            share_pct = share_x10 / 10.0
        
        leg_list.append((name, tokens, share_pct))
    
    # Sort legs: by tokens descending, then name ascending
    leg_list.sort(key=lambda x: (-x[1], x[0]))
    
    return {
        'grand': grand_total,
        'legs': num_legs,
        'malformed': malformed_count,
        'derived_state': derived_state,
        'derived_report': derived_report,
        'total_state_tokens_est': total_state_tokens_est,
        'total_report_tokens_est': total_report_tokens_est,
        'legs_list': leg_list,
        'delta_vs_prev': data.get('delta_vs_prev')
    }

def run_selftest():
    test_cases = [
        # Test case 1: Normal case with all fields populated
        {
            "name": "normal_case",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 300
                    },
                    "m2": {
                        "state_tokens_est": 600,
                        "report_tokens_est": 400
                    }
                },
                "total_state_tokens_est": 1100,
                "total_report_tokens_est": 700,
                "delta_vs_prev": {
                    "prev_generated": "2024-04-30T10:00:00Z",
                    "state_tokens_growth": 100,
                    "report_tokens_growth": -50,
                    "mandate_growth": 20
                }
            },
            "expected": {
                "grand": 1900,
                "legs": 6,
                "malformed": 0,
                "derived_state": 1100,
                "derived_report": 700,
                "cross_state": True,
                "cross_report": True
            }
        },
        # Test case 2: Cross mismatch
        {
            "name": "cross_mismatch",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 300
                    }
                },
                "total_state_tokens_est": 1100,
                "total_report_tokens_est": 700
            },
            "expected": {
                "grand": 1100,
                "legs": 4,
                "malformed": 0,
                "derived_state": 500,
                "derived_report": 300,
                "cross_state": False,
                "cross_report": False
            }
        },
        # Test case 3: Malformed machine entry
        {
            "name": "malformed_machine",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": "invalid",
                    "m2": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 300
                    }
                },
                "total_state_tokens_est": 800,
                "total_report_tokens_est": 500
            },
            "expected": {
                "grand": 1100,
                "legs": 4,
                "malformed": 1,
                "derived_state": 500,
                "derived_report": 300,
                "cross_state": True,
                "cross_report": True
            }
        },
        # Test case 4: Missing required keys
        {
            "name": "missing_key",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 300
                    }
                }
                # Missing total_state_tokens_est and total_report_tokens_est
            },
            "expected": "error"
        },
        # Test case 5: Grand is zero
        {
            "name": "zero_grand",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 0,
                    "codely_read_tokens_est": 0
                },
                "machines": {},
                "total_state_tokens_est": 0,
                "total_report_tokens_est": 0
            },
            "expected": {
                "grand": 0,
                "legs": 2,
                "malformed": 0,
                "derived_state": 0,
                "derived_report": 0,
                "cross_state": True,
                "cross_report": True
            }
        },
        # Test case 6: Delta absent
        {
            "name": "delta_absent",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 100,
                    "codely_read_tokens_est": 200
                },
                "machines": {
                    "m1": {
                        "state_tokens_est": 500,
                        "report_tokens_est": 300
                    }
                },
                "total_state_tokens_est": 500,
                "total_report_tokens_est": 300
            },
            "expected": {
                "grand": 1100,
                "legs": 4,
                "malformed": 0,
                "derived_state": 500,
                "derived_report": 300,
                "cross_state": True,
                "cross_report": True
            }
        },
        # Test case 7: Half-up rounding example
        {
            "name": "half_up_rounding",
            "input": {
                "generated": "2024-05-01T10:00:00Z",
                "per_round_context": {
                    "mandate_read_tokens_est": 5,
                    "codely_read_tokens_est": 11
                },
                "machines": {},
                "total_state_tokens_est": 16,
                "total_report_tokens_est": 16
            },
            "expected": {
                "grand": 16,
                "legs": 2,
                "malformed": 0,
                "derived_state": 0,
                "derived_report": 0,
                "cross_state": False,
                "cross_report": False
            }
        }
    ]
    
    passed = 0
    failed = []
    
    for tc in test_cases:
        try:
            result = process_data(tc["input"])
            if isinstance(result, dict):
                # Normal case
                expected = tc["expected"]
                if expected == "error":
                    failed.append(f"{tc['name']}: Expected error but got success")
                    continue
                
                actual = {
                    'grand': result['grand'],
                    'legs': result['legs'],
                    'malformed': result['malformed'],
                    'derived_state': result['derived_state'],
                    'derived_report': result['derived_report'],
                    'cross_state': result['derived_state'] == result['total_state_tokens_est'],
                    'cross_report': result['derived_report'] == result['total_report_tokens_est']
                }
                
                if actual == expected:
                    passed += 1
                else:
                    failed.append(f"{tc['name']}: Expected {expected}, got {actual}")
            else:
                # Error case
                if tc["expected"] == "error":
                    passed += 1
                else:
                    failed.append(f"{tc['name']}: Expected success but got error: {result}")
        except Exception as e:
            if tc["expected"] == "error":
                passed += 1
            else:
                failed.append(f"{tc['name']}: Unexpected exception: {e}")
    
    print(f"Passed: {passed}, Failed: {len(failed)}")
    if failed:
        for f in failed:
            print(f"FAIL: {f}")
        sys.exit(1)
    else:
        print("ALL PASS")

if __name__ == "__main__":
    main()
