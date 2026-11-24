"""r2036 report repair: undo a joined row and re-append it with the timestamp applied.

The closeout wrote its row with a literal %s (the format was never applied) and appended it to a
last line that had no trailing newline, so the row fused onto the previous one.  This script cuts
at the fused marker, restores the newline, and writes the row the way the closeout meant to.
"""
from __future__ import annotations

import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
MARK = "| %s | r2036"

ROW = open(os.path.join(ROOT, "results", "_r2036bmc_row.txt"), encoding="utf-8").read().strip()


def main() -> int:
    with io.open(REPORT, encoding="utf-8", newline="") as fh:
        text = fh.read()
    idx = text.find(MARK)
    if idx < 0:
        print("marker absent -- nothing fused; appending cleanly")
        head = text
    else:
        head = text[:idx].rstrip(" \t\r\n")
    out = head + "\n" + ROW + "\n"
    with io.open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    print("repaired: fused=%s rows_r2036=%d bytes=%d"
          % (idx >= 0, out.count("r2036"), len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
