# -*- coding: utf-8 -*-
"""r808 bm-c rebase conflict resolver: results/pool_core_samples.jsonl
append-only jsonl tail-race (their 12 bm-a W199 burn-sample lines vs our
1 bm-c w17 line, empty parent section). Law: append-only union zero-loss,
byte-exact line endings (r570 pretty-blob pit), chronological ts order.
Canon credit: r807 merge-close / r863 ledger-union family."""
import re
import sys

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\pool_core_samples.jsonl"

with open(PATH, "rb") as fh:
    raw = fh.read()
lines = raw.split(b"\n")
# keep exact terminators: split on \n, re-join later; lone \r stays in-line

MARK = re.compile(rb"^(<<<<<<<|\|\|\|\|\|\|\||=======|>>>>>>>)")
ts_re = re.compile(rb'"ts": "([^"]+)"')

out = []
region = None  # None | collecting conflict-region data lines
resolved_n = 0
for ln in lines:
    if MARK.match(ln):
        if ln.startswith(b"<<<<<<<"):
            region = []           # start: collect union members
        elif ln.startswith(b">>>>>>>"):
            # end: emit chronological union (stable sort by ts)
            region.sort(key=lambda l: (ts_re.search(l).group(1)
                                       if ts_re.search(l) else b""))
            out.extend(region)
            resolved_n = len(region)
            region = None
        # ||||||| / ======= markers: skip silently
        continue
    if region is not None:
        region.append(ln)
    else:
        out.append(ln)

data = b"\n".join(out)
# marker-scan must be zero after resolution
assert not MARK.search(data), "conflict markers remain after resolve"
assert resolved_n == 13, "expected 13 union lines, got %d" % resolved_n
with open(PATH, "wb") as fh:
    fh.write(data)
print("resolved: union %d lines, ts-chronological, markers=0" % resolved_n)
for ln in out[-13:]:
    print("  " + ln[:100].decode("utf-8", "replace"))
sys.exit(0)
