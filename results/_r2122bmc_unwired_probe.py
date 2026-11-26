"""r2122 bm-c: drive smoke_test.unwired_script_problems on the current tree.

Read-only. Prints the positive result (what is wired but not in git) and the negative
control (a fake leg naming a script that exists nowhere must be reported).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smoke_test as S  # noqa: E402

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bad = S.unwired_script_problems()
print("POSITIVE:", bad if bad else "none -- every referenced script is in origin/main or staged")

neg = S.unwired_script_problems(
    legs=[("probe", ["python", "scripts/__r2122_not_in_git__.py"])],
    root=root, tracked_set=set(), staged_set=set(), scan_own=False)
print("NEGATIVE:", neg)
ok = len(neg) == 1 and "__r2122_not_in_git__" in neg[0]
print("NEGATIVE_SPEAKS:", ok)
sys.exit(0 if ok else 3)
