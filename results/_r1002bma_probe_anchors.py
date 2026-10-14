import io
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
anchors_n1 = ['    # --- W242 materializer face', '    # --- T-141 s2 lane face',
              '242: {"batch"', '"a_seed_base": 549501', '"b_exit_seed_base": 541204',
              'n1_w242', 'PERPETUAL-N1-W242-SHARD-0']
anchors_pf = ['    242: {"a"', '# v1 + ext(wave-1) in-use bands']
for s in anchors_n1:
    print('n1', n1.count(s), repr(s))
for s in anchors_pf:
    print('pf', pf.count(s), repr(s))
# estate structure inside the W242 block
i = n1.find('    # --- W242 materializer face')
j = n1.find('    # --- T-141 s2 lane face')
blk = n1[i:j]
import re
rows = re.findall(r'assert pf\.N1_BANDS\[(\d+)\] ==', blk)
print('W242 block row-assert waves:', rows[:5], '...', rows[-5:], 'count', len(rows))
print('EOL crlf in n1:', n1.count('\r\n') > n1.count('\n') - n1.count('\r\n'))
