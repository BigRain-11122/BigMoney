# -*- coding: utf-8 -*-
import io
t = io.open(r"results/_r874bma_w184_freeze_edits.py", encoding="utf-8").read()
j = t.find("for old, new, cnt in")
print(t[j-700:j+1500])
