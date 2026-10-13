import re, json, subprocess, hashlib

raw = open('state-bm-c.json', encoding='utf-8').read()
print('--- duplicate key scan (raw state file) ---')
for m in re.finditer(r'"last_orders_sha":\s*"([0-9a-f]{40})"', raw):
    print('ord key at byte', m.start(), ':', m.group(1))
for m in re.finditer(r'"last_decisions_sha":\s*"([0-9a-f]{64})"', raw):
    print('dec key at byte', m.start(), ':', m.group(1))

# Ground truth: group tree origin blob hashes
K = 'K:\\Fluxgroup\\FluxGroup'
subprocess.run(['git', '-C', K, 'fetch', 'origin'], capture_output=True)

# ORD: content-bytes sha1 per probe method pin
ord_blob = subprocess.run(['git', '-C', K, 'show', 'origin/main:docs/orders.md'],
                          capture_output=True).stdout
ord_sha = hashlib.sha1(ord_blob).hexdigest()
print('--- ground truth ---')
print('live ORD content-sha1:', ord_sha)

# DEC: raw-blob sha256 per pin
dec_blob = subprocess.run(['git', '-C', K, 'show', 'origin/main:docs/decisions.md'],
                           capture_output=True).stdout
dec_sha = hashlib.sha256(dec_blob).hexdigest()
print('live DEC raw-blob sha256:', dec_sha)

d = json.load(open('state-bm-c.json', encoding='utf-8'))
print('--- delta verdict ---')
print('ORD delta:', d['last_orders_sha'] != ord_sha, '| state:', d['last_orders_sha'][:12], '| live:', ord_sha[:12])
print('DEC delta:', d['last_decisions_sha'] != dec_sha, '| state:', d['last_decisions_sha'][:12], '| live:', dec_sha[:12])
