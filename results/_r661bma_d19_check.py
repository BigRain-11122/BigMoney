import subprocess, hashlib, re

repo = r'C:\Users\sjs20\Desktop\FluxGroup'
txt = open(r'state-bm-a.json', 'rb').read().decode('utf-8', errors='replace')

for doc, key in [('docs/decisions.md', 'last_decisions_sha'), ('docs/orders.md', 'last_orders_sha')]:
    raw = subprocess.run(['git', '-C', repo, 'show', 'origin/main:' + doc], capture_output=True).stdout
    sha = hashlib.sha256(raw).hexdigest()
    m = re.search(r'"' + key + r'":\s*"([0-9a-f]{64})"', txt)
    wm = m.group(1) if m else 'MISSING'
    verdict = 'MATCH' if sha == wm else 'CHANGED'
    print(doc, sha[:16], 'vs', wm[:16], verdict)
    if verdict == 'CHANGED':
        for l in raw.decode('utf-8', errors='replace').splitlines()[-15:]:
            print('  |', l[:170])
