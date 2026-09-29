import re
src=open('scripts/trial_labor_w10.py',encoding='utf-8').read().split('\n')
for i,l in enumerate(src):
    if re.search(r'"(mom_state|amp_state|std)[_a-z]*":\s|tl1\._ST\[|"mom_state"\]|mom_state_series\(prices\)', l) and (1900<i+1<2670 or 3050<i+1<3300):
        print(f'{i+1:5d}: {l.strip()[:110]}')
