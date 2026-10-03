# r663 bm-a D-19 freshness probe: raw-bytes sha256 of group-tree docs/decisions.md + docs/orders.md
# law: r209/r631/r660 -- git show origin bytes via python subprocess, no PS string translation
import subprocess, hashlib

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup'
LAST_DECISIONS_SHA = 'eb14b510d304a1d0a30175447cf9360d6bab6dc20972ceebce35d47ef8935bfa'
LAST_ORDERS_SHA = '82a0cef99f147c6f6d14a0c2233a44309768c548312f9069f7c33cf6a2aa311a'

for label, path in (('decisions', 'docs/decisions.md'), ('orders', 'docs/orders.md')):
    p = subprocess.run(['git', '-C', ROOT, 'show', 'origin/main:' + path], capture_output=True)
    if p.returncode != 0:
        print(label, 'SHOW_FAIL', p.returncode, p.stderr[:200])
        continue
    raw = p.stdout
    sha = hashlib.sha256(raw).hexdigest()
    prev = LAST_DECISIONS_SHA if label == 'decisions' else LAST_ORDERS_SHA
    verdict = 'MATCH' if sha == prev else 'CHANGED'
    print(f'{label}_sha256={sha} verdict={verdict} bytes={len(raw)}')
    if verdict == 'CHANGED':
        txt = raw.decode('utf-8', errors='replace')
        lines = txt.splitlines()
        print(f'{label}_total_lines={len(lines)}')
        # print tail 40 lines for row-level diff by eye
        print('--- tail 40 ---')
        for ln in lines[-40:]:
            print(ln)
