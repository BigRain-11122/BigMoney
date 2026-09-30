# -*- coding: utf-8 -*-
src = open("scripts/trial_labor_w12.py", encoding="utf-8").read()
i = src.find("TRIAL_LABOR_W12 runner")
j = src.find('\n"""', i)
seg = src[i - 3:j + 5]
open("results/_r464bma_w12_docstring_dump.txt", "w", encoding="utf-8").write(seg)
print("docstring chars:", len(seg))
