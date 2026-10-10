"""r827 bm-b E7 pre-write probe: GRID cells roster, core48 roster, ETF list source shape."""
import json, os, re

# 1) GRID cell codes from grid_paper.py
src = open('scripts/grid_paper.py', encoding='utf-8').read()
hits = set(re.findall(r'\b(1[05]\d{4}|51\d{4}|58\d{4}|56\d{4}|159\d{3})\b', src))
print('grid_paper code-like tokens:', sorted(hits)[:30])
for line in src.splitlines():
    if 'CELLS' in line and '=' in line and not line.strip().startswith('#'):
        print('CELLS line:', line.strip()[:180])

# 2) core48 roster file
for cand in ['data/core48.csv', 'data/core48.json', 'results/core48.json',
             'scripts/etf_ops_bp1.py', 'research/etf_ops']:
    print(cand, 'exists=', os.path.exists(cand))
if os.path.exists('research/etf_ops'):
    print('etf_ops dir:', os.listdir('research/etf_ops')[:15])

# 3) core48 definition search across scripts
import glob
for f in glob.glob('scripts/*.py'):
    s = open(f, encoding='utf-8', errors='replace').read()
    if 'core48' in s.lower() and ('CORE48' in s or 'core48 =' in s or 'CORE_48' in s):
        for line in s.splitlines():
            if 'CORE48' in line or 'core48 =' in line or 'CORE_48' in line:
                print(f.split(chr(92))[-1], '->', line.strip()[:150])
                break
