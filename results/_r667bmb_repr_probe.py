# -*- coding: utf-8 -*-
# repr probe of resolver lambda line (deterministic, ASCII-only)
import io
p = r"results\_r667bmb_merge_resolve.py"
lines = io.open(p, encoding="utf-8").read().split("\n")
for i in (104, 105, 106):  # 0-based: file lines 105,106,107
    l = lines[i]
    print("L%d open=%d close=%d" % (i + 1, l.count("("), l.count(")")))
    print("  repr:", repr(l.strip())[:150])
