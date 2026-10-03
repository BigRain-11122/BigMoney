# -*- coding: utf-8 -*-
"""r441 anchor dry-run probe: report all anchors with hit-count != 1 (no writes)."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, "..", "Tools", "_r441bmc_pit_git_b2_split.py"))
spec = importlib.util.spec_from_file_location("b2", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

lines = open(m.SRC, "rb").read().split(b"\r\n")
groups = [("netpath", m.ANCHORS_NETPATH), ("parse", m.ANCHORS_PARSE),
          ("staged", m.ANCHORS_STAGED), ("stay", m.STAY)]
bad = 0
for gname, anchors in groups:
    for a in anchors:
        hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(a)]
        if len(hits) != 1:
            bad += 1
            print("MISS %s hits=%d | %s" % (gname, len(hits), a))
            frag = a.split("]")[0] + "]" if "]" in a else a[:30]
            for i, l in enumerate(lines):
                t = l.decode("utf-8")
                if frag in t:
                    print("   near L%d: %s" % (i + 1, t[:100]))
hits = [i for i, l in enumerate(lines) if m.FUSED.encode("utf-8") in l]
print("fused hits=%d" % len(hits))
print("PROBE bad=%d" % bad)
