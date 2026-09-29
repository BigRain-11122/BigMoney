import re
SRC = open('results/_r442bmb_stage3c.py', encoding='utf-8').read()
lines = SRC.split('\n')
for pat in ('"amp_meta": amp_meta, "mom_meta": mom_meta,',
            'mom meta L/D 139-bar-warmup',
            'if std_state is None:',
            'std_state = std_state_series(prices)'):
    hits = [i + 1 for i, l in enumerate(lines) if pat in l]
    print(pat[:45], '->', hits[:10])
# context of the two metas sites
for ln in [i + 1 for i, l in enumerate(lines)
           if '"amp_meta": amp_meta, "mom_meta": mom_meta,' in l][:2]:
    print(f'---- metas @ {ln}')
    for j in range(ln - 2, ln + 2):
        print(f'{j+1:5d}: {lines[j][:100]}')
# curve lazy region
for ln in [i + 1 for i, l in enumerate(lines)
           if 'if std_state is None:' in l][:3]:
    print(f'---- curvelazy @ {ln}')
    for j in range(ln - 6, ln + 2):
        print(f'{j+1:5d}: {lines[j][:100]}')
# print region
for ln in [i + 1 for i, l in enumerate(lines)
           if 'mom meta L/D' in l][:2]:
    print(f'---- print @ {ln}')
    for j in range(ln - 3, ln + 4):
        print(f'{j+1:5d}: {lines[j][:100]}')
