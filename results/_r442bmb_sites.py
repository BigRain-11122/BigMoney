import re
src = open('scripts/trial_labor_w10.py', encoding='utf-8').read().split('\n')
pat = re.compile(r'mom|axis_config|thirteen|THIRTEEN')
out = []
i = 1050  # 0-based: line 1051
prev_printed = -99
while i < len(src):
    if pat.search(src[i]):
        if i - prev_printed > 1 and out:
            out.append('   ...')
        out.append(f'{i+1:5d}: {src[i]}')
        prev_printed = i
    i += 1
open('results/_r442bmb_mom_sites.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out), 'lines')
