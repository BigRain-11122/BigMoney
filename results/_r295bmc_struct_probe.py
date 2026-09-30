import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for f in ['scripts/cross_start_robustness.py', 'scripts/exclusion_marginal_scan.py']:
    t = open(f, encoding='utf-8', errors='replace').read().splitlines()
    print('==', f, len(t), 'lines')
    for i, l in enumerate(t):
        s = l.strip()
        if s.startswith('def ') or s.startswith('class ') or s.startswith('if __name__'):
            print(f'{i+1}: {s[:110]}')
        elif ('for ' in s[:40]) and ('cell' in s or 'start' in s):
            print(f'{i+1}:   LOOP: {s[:110]}')
