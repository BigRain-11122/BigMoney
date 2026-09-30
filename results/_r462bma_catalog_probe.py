# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = io.open("results/_r445bmb_w12_surgeon.py", encoding="utf-8").read().splitlines()
pat = re.compile(r"^(    src = sub1|    src = subn|    gb = sub1|    gb = subn|    sc = sub1|    jd = sub1|    st = sub1|    st = subn|    steps\.append|    # ---- |    res = sub1|    res = subn|    rp = sub1|    rp = subn)")
for i, l in enumerate(lines, 1):
    if pat.match(l):
        print(i, "|", l.strip()[:170])
