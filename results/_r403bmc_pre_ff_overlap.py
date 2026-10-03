# -*- coding: utf-8 -*-
"""r403 bm-c pre-FF overlap analysis: local dirty faces vs incoming origin changes."""
import subprocess
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'


def g(args):
    r = subprocess.run(['git'] + args, capture_output=True, cwd=REPO,
                       text=True, encoding='utf-8', errors='replace',
                       creationflags=0x08000000)
    return r.returncode, r.stdout, r.stderr


rc, out, _ = g(['status', '--porcelain'])
if rc != 0:
    sys.exit('status rc=%d' % rc)
local = []
for line in out.splitlines():
    if not line.strip():
        continue
    st = line[:2].strip()
    p = line[3:].strip().strip('"')
    local.append((st, p))

rc, out2, _ = g(['diff', '--name-only', 'HEAD', 'origin/main'])
incoming = set(x.strip() for x in out2.splitlines() if x.strip())
mod_local = {p for st, p in local if st in ('M', 'D', 'MM', 'MD')}
overlap = sorted(mod_local & incoming)
untracked = {p for st, p in local if st == '??'}
untracked_hit = sorted(untracked & incoming)

print('local_dirty=%d incoming=%d overlap_tracked=%d untracked_hit=%d'
      % (len(mod_local), len(incoming), len(overlap), len(untracked_hit)))
for x in overlap:
    print('OVERLAP', x)
for x in untracked_hit:
    print('UNTRACKED_HIT', x)
print('incoming files:')
for x in sorted(incoming):
    print('IN', x)
