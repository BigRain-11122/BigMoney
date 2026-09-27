# r334 resolver PATCH: dashboard pair take-side fix (max-scan heuristic poisoned by future scheduled-field ts "2026-09-28 09:15" = T-91 Monday auto-fire face, NOT a generation ts)
# Authoritative probe = meta.generated_at (r319 existence-first, known producer path): origin 15:48:33 < mine 15:53:10 -> take MINE both faces (pair-law R209/R330).
import subprocess, json

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0, f'git show :{stage}:{path} failed'
    return r.stdout

PJSON = 'results/dashboard_status.json'
PJS = 'results/dashboard_status.js'

bo, bm = blob(2, PJSON), blob(3, PJSON)
jo, jm = json.loads(bo), json.loads(bm)
to, tm = jo['meta']['generated_at'], jm['meta']['generated_at']
assert tm > to, f'mine {tm} not later than origin {to} -- abort'
js_m = blob(3, PJS)

with open(PJSON, 'wb') as f:
    f.write(bm)
with open(PJS, 'wb') as f:
    f.write(js_m)

# re-verify: both faces byte-identical to stage3 blob (pair-law same-side), json parses
assert open(PJSON, 'rb').read() == bm
assert open(PJS, 'rb').read() == js_m
json.loads(open(PJSON, 'rb').read().decode('utf-8'))
print(f'dashboard pair PATCHED to stage3(mine): json meta.generated_at origin={to} -> mine={tm}; js paired same-side (pair-law OK)')
