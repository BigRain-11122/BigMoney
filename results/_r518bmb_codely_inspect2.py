# -*- coding: utf-8 -*-
raw = open("CODELY.md", "rb").read().decode("utf-8")
lines = raw.split("\n")
strip = lambda l: l.rstrip("\r")
opens = [i for i, l in enumerate(lines) if strip(l).startswith("<<<<<<< ")]
closes = [i for i, l in enumerate(lines) if strip(l).startswith(">>>>>>> ")]
seps = [i for i, l in enumerate(lines) if strip(l) == "======="]
print("opens:", opens, "closes:", closes, "seps:", seps)
for oi, ci in zip(opens, closes):
    mid = [s for s in seps if oi < s < ci]
    print("=== block", oi, ci, "sep:", mid, "===")
    head = lines[oi + 1: mid[0]] if mid else []
    mine = lines[mid[0] + 1: ci] if mid else []
    print("--- HEAD/base side ---")
    for l in head:
        print(l[:160])
    print("--- mine side ---")
    for l in mine:
        print(l[:160])
