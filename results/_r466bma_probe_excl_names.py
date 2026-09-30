import re
live = open('scripts/trial_labor_w12.py', encoding='utf-8').read()
i = live.find('def _load_exclusion_rows_w12')
seg = live[i:i+4200]
for ln in seg.splitlines():
    low = ln.lower()
    if ('"w' in ln) or ('source' in low) or ('disc' in low) or ('SOURCES' in ln):
        print(ln[:135])
print('---source-name occurrences across file---')
for pat in ['w12_screen_survivors', 'w11_screen_survivors', 'w12_judge_products',
            'w11_judge_products', 'w13_screen_survivors']:
    print(pat, '->', live.count(pat))
