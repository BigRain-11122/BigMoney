import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
for pat in ['survivors (generate-time)', 'THIRTEENTH source', 'TWELFTH source',
            'W12-JUDGE landed', 'W11-JUDGE landed']:
    hits = [m.start() for m in re.finditer(re.escape(pat), draft)]
    print(repr(pat), '->', len(hits))
    for h in hits[:3]:
        print('   ...', repr(draft[max(0, h-200):h+220]))
