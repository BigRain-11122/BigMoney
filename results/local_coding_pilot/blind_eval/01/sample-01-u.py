import sys
import re
import os

def parse_timestamp(ts):
    return re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', ts) is not None

def validate_row(row, line_num):
    if not row.startswith("| "):
        return False, f"Line {line_num}: does not start with \"| \""
    
    # Remove leading and trailing "|"
    cleaned = row[2:].rstrip()
    if not cleaned.endswith("|"):
        return False, f"Line {line_num}: does not end with \"|\""
    
    cleaned = cleaned[:-1]
    
    fields = [f.strip() for f in cleaned.split(" | ")]
    
    if len(fields) != 5:
        return False, f"Line {line_num}: expected 5 fields, got {len(fields)}"
    
    # Check timestamp
    if not parse_timestamp(fields[0]):
        return False, f"Line {line_num}: invalid timestamp format"
    
    # Check round number field (field 2)
    if not re.match(r'^R\d+(?: \(dept:.+\))?$', fields[1]):
        return False, f"Line {line_num}: field 2 must start with \"R\" followed by digits"
    
    # Check other fields are non-empty after stripping
    for i, field in enumerate(fields[2:], start=3):
        if not field:
            return False, f"Line {line_num}: field {i} is empty or whitespace only"
    
    return True, ""

def lint_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        sys.exit(2)
    
    errors = []
    for i, line in enumerate(lines, start=1):
        is_valid, msg = validate_row(line.strip(), i)
        if not is_valid:
            errors.append(msg)
    
    for error in errors:
        print(error)
    
    if errors:
        print(f"Total violations: {len(errors)}")
        sys.exit(1)
    else:
        sys.exit(0)

def selftest():
    test_cases = [
        "| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |",
        "| 2023-04-05 12:30 | R123 (dept:research) | PASS | did1 | next1 |",
        "| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |",
        "| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |",
        "| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |",
        "| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |",
    ]
    
    # Test invalid cases
    invalid_cases = [
        ("| 2023-04-05 12:30 | 123 | PASS | did1 | next1 |", "missing R prefix"),
        ("| 2023-04-05 12:30 | R123 | PASS | did1 |", "too few fields"),
        ("| 2023-04-05 12:30 | R123 | PASS | did1 | next1 | extra |", "too many fields"),
        ("| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |", "empty field in middle"),
        ("| 2023-04-05 12:30 | R123 | PASS | did1 | next1 |", "invalid timestamp"),
    ]
    
    all_passed = True
    total_tests = len(test_cases) + len(invalid_cases)
    
    for i, line in enumerate(test_cases):
        is_valid, msg = validate_row(line.strip(), i+1)
        if not is_valid:
            print(f"FAIL: Valid case {i+1}: {msg}")
            all_passed = False
    
    for i, (line, desc) in enumerate(invalid_cases):
        is_valid, msg = validate_row(line.strip(), i+1)
        if is_valid:
            print(f"FAIL: Invalid case {i+1} ({desc}): should have failed but passed")
            all_passed = False
    
    if all_passed:
        print(f"{total_tests} assertions checked. ALL PASS")
        sys.exit(0)
    else:
        sys.exit(1)

def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/rr_lint.py <file.md> or python scripts/rr_lint.py selftest")
        sys.exit(2)
    
    if sys.argv[1] == "selftest":
        selftest()
    else:
        lint_file(sys.argv[1])

if __name__ == "__main__":
    main()
