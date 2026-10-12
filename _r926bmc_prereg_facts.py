import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = open(r"research\PERPETUAL_N1_W221_PREREG.md", encoding="utf-8").read()
print("=== header (first 40 lines) ===")
for l in p.splitlines()[:40]:
    print(l[:170])
print("=== finalize stamp mentions ===")
for m in re.finditer(r'.*1[012]:\dx.*', p):
    print(repr(m.group(0).strip()[:180]))
print("=== replay chain mentions ===")
for m in re.finditer(r'.*replay.*', p, re.I):
    print(repr(m.group(0).strip()[:260]))
print("=== ledger anchors ===")
for m in re.finditer(r'.*907,789.*|.*481,920.*', p):
    print(repr(m.group(0).strip()[:180]))
