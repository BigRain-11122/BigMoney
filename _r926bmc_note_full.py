import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"results\_w220bmc_freeze_edits.py", encoding="utf-8").read()
# full prereg-note line
for m in re.finditer(r'"note": "r923 freeze-window bundle.*?(?=",?\n)', t, re.S):
    print("FULL NOTE:")
    print(m.group(0))
    print("LEN:", len(m.group(0)))
print("=== placeholder guards in prereg derive ===")
d = open(r"results\_w221bmc_prereg_derive.py", encoding="utf-8").read()
for m in re.finditer(r'@[LT]\d+@', d):
    print(m.group(0), end=" ")
print()
print("=== derive header 12 lines ===")
for l in d.splitlines()[:12]:
    print(l[:160])
print("=== 46 pairs count check ===")
print("PAIR append count:", d.count("P1(") + d.count("PAIR(") + len(re.findall(r'\.append\(\(', d)))
