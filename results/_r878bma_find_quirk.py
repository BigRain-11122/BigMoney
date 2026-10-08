# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_r874bma_w184_freeze_buildgen.py", encoding="utf-8").read()
i = t.find("landed same-window")
print("first at", i)
print(t[i-200:i+300])
j = t.find("landed same-window", i+1)
while j > 0:
    print("---- next at", j)
    print(t[j-160:j+240])
    j = t.find("landed same-window", j+1)
