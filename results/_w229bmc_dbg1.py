# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(HERE, "_w228bmc_freeze_edits.py"), "r", encoding="utf-8", newline="").read()
q = chr(39)  # single quote
print("quoted 228:", t.count(q + '228: {"batch"' + q))
print("quoted 227:", t.count(q + '227: {"batch"' + q))
print("any 228 batch:", t.count('228: {"batch"'))
print("any 227 batch:", t.count('227: {"batch"'))
i = t.find("assert new_cfg.count")
print("LINE399:", repr(t[i:i+95]))
i2 = t.find("assert n1_t4.count(" + q + "228")
print("LINE608:", repr(t[i2:i2+95]))
# simulate shifts 1-13 then recount
t2 = t
SH = [("n1_w228", "n1_w229", 5), ("w228_", "w229_", 9), ("n1w228", "n1w229", 2),
      ("W228", "W229", 72), ("W227", "W228", 111), ("w227_", "w228_", 94),
      ("m225", "m226", 3), ("N1_BANDS\\[225\\]", "N1_BANDS\\[226\\]", 1),
      ("_c227", "_c228", 5), ("arith_a228", "arith_a229", 3), ("arith_b228", "arith_b229", 3),
      ("n3r1_used228", "n3r1_used229", 3), ("_set_wave(228)", "_set_wave(229)", 1)]
for old, new, n in SH:
    c = t2.count(old)
    print(f"  {old!r}: {c} (expect {n})", "OK" if c == n else "MISMATCH")
    t2 = t2.replace(old, new)
print("after shifts 1-13, quoted 228:", t2.count(q + '228: {"batch"' + q))
j = t2.find("assert new_cfg.count")
print("LINE399 now:", repr(t2[j:j+95]))
