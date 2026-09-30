import re
live = open('scripts/trial_labor_w12.py', encoding='utf-8').read()
for pat in ['TWELFTH source', 'w11_screen.json survivors', 'w11_judge products',
            'W11-JUDGE landed', 'screen_survivor', '@@W']:
    hits = [m.start() for m in re.finditer(re.escape(pat), live)]
    print(repr(pat), '->', len(hits))
    for h in hits[:4]:
        print('   ...', repr(live[max(0, h-140):h+180]))
