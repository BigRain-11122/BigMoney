# -*- coding: utf-8 -*-
import io, re

t = io.open("scripts/perpetual_faces_n1.py", encoding="utf-8").read()
for m in re.finditer(r"\n(\s*)(324|325): \{", t):
    print("--- key", m.group(2), "at", m.start())
    print(t[m.start():m.start() + 220].replace("\n", "|"))
i = t.find('PREREG = WAVE_CONFIGS[2]["prereg"]')
print("... close region ...")
print(t[i - 500:i + 60].replace("\n", "|"))