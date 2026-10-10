import re
src = open(r'scripts\trial_labor_w16.py', encoding='utf-8').read()
i = src.find('def cmd_judge_prep')
if i < 0:
    print('no judge_prep in w16')
else:
    j = src.find('def cmd_', i + 10)
    seg = src[i:j]
    pat = re.compile(r'MIN_LISTED|_load_leg\("D"\)|leg == "D"|FROZEN_CENSUS\[leg\]|starts\[leg\]')
    for m in pat.finditer(seg):
        off = seg[:m.start()].count('\n')
        print('off', off, ':', seg.splitlines()[off].strip()[:135])
