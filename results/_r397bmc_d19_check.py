# -*- coding: utf-8 -*-
# r397 bm-c D-19 decisions fresh-read check (D-20260930-19: origin show, zero tree touch)
import subprocess, hashlib, sys
G = r'K:\Fluxgroup\FluxGroup'
NW = 0x08000000
KNOWN = '4167B7841A5B2B889FA8F8D27B81286FAAE39B340E786609998431EE6FD46D26'
r = subprocess.run(['git', '-C', G, 'fetch', 'origin'], capture_output=True, creationflags=NW)
print('group fetch rc=%d %s' % (r.returncode, (r.stderr or b'').decode('utf-8', 'replace')[:120]))
r = subprocess.run(['git', '-C', G, 'show', 'origin/main:docs/decisions.md'], capture_output=True, creationflags=NW)
if r.returncode != 0:
    print('SHOW_FAIL ' + r.stderr.decode('utf-8', 'replace')[:200])
    sys.exit(2)
h = hashlib.sha256(r.stdout).hexdigest().upper()
print('DECISIONS_SHA ' + h)
print('SAME' if h == KNOWN else 'CHANGED bytes=%d' % len(r.stdout))
if h != KNOWN:
    txt = r.stdout.decode('utf-8', 'replace')
    lines = txt.splitlines()
    print('--- tail 60 lines ---')
    for ln in lines[-60:]:
        print(ln[:240])
