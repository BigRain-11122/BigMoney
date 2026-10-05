import re

for f in ['scripts/fund_quality_p1.py', 'scripts/fund_value_p1.py', 'scripts/fund_divlowvol_p1.py']:
    src = open(f, encoding='utf-8').read()
    lines = src.splitlines()
    print('==', f)
    for i, l in enumerate(lines):
        s = l.strip()
        if re.search(r'digest', s, re.I) and ('def ' in s or ('=' in s and 'DIGEST' in s.upper())):
            print('  def/const', i + 1, ':', s[:110])
        elif re.search(r'digest', s, re.I) and 'def ' not in s and not s.startswith('#') and not s.startswith('"'):
            print('  use', i + 1, ':', s[:110])
