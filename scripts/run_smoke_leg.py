"""Run ONE leg block out of smoke_test.py, verbatim, without the rest of the suite.

The per-card `run_e4xx_smoke_leg.py` runners each hardcode a start and an end marker.  This one
takes the start marker on the command line and ends at the next top-level comment block, so a leg
can be re-run while it is being fixed instead of writing a new runner file per card (r1441).

  python scripts/run_smoke_leg.py "# E412:" [--next "# E406:"]
"""
import io
import json
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))


def block_for(text, start_marker, next_marker=None):
    start = text.index(start_marker)
    if next_marker:
        end = text.index(next_marker, start)
    else:
        # a leg starts at a column-0 comment and ends at the next one
        end = len(text)
        cursor = start + len(start_marker)
        while True:
            cursor = text.find("\n# ", cursor)
            if cursor < 0:
                break
            end = cursor + 1
            break
        if end == len(text):
            raise SystemExit("no next top-level leg after %r; pass --next" % start_marker)
    return text[start:end]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    start_marker = argv[1]
    next_marker = None
    if "--next" in argv:
        next_marker = argv[argv.index("--next") + 1]
    text = io.open("smoke_test.py", encoding="utf-8").read()
    block = block_for(text, start_marker, next_marker)
    if "check(" not in block:
        print("the block starting at %r calls no check(); refusing to report a pass" % start_marker)
        return 2

    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    env = {"check": check, "json": json, "os": os, "sys": sys, "__name__": "smoke_leg"}
    exec(compile(block, "smoke_test.py:%s" % start_marker.strip("# "), "exec"), env)
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + str(detail))
    print("legs %d/%d" % (sum(1 for r in results if r[1]), len(results)))
    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))