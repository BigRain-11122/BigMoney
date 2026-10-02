# scan W95 leg for remaining split-message-after-backslash patterns
import re
s = open(r'scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = s.find('# --- W95 materializer face')
j = s.find('_set_wave(2)', i)
leg = s[i:j]
lines = leg.splitlines()
bad = []
for k in range(len(lines) - 1):
    if lines[k].rstrip().endswith('\\'):
        nxt = lines[k + 1].lstrip()
        if nxt.startswith('"') and k + 2 < len(lines):
            nxt2 = lines[k + 2].lstrip()
            if nxt2.startswith('"'):
                bad.append((k + 1, lines[k][-50:], lines[k + 1][:60]))
print('BAD_SPLIT_MESSAGES:', len(bad))
for b in bad:
    print(b)
import py_compile
try:
    py_compile.compile(r'scripts/perpetual_faces_n1.py', doraise=True)
    print('compile OK')
except py_compile.PyCompileError as e:
    print('COMPILE FAIL:', str(e)[-200:])
