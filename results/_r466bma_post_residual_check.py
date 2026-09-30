import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
lines = draft.splitlines()
checks = [
    ('w12_screen_survivors', 2), ('w12_judge_products', 2),
    ('w12_screen_survivor', 1), ('w12_judged', 1),
    ('w13_screen_survivors', 1), ('w13_judge_products', 1),
    ('W13-NULL-0000', 2), ('run_candidate_curve_w13', 14),
    ('csv_cols_screen_w13', 6), ('_excluded_w13', 1),
    ('tl12.build_grammar_w12', 2),
]
bad = 0
for pat, want in checks:
    n = draft.count(pat)
    flag = 'OK ' if n == want else ('!! ' if n > 0 else 'XX ')
    if n != want: bad += 1
    print('%s %-28s %d (want %d)' % (flag, pat, n, want))
print()
# leftover _w12-suffixed identifiers (excluding tl12.*_w12 guard-reverted)
left = []
for i, l in enumerate(lines):
    for m in re.finditer(r'(?<!tl12\.)(?<![A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*_w12\b', l):
        if 'tl12.' + m.group(0).replace('_w12', '_w12') in l:
            continue
        left.append((i + 1, m.group(0)))
print('leftover _w12 identifiers (non-tl12):')
for ln, t in left[:12]:
    print('  %5d %s | %s' % (ln, t, lines[ln - 1].strip()[:90]))
print('count:', len(left))
print()
print('w12_ prefixed occurrences remaining:')
for i, l in enumerate(lines):
    if re.search(r'\bw12_[a-z]', l):
        print('  %5d %s' % (i + 1, l.strip()[:110]))
print()
print('trial_labor_w12 non-import refs:')
for i, l in enumerate(lines):
    if 'trial_labor_w12' in l and not l.strip().startswith('import'):
        print('  %5d %s' % (i + 1, l.strip()[:110]))
print()
print('20321000/20321500/20320500 remaining:')
for i, l in enumerate(lines):
    if re.search(r'2032[01]500|20320500', l):
        print('  %5d %s' % (i + 1, l.strip()[:110]))
