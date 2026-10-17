# -*- coding: utf-8 -*-
# r1081 bm-c: W265 derive needle-count pre-flight (measure every VMAP_FLOORS candidate on T0, one pass).
# Canon-clone of _w264bmc_needle_probe.py pattern; floors extracted from the derive script source via
# ast (zero transcription); evidence -> results/_w265bmc_needle_counts.txt (dead r1080 window authored
# floors but died before writing this evidence file; THIS window re-measures live).
import io, os, re, ast

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T0 = io.open(os.path.join(REPO, "results", "_w265bmc_w264_frozen_face.txt"), encoding="utf-8", newline="").read()
SRC = io.open(os.path.join(REPO, "results", "_w265bmc_prereg_derive.py"), encoding="utf-8").read()

m = re.search(r"VMAP_FLOORS = (\{.*?\n\})", SRC, re.S)
assert m, "VMAP_FLOORS block not found in derive script"
floors = ast.literal_eval(m.group(1))

lines = []
mismatch = 0
for k, f in floors.items():
    c = T0.count(k)
    ok = (c >= f) if f > 0 else (c == 0)
    if not ok:
        mismatch += 1
    lines.append("%s = %d (floor=%d %s)" % (k, c, f, "OK" if ok else "MISMATCH"))
txt = "\n".join(lines)
print(txt)
print("\nfloors_total=%d mismatch=%d" % (len(floors), mismatch))
io.open(os.path.join(REPO, "results", "_w265bmc_needle_counts.txt"), "w", encoding="utf-8", newline="").write(txt + "\n")
print("written results/_w265bmc_needle_counts.txt")
if mismatch:
    raise SystemExit("NEEDLE MISMATCH x%d — heal floors in derive script before run (disclose)" % mismatch)
print("ALL FLOORS OK")
