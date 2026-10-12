import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"results\_w220bmc_freeze_edits.py", encoding="utf-8").read()
print("n1_w220 count:", t.count("n1_w220"))
print("n1w220 count:", t.count("n1w220"))
print("n1_w219 count:", t.count("n1_w219"))
print("r921 window count:", t.count("r921 window"))
print("r919 seat count:", t.count("r919 seat"))
print("r921 seat count:", t.count("r921 seat"))
print("r921 finalize count:", t.count("r921 finalize"))
print("r920 freeze count:", t.count("r920 freeze"))
print("r923 freeze count:", t.count("r923 freeze"))
print("1025 count:", t.count("1025"), "| 0916 count:", t.count("0916"))
print("10:1x count:", t.count("10:1x"))
print("=== structural lines ===")
for m in re.finditer(r'.*rows: estate 69.*', t):
    print(repr(m.group(0).strip()))
for m in re.finditer(r'.*self-asserts the 7\d-row cut.*', t):
    print(repr(m.group(0).strip()))
for m in re.finditer(r'.*_estate_ws\[\d+\].*== \[.*', t):
    print(repr(m.group(0).strip()))
for m in re.finditer(r'.*par_sec\.count.*', t):
    print(repr(m.group(0).strip()))
for m in re.finditer(r'.*par_full\.count.*', t):
    print(repr(m.group(0).strip()))
print("=== receipt-prereg-note ===")
for m in re.finditer(r'.*replay chain.*', t):
    print(repr(m.group(0).strip()[:400]))
print("=== transitive four ===")
for m in re.finditer(r'.*W219\+W218.*|.*chain-order precondition.*', t):
    print(repr(m.group(0).strip()[:200]))
print("=== own payload window contexts ===")
for m in re.finditer(r'.*r921 window.*', t):
    print(repr(m.group(0).strip()[:200]))
print("=== r919 seat contexts ===")
for m in re.finditer(r'.*r919 seat.*', t):
    print(repr(m.group(0).strip()[:200]))
print("=== finalize 10:1x contexts ===")
for m in re.finditer(r'.*10:1x.*', t):
    print(repr(m.group(0).strip()[:200]))
print("=== LIV lines ===")
for m in re.finditer(r"assert n1_t4\.count\('    # --- W\d\d\d materializer face'\) == 1.*", t):
    print(repr(m.group(0).strip()[:160]))
print("=== hdr lines ===")
for i, l in enumerate(t.splitlines()[:26]):
    print(i, repr(l[:150]))
