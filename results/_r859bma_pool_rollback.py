import json, subprocess

# 1. capture the exact entry the submit wrote (semantic content)
d = json.load(open(r'results/runnable_pool.json', encoding='utf-8'))
entry = next(e for e in d['entries'] if e.get('id') == 'TRIAL-LABOR-W16-SCREEN')
json.dump(entry, open(r'results/_r859bma_w16_entry.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 2. rollback the submit's escape-churn write
r = subprocess.run(['git', 'checkout', '--', 'results/runnable_pool.json'])
print('rollback rc:', r.returncode)

# 3. verify: 406 entries, raw CJK restored
d2 = json.load(open(r'results/runnable_pool.json', encoding='utf-8'))
print('entries after rollback:', len(d2['entries']))
raw = open(r'results/runnable_pool.json', 'rb').read()
print('has-raw-CJK law_ref:', '\u6267\u884c'.encode('utf-8') in raw)
print('has-escape-form:', b'\\u6267' in raw)
