import json, hashlib

# 1) Raw V entry block from pool
raw = open('results/runnable_pool.json', encoding='utf-8', newline='').read()
needle = '"FUND-VALUE-P1-NULLS"'
i = raw.find(needle)
assert i > 0, "V entry not found"
j = raw.rfind('{', 0, i)
depth = 0; k = j
while k < len(raw):
    if raw[k] == '{': depth += 1
    elif raw[k] == '}':
        depth -= 1
        if depth == 0: break
    k += 1
block = raw[j:k+1]
print("=== V ENTRY RAW (%d bytes) ===" % len(block))
print(block)
print()

# 2) crash fuse sigs matching fund_value
d = json.load(open('results/crash_fuse.json', encoding='utf-8'))
print("=== FUSE active ===")
print(json.dumps(d.get('active', {}), ensure_ascii=False))
print()
print("=== FUSE sigs matching fund_value / nulls ===")
for sig, rec in d.get('sigs', {}).items():
    if 'fund_value' in sig or ('nulls' in sig and 'fund' in sig):
        print(sig, '->', json.dumps(rec, ensure_ascii=False))
print()

# 3) runner file sha16 (fuse compares code_sha256)
h = hashlib.sha256(open('scripts/fund_value_p1.py','rb').read()).hexdigest()[:16]
print("current fund_value_p1.py sha16 =", h)

# 4) pool claims dir for V
import os
for name in os.listdir('results/pool_claims'):
    if 'VALUE' in name:
        p = os.path.join('results/pool_claims', name)
        if os.path.isdir(p):
            print("claims dir:", p, "->", os.listdir(p))
        else:
            print("claims file:", p, "->", open(p, encoding='utf-8').read()[:200])
