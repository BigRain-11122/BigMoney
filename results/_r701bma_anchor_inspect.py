# r701 anchor inspection for the W119 freeze edits (r446 probe-file law)
t = open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
i = t.find('    118: {')
print('PF118:', repr(t[i:i+150]))
i2 = t.find('}\n', i)
print('PF after row:', repr(t[i2-20:i2+40]))

t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
j = t2.find('"shard_subdir": "n1_w118"')
print('N1 anchor region:', repr(t2[j-80:j+160]))

k = t2.find('_set_wave(2)\n    # --- T-141 s2 lane face')
print('T141 anchor count:', t2.count('_set_wave(2)\n    # --- T-141 s2 lane face'))
m = t2.find('law sec.4 W118 row, r678 bm-b] "')
print('summary anchor found:', m > 0)
print('SUM ctx:', repr(t2[m-60:m+80]) if m > 0 else None)

c = open('research/PERPETUAL_FACES.md', encoding='utf-8', newline='').read()
a = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
print('canon anchor count:', c.count(a))
