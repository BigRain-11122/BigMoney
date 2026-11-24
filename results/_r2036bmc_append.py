"""r2036 append helper: add one row to the round report without fusing onto the previous line.

The round's first attempt fused because the file ended without a trailing newline and the format
string was never applied.  This helper is the corrected path: fresh read, newline guard, write.
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: _r2036bmc_append.py <row-file>")
        return 2
    src = argv[0]
    if not os.path.isabs(src):
        src = os.path.join(ROOT, src)
    with io.open(src, encoding="utf-8") as fh:
        row = fh.read().strip()
    with io.open(REPORT, encoding="utf-8", newline="") as fh:
        text = fh.read()
    if not text.endswith("\n"):
        text += "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + row + "\n")
    print("appended %d bytes to %s" % (len(row), os.path.relpath(REPORT, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
