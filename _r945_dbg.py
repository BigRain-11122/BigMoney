# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_w227bmc_20261012_probe.py", encoding="utf-8").read() if False else None
# derive is deterministic; re-run its pipeline inline to find residual
import importlib.util
spec = importlib.util.spec_from_file_location("d", r"results/_w227bmc_probe_derive.py")
# cannot import (asserts). Instead re-derive with traceback off: just locate residual in a fresh run copy
src = io.open(r"results/_w226bmc_20261012_probe.py", encoding="utf-8").read()
import re
t = src.replace("226", "227").replace("225", "226")
t = t.replace("A-hops-prior-B EIGHTY-SEVENTH instance ", "A-hops-prior-B EIGHTY-EIGHTH instance ")
t = t.replace("EIGHTY-SIXTH ", "EIGHTY-SEVENTH ")
i = t.find('"""'); j = t.find('"""', 3) + 3
t = t[j:]
i = 0
while True:
    i = t.find("84ecb3a3a", i)
    if i < 0:
        break
    print(repr(t[i-160:i+60]))
    i += 1
