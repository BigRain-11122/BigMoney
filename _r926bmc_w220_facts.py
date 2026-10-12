import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"results\_w220bmc_freeze_edits.py", encoding="utf-8").read()
print("=== transitive entries ===")
for m in re.finditer(r'"w2\d\d_transitive": \{[^}]*\}', t):
    print(m.group(0)[:200])
print("=== SEAT ===")
for m in re.finditer(r'SEAT_MSG = .*\n|SEAT_ORIGIN = .*\n', t):
    print(m.group(0).strip())
print("=== anchors ===")
for m in re.finditer(r'assert w22\d+_total == .*|assert \(a_lo, a_hi\).*|def fmt\(n\).*', t):
    print(m.group(0).strip())
print("=== live ordinal ===")
for m in re.finditer(r'assert len\(owner_rows_live\) == .*|assert len\(bmc_rows_live\) == .*', t):
    print(m.group(0).strip())
print("=== par counts ===")
for m in re.finditer(r'== 7[5-9] \\|== 7[5-9],|par_sec\.count\("assert pf\.N1_BANDS\["\) == \d+|par_full\.count\("assert pf\.N1_BANDS\["\) == \d+|_w220_block = \d+ rows', t):
    print(m.group(0).strip())
print("=== estate ws ===")
for m in re.finditer(r'\[int\(_estate_ws\[\d+\]\)[^\]]*\] == \[[\d, ]+\]', t):
    print(m.group(0).strip())
print("=== r-window tokens ===")
for m in re.finditer(r'r9\d\d (?:freeze|finalize|seat|window|probe|absorb)[^"\n]{0,50}', t):
    print(m.group(0).strip())
print("=== finalize stamps ===")
for m in re.finditer(r'1[012]:\dx[^"\n]{0,30}', t):
    print(m.group(0).strip())
print("=== stair ordinals ===")
for m in re.finditer(r'EIGHT[IY]+[^"\n;]{0,40}|TWO HUNDRED[^"\n]{0,40}|forty-\w+|fifti\w+|fifty-\w+', t):
    print(m.group(0).strip())
