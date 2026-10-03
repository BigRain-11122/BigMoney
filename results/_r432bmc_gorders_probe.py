# -*- coding: utf-8 -*-
"""r432 bm-c GORDERS probe: group-tree docs/orders.md raw-blob SHA-1 vs state
watermark last_orders_sha (D-20260930-13 family, zero tree touch, r640
python-direct-read law)."""
import hashlib
import json
import os
import re
import subprocess
import sys

CREATE = 0x08000000
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(REPO, '..', '..'))


def git(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True,
                       creationflags=CREATE, cwd=GROUP)
    assert p.returncode == 0, (a, p.stderr.decode('utf-8', 'replace')[:200])
    return p.stdout


def main():
    git('fetch', 'origin')
    blob = git('show', 'origin/main:docs/orders.md')
    sha = hashlib.sha1(blob).hexdigest().upper()
    st = json.load(open(os.path.join(REPO, 'state-bm-c.json'), encoding='utf-8-sig'))
    prev = (st.get('last_orders_sha') or '').upper()
    verdict = 'MATCH' if sha == prev else 'CHANGED'
    print('GORDERS prev=%s now=%s -> %s' % (prev[:12], sha[:12], verdict))
    if verdict == 'CHANGED':
        for ln in blob.decode('utf-8', 'replace').splitlines():
            if re.search(r'BigMoney|bigmoney|quant|bm-[abc]', ln, re.I):
                print('KW:', ln[:200])
    return 0


if __name__ == '__main__':
    sys.exit(main())
