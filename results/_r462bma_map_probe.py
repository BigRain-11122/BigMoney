# -*- coding: utf-8 -*-
# r462 bm-a: extract the W12 surgeon's ordered surgical operation list
# (sub1/subn anchor + what labels) as the W13 conversion map backbone.
import io, re, json

SURG = 'results/_r445bmb_w12_surgeon.py'
src = io.open(SURG, encoding='utf-8').read()
L = src.splitlines()
ops = []
pat = re.compile(r'\b(sub1|subn)\(')
cur_context = ''
for i, l in enumerate(L):
    s = l.strip()
    if s.startswith('#') and len(s) > 4 and 'sub' not in s:
        cur_context = s[:100]
    m = pat.search(l)
    if m:
        ops.append({'line': i + 1, 'ctx': cur_context, 'call': s[:160]})
print('total ops:', len(ops))
for o in ops:
    print(o['line'], '|', o['ctx'][:60], '||', o['call'][:120])
# also dump top-level function defs
print('--- defs ---')
for i, l in enumerate(L):
    if re.match(r'def \w+', l):
        print(i + 1, l.rstrip()[:100])
