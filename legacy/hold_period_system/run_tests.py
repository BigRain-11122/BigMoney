"""Zero-dependency test runner. Usage: python run_tests.py"""
import importlib
import inspect
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TEST_MODULES = [
    "tests.test_time_manager",
    "tests.test_risk_rules",
    "tests.test_evaluator",
]


def main() -> int:
    passed = failed = errors = 0
    failures = []
    for mod_name in TEST_MODULES:
        mod = importlib.import_module(mod_name)
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                fn()
                passed += 1
                print(f"  PASS  {mod_name}.{name}")
            except AssertionError as e:
                failed += 1
                failures.append((mod_name, name, f"AssertionError: {e}"))
                print(f"  FAIL  {mod_name}.{name}: {e}")
            except Exception:
                errors += 1
                tb = traceback.format_exc()
                failures.append((mod_name, name, tb))
                print(f"  ERROR {mod_name}.{name}\n{tb}")

    print(f"\n{passed} passed, {failed} failed, {errors} errors")
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
