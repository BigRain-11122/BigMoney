# -*- coding: utf-8 -*-
import io
import re

t = io.open("results/_r1185bmc_w302_sixgate.py", encoding="utf-8").read()
print("bytes", len(t))
print("6+", sorted(set(re.findall(r"\b\d{6,}\b", t))))
m = re.search(r"SPLICE = '([0-9a-f]{40})'", t)
print("splice", m.group(1) if m else None)
print("ord", sorted(set(re.findall(r"\d+(?:st|nd|rd|th) consecutive", t))))
print("waves", sorted(set(re.findall(r"W30\d", t))))
print("rounds", sorted(set(re.findall(r"r118\d", t))))
print("parity", sorted(set(re.findall(r"\d+ parity", t))))
print("bands3", sorted(set(re.findall(r"\b\d{3}_\d{3}\b", t))))
print("---------- first 40 lines")
for i, l in enumerate(t.splitlines()[:40], 1):
    print(i, l)