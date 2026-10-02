import json, sys
sys.path.insert(0, '.')
src = open('scripts/science_gates.py', encoding='utf-8').read()
i = src.find('def ledger_head')
j = src.find('\ndef ', i + 10)
print(src[i:j])
print('=' * 60)
# where do blocks live? find append_ledger body
i2 = src.find('def append_ledger')
j2 = src.find('\ndef ', i2 + 10)
print(src[i2:j2][:3000])
