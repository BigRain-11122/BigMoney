src = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
off = 17135
line = src.count('\n', 0, off) + 1
print('byte offset', off, '=> line', line)
lines = src.splitlines()
for i in range(max(0, line - 25), min(len(lines), line + 8)):
    print(i + 1, ':', lines[i])
