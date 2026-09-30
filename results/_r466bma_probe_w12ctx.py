import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
lines = draft.splitlines()
def ctx(pat, n=3):
    print('=== %r -> %d' % (pat, draft.count(pat)))
    for i, l in enumerate(lines):
        if pat in l:
            print('  %5d: %s' % (i+1, l.strip()[:118]))
            n -= 1
            if n <= 0: break
ctx('w12_gen')
ctx('w12_unc')
ctx('w12_scrnull')
ctx('trial_labor_w12')
ids = sorted(set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*_w12\b', draft)))
print('=== _w12-suffixed identifiers:', ids)
