# -*- coding: utf-8 -*-
# r1017 bm-a: W245 vs W244 editor face-block shape probe (read-only)
import io
t245 = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8').read()
t244 = io.open('results/_w244bma_freeze_edits.py', encoding='utf-8').read()
pats = ['hops_B") == 0', 'hops_B") == 1', 'B_naive_hops") == 0', 'B_naive_hops") == 1',
        'B_honest_forward_hop_expected_face', 'B_double_clean_expected_face',
        'B_no_ownA_jump', 'B_hop_lands_inside_A', 'A_clean_at_naive_start']
print('pattern counts (245ed / 244ed):')
for p in pats:
    print('  %-42r 245=%d 244=%d' % (p, t245.count(p), t244.count(p)))
lines = t245.splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith('# W245 FACE'))
print()
print('W245 editor a2 region lines %d..%d:' % (start, start + 41))
for i in range(start, min(start + 42, len(lines))):
    print('%d: %s' % (i, lines[i][:135]))
