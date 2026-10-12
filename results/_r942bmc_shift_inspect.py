# -*- coding: utf-8 -*-
# r942 inspect: how did prior-wave derive editors order PERPETUAL-specific shifts vs general W-shifts?
import os, re, glob

here = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(here, "_w2*derive*.py"))):
    t = open(f, encoding="utf-8", newline="").read()
    print("==", os.path.basename(f), len(t))
    # show SHIFTS block order (first 40 entries)
    entries = []
    m = re.search(r"SHIFTS = \[(.*?)\n\]", t, re.S)
    if m:
        entries = re.findall(r'\("([^"]{0,60})", "([^"]{0,60})", (\d+)\)', m.group(1))
        for i, (a, b, c) in enumerate(entries[:30]):
            print(f"  {i:2d}. {c:>4}x {a!r} -> {b!r}")
    else:
        print("  (no SHIFTS block matched)")
    # any PERPETUAL-specific entries and their position vs general W-shift
    for pat in ["PERPETUAL-N1-W2", "PERPETUAL_N1_W2"]:
        idxs = [i for i, e in enumerate(entries) if pat in e[0]]
        print(f"  positions of {pat!r}-specific shifts: {idxs}")
