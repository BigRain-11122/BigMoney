import re
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
for w in (229, 230, 231, 232, 233):
    print('assert pf.N1_BANDS[%d] ==' % w, ':', t.count('assert pf.N1_BANDS[%d] ==' % w))
print('W234 materializer face:', t.count('# --- W234 materializer face'))
print('W233 materializer face:', t.count('# --- W233 materializer face'))
print('batch W234:', t.count('"batch": "PERPETUAL-N1-W234"'))
print('print W234 frag:', t.count('"+ W234 materializer face'))
print('T-141 marker:', t.count('    # --- T-141 s2 lane face'))
print('print T-141 frag:', t.count('"+ T-141 s2 '))
i = t.find('    # --- W234 materializer face')
j = t.find('    # --- T-141 s2 lane face')
blk = t[i:j]
m_first = re.search(r'assert pf\.N1_BANDS\[', blk)
m_disj = re.search(r'        # prior-wave disjointness W2\.\.W\d+ \(single state', blk)
ls = blk.rfind('\n', 0, m_first.start()) + 1
par_full = blk[ls:m_disj.start()]
ws = re.findall(r'assert pf\.N1_BANDS\[(\d+)\] ==', par_full)
print('par_full rows:', len(ws), 'last 6:', ws[-6:])
m232 = re.search(r' *assert pf\.N1_BANDS\[232\] ==', par_full)
m231 = re.search(r' *assert pf\.N1_BANDS\[231\] ==', par_full)
print('m231 at', m231.start() if m231 else None, 'm232 at', m232.start() if m232 else None)
sec = par_full[:m232.start()]
ws2 = re.findall(r'assert pf\.N1_BANDS\[(\d+)\] ==', sec)
print('par_sec rows:', len(ws2), 'last 4:', ws2[-4:], 'first 2:', ws2[:2])
print('sec ends with EOL:', sec.endswith('\n'))
print('block W234 header first 3 lines:')
for l in blk.split('\n')[:3]:
    print('  ', repr(l[:120]))
# cfg entry 234 location + PRE anchors
c234 = t.find('234: {"batch"')
print('cfg 234 at char', c234)
print('PRE_KEY anchor count:', t.count('"prereg": ("research/PERPETUAL_N1_W234_PREREG.md'))
print('cfg close anchor count:', t.count('PREREG = WAVE_CONFIGS[2]["prereg"]'))
# pf row 234 structure
pt = open('scripts/perpetual_faces.py', encoding='utf-8').read()
r234 = pt.find('    234: {"a"')
print('pf row 234 at char', r234)
line_end = pt.find('\n', r234)
print('row line:', repr(pt[r234:line_end][:130]))
next_line_end = pt.find('\n', line_end + 1)
print('owner line:', repr(pt[line_end + 1:next_line_end][:130]))
tail_after = pt[next_line_end + 1:next_line_end + 60]
print('after owner line:', repr(tail_after))
