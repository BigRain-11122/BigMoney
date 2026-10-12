# -*- coding: utf-8 -*-
# r942 gt-2: targeted searches on template AND diag final text
import io, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
T = io.open(os.path.join(HERE, "_w225bmc_freeze_edits.py"), encoding="utf-8", newline="").read()
D = io.open(os.path.join(HERE, "_r942bmc_diag_out.py"), encoding="utf-8", newline="").read()

print("== TEMPLATE: count('22 / count('23 asserts")
for m in re.finditer(r"count\('22[345][^\n]*", T):
    print(repr(m.group(0)[:130]))
print("== TEMPLATE: N1_BANDS runtime asserts")
for m in re.finditer(r"assert pf\.N1_BANDS\[22\d\] ==[^\n]*", T):
    print(repr(m.group(0)[:130]))
print("== TEMPLATE: count of 'assert pf.N1_BANDS[224] ==' =", T.count("assert pf.N1_BANDS[224] =="))
print("== TEMPLATE: count of 'assert pf.N1_BANDS[223] ==' =", T.count("assert pf.N1_BANDS[223] =="))
print("== DIAG FINAL: 'r938 ' contexts")
for m in re.finditer(r"r938 ", D):
    print(repr(D[max(0,m.start()-100):m.end()+60]))
print("== DIAG FINAL: 'r941 window' contexts")
for m in re.finditer(r"r941 window", D):
    print(repr(D[max(0,m.start()-100):m.end()+40]))
print("== DIAG FINAL: 'r937' contexts")
for m in re.finditer(r"r937", D):
    print(repr(D[max(0,m.start()-110):m.end()+50]))
print("== DIAG FINAL: 'MSG-20261012-1943-bmc-w225-seat' contexts")
for m in re.finditer(r"MSG-20261012-1943-bmc-w225-seat", D):
    print(repr(D[max(0,m.start()-90):m.end()+90]))
print("== DIAG FINAL: count 'r940 window' =", D.count("r940 window"))
print("== DIAG FINAL: count 'r939 window' =", D.count("r939 window"))
print("== TEMPLATE census check: 'MSG-20261012-175x' =", T.count("MSG-20261012-175x"), " 'MSG-20261012-1943-bmc-w225-seat' =", T.count("MSG-20261012-1943-bmc-w225-seat"))
print("== TEMPLATE: 'r938 ' contexts")
for m in re.finditer(r"r938 ", T):
    print(repr(T[max(0,m.start()-90):m.end()+50]))
print("== DIAG FINAL: count '226: {\"batch\": \"PERPETUAL-N1-W226\"' =", D.count('226: {"batch": "PERPETUAL-N1-W226"'))
print("== DIAG FINAL: count('225 count-assert forms")
for m in re.finditer(r"count\('22[3456][^\n]*", D):
    print(repr(m.group(0)[:130]))
print("== TEMPLATE: all 'PERPETUAL-N1-W225' dash contexts (census 7 check)")
print("template dash count:", T.count("PERPETUAL-N1-W225"))
