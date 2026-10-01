lines = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read().splitlines()
for target in ['2: {"batch"', '55: {"batch"', '56: {"batch"', '57: {"batch"']:
    for i, l in enumerate(lines):
        if target in l:
            print(repr(l[:60]), 'indent=', len(l) - len(l.lstrip()))
            break
