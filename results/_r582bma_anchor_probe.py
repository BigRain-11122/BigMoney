# -*- coding: utf-8 -*-
# r582 bm-a: anchor probe for W98 freeze generator (repr probe law r581)
t = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')
eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
print('pf eol:', repr(eol))
i = t.find('    97: {"a": (237_004')
print('PF W97 ROW+TAIL:'); print(repr(t[i:i+240]))
t2 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
eol2 = '\r\n' if t2.count('\r\n') * 2 > t2.count('\n') else '\n'
print('n1 eol:', repr(eol2))
j = t2.find('"shard_subdir": "n1_w97"')
print('N1 W97 ENTRY TAIL:'); print(repr(t2[j - 60:j + 200]))
k = t2.find('law sec.4 W97 row')
print('SUMMARY ANCHOR:'); print(repr(t2[k - 60:k + 130]))
m = t2.find('        _set_wave(2)\r\n    # --- T-141 s2 lane face')
print('LEG3 ANCHOR count:', t2.count(m and t2[m:m+80]) if m >= 0 else 'N/A')
print('LEG3 ANCHOR:'); print(repr(t2[m:m+150]) if m >= 0 else 'NOT FOUND with this exact byte string')
t4 = open('research/PERPETUAL_FACES.md', 'rb').read().decode('utf-8')
eol4 = '\r\n' if t4.count('\r\n') * 2 > t4.count('\n') else '\n'
print('canon eol:', repr(eol4))
a4 = '\n- 每波 finalize 后：`science_gates.append_ledger` 落行'
print('CANON ANCHOR count:', t4.count(a4.replace('\n', eol4)))
