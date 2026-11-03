"""Run the lane-host-ownership smoke leg verbatim, without the rest of the suite.

The leg lives in smoke_test.py and is registered there; this runner extracts the
block between its own banner comment and the module guard so the leg can be
exercised in seconds while the full suite is a multi-minute run. Extracting the
source rather than re-typing the assertions is the point: a copied leg passes on
the copy, not on the suite.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANNER = "# D-20261104-05: before the 2026-11-08 whitelist review"


def extract(src: str) -> str:
    start = src.index(BANNER)
    end = src.index('if __name__ == "__main__":', start)
    return src[start:end]


def main() -> int:
    import os
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT / "scripts"))
    import json  # noqa: F401  (the leg uses it)

    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    src = (ROOT / "smoke_test.py").read_text(encoding="utf-8")
    block = extract(src)
    env = {"__name__": "lane_host_ownership_leg", "json": json, "os": os,
           "sys": sys, "check": check}
    exec(compile(block, "smoke_test.py:lho", "exec"), env)
    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            print("   " + detail)
    print("legs %d/%d" % (len(checks) - len(bad), len(checks)))
    return 0 if checks and not bad else 1


if __name__ == "__main__":
    sys.exit(main())