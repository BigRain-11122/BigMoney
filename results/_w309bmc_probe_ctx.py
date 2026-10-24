# -*- coding: utf-8 -*-
import io
import re

s = io.open("results/_w308bmc_freeze_edits.py", encoding="utf-8").read()
for pat in ("297", "126", "130", '308: {"', "wave 308", "13:1x", "r309;", "SEAT_MSG", "SEAT_ORIGIN"):
    for m in re.finditer(re.escape(pat), s):
        print(pat, ">>>", repr(s[max(0, m.start() - 90):m.end() + 45]))
    print("===")