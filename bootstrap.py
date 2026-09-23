"""One-command bootstrap: any machine, any time.

    python bootstrap.py

What it does (all paths relative to this file - no hardcoded machine paths):
  1. checks Python >= 3.10
  2. installs dependencies (falls back to Tsinghua PyPI mirror for CN networks)
  3. runs the 20-check smoke test  (python -m smoke_test)
  4. generates dashboard data     (python -m monitor.build_status)
  5. prints the "start working" quickstart

Exit 0 = machine ready. Loop registration is optional and separate
(Tools\\register_loop_task.ps1, Windows only).
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def run(cmd: list, **kw) -> int:
    print("  $", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT, **kw)


def main() -> int:
    print("=" * 60)
    print("Bigmoney bootstrap - any machine, any time")
    print("=" * 60)

    print(f"[1/4] Python check: {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("FAIL: Python >= 3.10 required (3.11 recommended)")
        return 1

    print("[2/4] dependencies")
    rc = run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
    if rc != 0:
        print("  primary PyPI failed, retrying with Tsinghua mirror ...")
        rc = run([sys.executable, "-m", "pip", "install", "-q", "-r",
                  "requirements.txt", "-i", MIRROR])
        if rc != 0:
            print("FAIL: dependency install failed on both mirrors")
            return 1

    print("[3/4] smoke test (20 checks)")
    rc = run([sys.executable, "-m", "smoke_test"])
    if rc != 0:
        print("FAIL: smoke test red - fix the listed checks before working")
        return 1

    print("[4/4] dashboard data")
    run([sys.executable, "-m", "monitor.build_status"])

    print()
    print("=" * 60)
    print("READY. Machine is ready to work:")
    print("  - open company console : bigmoney.html")
    print("  - AI loop (Windows, optional, path-agnostic):")
    print("      powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register_loop_task.ps1")
    print("  - a Codely session here auto-reads PLAN.md + CODELY.md rules")
    print("  - full handover guide : research/HANDOVER.md")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
