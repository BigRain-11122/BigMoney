# -*- coding: utf-8 -*-
# r1046 bm-c: W249-template literal-face line locator (editor-build evidence)
import io
t = io.open(r"results\_w249bmc_freeze_edits.py", encoding="utf-8").read()
lines = t.split("\n")
keys = ["563_501", "565_500", "544_901", "545_100", "561_501", "544_701", "544_900",
        "68th", "69th", "r1036", "r1041", "r1040-dead", "r1030", "thirty-seventh",
        "W250p_", "W250 freezer", "W249 freezer", "queue-depth", "waits-upstream",
        "W239 A band", "247/W248", "first_clean", "hops="]
for i, ln in enumerate(lines, 1):
    hits = [k for k in keys if k in ln]
    if hits:
        print("%d: [%s] %s" % (i, ";".join(hits[:4]), ln.strip()[:150]))
