"""r1038 bm-a: watermark_red.json UU newer-wins resolver (r1028 recipe).

Both sides are machine probe writes; the face is a shared regenerable probe
(dropped-probe-heartbeat). Resolve = compare the top-level ts field,
take the newer side whole (zero data loss -- the next watchdog/probe write
regenerates the face anyway).
"""
import json
import re
import subprocess
import io

G = r'C:\Program Files\Git\cmd\git.exe'
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
path = 'results/watermark_red.json'


def side(rev):
    r = subprocess.run([G, '-C', REPO, 'show', f'{rev}:{path}'],
                       capture_output=True)
    return r.stdout.decode('utf-8', 'replace')


ours = side('HEAD')      # during rebase: HEAD = the commit being replayed onto (origin side pre-image? verify)
# In a rebase, "ours" = the branch being rebased ONTO (upstream/origin), "theirs" = the commit being replayed (ours original).
# For this absorb commit replay: 'theirs' = my local absorb (bm-a write), 'ours' = origin side (bm-c r1069 write).
theirs = side('REBASE_HEAD') if True else None
up = side('HEAD')
my = theirs


def ts_of(t):
    m = re.search(r'"ts"\s*:\s*"([^"]+)"', t)
    return m.group(1) if m else ''


ts_up, ts_my = ts_of(up), ts_of(my)
newer = my if ts_my >= ts_up else up
who = 'absorb-side (bm-a write)' if ts_my >= ts_up else 'origin-side (peer write)'
io.open(REPO + '/' + path, 'w', encoding='utf-8', newline='').write(newer)
json.loads(newer)  # sanity
print(json.dumps({'ts_origin_side': ts_up, 'ts_absorb_side': ts_my,
                  'winner': who}, indent=1))
