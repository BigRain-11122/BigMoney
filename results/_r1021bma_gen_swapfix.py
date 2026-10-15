import io
p = 'results/_r1020bma_w247_gen.py'
raw = io.open(p, encoding='utf-8', newline='').read()
lines = raw.split('\n')
i_short = None
for i, l in enumerate(lines):
    if '("derived by the bm-a r1016 window", "derived by the bm-a r1019 window"),' in l:
        i_short = i
        break
assert i_short is not None, 'short entry not found'
assert 'prereg derived by the bm-a r1016 window' in lines[i_short + 1], lines[i_short + 1]
assert 'prereg derived by the bm-a r1019 window' in lines[i_short + 2], lines[i_short + 2]
new = lines[:i_short] + [lines[i_short + 1], lines[i_short + 2], lines[i_short]] + lines[i_short + 3:]
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(new))
print('swapped OK: short entry moved after long entry (idx %d)' % i_short)
