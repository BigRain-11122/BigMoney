# -*- coding: utf-8 -*-
# r1107 diagnostic 5: find the surviving 618_101..620_100 in rolled T2 + check raw T0' live faces.
import io
T0 = io.open(r"results\_w275bmc_w274_frozen_face.txt", encoding="utf-8", newline="").read()
face = "618_101..620_100"
print("RAW T0' count:", T0.count(face))
import re
for m in re.finditer(re.escape(face), T0):
    a, b = m.start(), m.end()
    print("  ctx:", repr(T0[max(0, a - 70):b + 50]))
# which lines are inside blocks? print line numbers
for n, line in enumerate(T0.split("\n"), 1):
    if face in line:
        print("  line %d: %r" % (n, line[:150]))
