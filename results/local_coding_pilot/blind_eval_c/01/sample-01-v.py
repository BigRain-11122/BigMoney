import sys
import re
import os

def parse_timestamp(ts):
    return re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', ts) is not None

def validate_row(row, line_num):
    if not row.startswith("| "):
        return False, f"Line {line_num}: does not start with \"| \""
    
    # Strip leading and trailing "|"
    stripped = row.strip()
    if not stripped.startswith("| ") or not stripped.endswith(" |"):
        return False, f"Line {line_num}: malformed table row"
    
    # Remove outer pipes
    content = stripped[2:-2]
    fields = [f.strip() for f in content.split(" | ")]
    
    # Check number of fields
    if len(fields) != 5:
        return False, f"Line {line_num}: expected 5 fields, got {len(fields)}"
    
    # Check field 1: timestamp
    if not parse_timestamp(fields[0]):
        return False, f"Line {line_num}: invalid timestamp format"
    
    # Check field 2: round number starts with "R"
    if not fields[1].startswith("R"):
        return False, f"Line {line_num}: second field must start with 'R'"
    
    # Check remaining fields are non-empty
    for i, f in enumerate(fields[2:], 3):
        if not f:
            return False, f"Line {line_num}: field {i} is empty"
    
    return True, ""

def lint_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.", file=sys.stderr)
        sys.exit(2)
    
    errors = []
    for i, line in enumerate(lines, 1):
        line = line.rstrip('\n')
        if not line.strip() or not line.startswith("| "):
            continue
        is_valid, msg = validate_row(line, i)
        if not is_valid:
            errors.append(msg)
    
    for err in errors:
        print(err)
    
    if errors:
        print(f"Total errors: {len(errors)}")
        sys.exit(1)
    else:
        sys.exit(0)

def selftest():
    # Valid test cases
    valid_cases = [
        "| 2023-01-01 12:00 | R1 | verdict | did | next |",
        "| 2023-01-01 12:00 | R155 (dept:研究) | verdict | did | next |",
        "| 2023-01-01 12:00 | R999 | v | d | n |",
        "| 2023-01-01 12:00 | R1 | v | d | n |",
    ]
    
    # Invalid test cases
    invalid_cases = [
        ("| 2023-01-01 12:00 | 1 | v | d | n |", "no R prefix"),
        ("| 2023-01-01 12:00 | R1 | v | d | n | n2 |", "too many fields"),
        ("| 2023-01-01 12:00 | R1 | v | d |", "too few fields"),
        ("| 2023-01-01 12:00 | R1 | v |  | n |", "empty field"),
    ]
    
    # Test valid cases
    valid_count = 0
    for i, line in enumerate(valid_cases):
        is_valid, msg = validate_row(line, i+1)
        if is_valid:
            valid_count += 1
        else:
            print(f"Unexpected failure: {msg}")
            sys.exit(1)
    
    # Test invalid cases
    invalid_count = 0
    for line, desc in invalid_cases:
        is_valid, msg = validate_row(line, 1)
        if not is_valid:
            invalid_count += 1
    
    if valid_count < 3 or invalid_count < 4:
        print("Selftest failed: insufficient test coverage")
        sys.exit(1)
    
    print(f"{valid_count + invalid_count} assertions checked")
    print("ALL PASS")
    sys.exit(0)

def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/rr_lint.py <file.md> or python scripts/rr_lint.py selftest")
        sys.exit(2)
    
    arg = sys.argv[1]
    if arg == "selftest":
        selftest()
    else:
        lint_file(arg)

if __name__ == "__main__":
    main()
