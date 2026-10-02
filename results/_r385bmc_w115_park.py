# -*- coding: utf-8 -*-
# r385 bm-c: W115 PARK per O-20261002-2115 supply-priority (N1 deprioritized; engine firepower -> new faces)
# Steps: fetch -> HEAD vs origin check for 3 faces -> capture parked diff -> restore from origin/main -> verify
import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NW = 0x08000000
FACES = ['research/PERPETUAL_FACES.md', 'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py']

def g(args):
    r = subprocess.run(['git'] + args, capture_output=True, creationflags=NW)
    return r.returncode, r.stdout, r.stderr

rc, o, e = g(['fetch', 'origin'])
print('fetch rc=%d' % rc)

rc, o, e = g(['diff', '--stat', 'HEAD', 'origin/main', '--'] + FACES)
print('HEAD_vs_origin_3faces: %r' % o.decode('utf-8', 'replace').strip()[:300])

rc, o, e = g(['diff', 'HEAD', '--'] + FACES)
open('results/_r385bmc_w115_parked.diff', 'wb').write(o)
print('parked diff bytes=%d' % len(o))

rc, o, e = g(['diff', 'HEAD', '--', 'state-bm-c.json'])
print('=== state-bm-c.json worktree-vs-HEAD diff (first 1200 chars) ===')
print(o.decode('utf-8', 'replace')[:1200])

rc, o, e = g(['restore', '--source=origin/main', '--'] + FACES)
print('restore rc=%d %s' % (rc, e.decode('utf-8', 'replace')[:200]))

rc, o, e = g(['status', '--porcelain', '--'] + FACES)
print('post-restore status 3faces: %r' % o.decode().strip())
