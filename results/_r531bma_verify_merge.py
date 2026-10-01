import os, re, py_compile, sys
d = os.path.join(os.environ["TEMP"], "r531_surgical")
pf = os.path.join(d, "merged_scripts__perpetual_faces.py")
n1 = os.path.join(d, "merged_scripts__perpetual_faces_n1.py")
cn = os.path.join(d, "merged_research__PERPETUAL_FACES.md")
py_compile.compile(pf, doraise=True)
py_compile.compile(n1, doraise=True)
print("COMPILE OK")
t = open(pf, encoding="utf-8").read()
print("N1_BANDS wave keys order:", re.findall(r"^\s+(\d+): \{\"a\":", t, re.M))
print("W18 row (78_001/bm-a):", "78_001" in t and '"engine_owner": "bm-a"' in t)
print("W19 row (80_001/bm-b):", "80_001" in t and '"engine_owner": "bm-b"' in t)
n = open(n1, encoding="utf-8").read()
print("n1 WAVE_CONFIGS keys order:", re.findall(r"^\s+(\d+): \{\"batch\": \"PERPETUAL-N1", n, re.M))
print("n1 W18 leg:", "_set_wave(18)" in n, "| W19 leg:", "_set_wave(19)" in n)
print("n1 PASS W18 face:", "W18 materializer face" in n, "| W19 face:", "W19 materializer face" in n)
c = open(cn, encoding="utf-8").read()
w18 = "N1 \u6ce218" in c
w19 = "N1 \u6ce219" in c
print("canon W18 row:", w18, "| canon W19 row:", w19)
# order sanity: W18 row must appear before W19 row in canon
if w18 and w19:
    print("canon order W18<W19:", c.index("N1 \u6ce218") < c.index("N1 \u6ce219"))
