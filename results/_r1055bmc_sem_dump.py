# -*- coding: utf-8 -*-
"""r1055 absorb: dump actual band_semantics region from staged2 t."""
import io

t = io.open(r"results\_r1055bmc_staged2_t.txt", encoding="utf-8").read()
j = t.find('"band_semantics"')
print("band_semantics at", j)
while j > 0:
    seg = t[j:j + 120]
    print("---", repr(seg[:110]))
    j = t.find('"band_semantics"', j + 1)
# dump the A and B values
a = t.find('"A": "1-HOP')
b = t.find('"B": "1-HOP')
print("=== A value region ===")
print(t[a - 80:a + 900])
print("=== B value region ===")
print(t[b - 80:b + 900])
