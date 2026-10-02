import re
src = open('scripts/science_gates.py', encoding='utf-8').read()
m = re.findall(r"[A-Z_]*LEDGER[A-Z_]*\s*=\s*['\"]([^'\"]+)['\"]", src)
print('ledger consts:', m)
m2 = re.findall(r'def append_ledger.*?(?=\ndef |\Z)', src, re.S)
print((m2[0][:800] if m2 else 'not found'))
