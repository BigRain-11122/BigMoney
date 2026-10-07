import hashlib, subprocess, json, re

txt = subprocess.run(['git', '-C', 'C:/Users/sjs20/Desktop/FluxGroup', 'show', 'origin/main:docs/decisions.md'], capture_output=True).stdout
print('decisions sha256[:16]:', hashlib.sha256(txt).hexdigest()[:16].upper())

raw = open(r'fleet\machines\bm-a.json', encoding='utf-8').read()
h = json.loads(raw)
print('heartbeat keys:', sorted(h.keys()))
m = re.search(r'last_decisions_sha["\':\s]+([0-9A-Fa-f]+)', raw)
print('heartbeat last_decisions_sha:', m.group(1) if m else '(none found)')

txt2 = subprocess.run(['git', '-C', 'C:/Users/sjs20/Desktop/FluxGroup', 'show', 'origin/main:docs/orders.md'], capture_output=True).stdout
print('orders.md size:', len(txt2))
