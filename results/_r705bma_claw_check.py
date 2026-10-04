"""r705 bm-a S7: pre-commit/pre-push claw presence+parity check
(CR-normalized compare vs Tools/git-hooks canon; reinstall via the
register scripts if missing/different -- those are PS1, done by the
caller when this reports a mismatch)."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(p):
    b = open(p, "rb").read()
    return b.replace(b"\r\n", b"\n")


ok = True
for hook in ("pre-commit", "pre-push"):
    live = os.path.join(ROOT, ".git", "hooks", hook)
    canon = os.path.join(ROOT, "Tools", "git-hooks", hook)
    if not os.path.exists(live):
        print(f"{hook}: MISSING -> needs register script")
        ok = False
        continue
    if norm(live) != norm(canon):
        print(f"{hook}: DRIFT vs canon -> needs register script")
        ok = False
        continue
    print(f"{hook}: present + parity PASS")
print("claws:", "OK" if ok else "ACTION NEEDED")
