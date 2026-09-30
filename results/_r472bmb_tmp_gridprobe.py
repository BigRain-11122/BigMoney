import re
src = open('results/_r470bmb_vsumd_resi_w14_probe.py', encoding='utf-8').read()
# find ALL definition lines of the shared faces anywhere before grid9 calls
j = src.find('def grid9')
seg = src[:j]
pat = re.compile(r'^(\w+)\s*=\s*')
names = ('bull', 'bear', 'calm', 'wild', 'yang', 'surge', 'up_st', 'dn_st',
         'st', 'amp_known', 'mad_q10', 'dec_mad', 'rsv_low', 'dec_rsv',
         'dec_s20', 'std20_open', 'ma200', 'ma60', 'med20v', 'med20amp',
         'wide', 'judge', 'o_', 'h_', 'l_', 'v_', 'close')
seen = set()
for i, line in enumerate(seg.split('\n')):
    s = line.strip()
    m = pat.match(s)
    if m and m.group(1) in names and m.group(1) not in seen:
        seen.add(m.group(1))
        print(f"{m.group(1)} = {s[s.find('=')+1:s.find('=')+90]}")
