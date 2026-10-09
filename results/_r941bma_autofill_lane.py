# r941 autofill lane resolve: R31 owner authority (bm-a owns this lane file) -> live-wins newest side,
# with launches superset safety check (mixed-dict+ledger form, skill table r203 family).
import subprocess, json, io, os, re

GIT = r'C:\Program Files\Git\cmd\git.exe'
PATH_ = 'results/autofill_state.bm-a.json'
TSVAL_RE = re.compile(r'^20\d{2}-')
WALLCLOCK_RE = re.compile(r'[T ]\d{2}:\d{2}')

def git_bytes(*a):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    return r.stdout if r.returncode == 0 else None

def blob_ts(obj):
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and TSVAL_RE.match(v) and WALLCLOCK_RE.search(v):
                    if best is None or v > best:
                        best = v
                if isinstance(v, str) and TSVAL_RE.match(v) and not WALLCLOCK_RE.search(v):
                    pass
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

cands = {}
for label, raw in [(':2:', git_bytes('cat-file', 'blob', ':2:' + PATH_)),
                   (':3:', git_bytes('cat-file', 'blob', ':3:' + PATH_)),
                   ('worktree', io.open(PATH_, 'rb').read() if os.path.exists(PATH_) else None)]:
    if raw is None:
        continue
    try:
        obj = json.loads(raw.decode('utf-8', 'replace'))
        cands[label] = (obj, raw, blob_ts(obj))
    except Exception:
        cands[label] = ('INVALID', raw, None)

valid = {k: v for k, v in cands.items() if v[0] != 'INVALID'}
assert valid, 'no valid candidate'
tsmap = {k: v[2] for k, v in valid.items() if v[2]}
chosen = max(tsmap, key=tsmap.get) if tsmap else (':3:' if ':3:' in valid else ':2:')
chosen_obj = valid[chosen][0]

# launches superset safety: chosen must contain every launch key of the other sides
def launch_keys(obj):
    out = set()
    if isinstance(obj, dict):
        L = obj.get('launches')
        if isinstance(L, list):
            for e in L:
                out.add(json.dumps(e, sort_keys=True, ensure_ascii=False))
    return out

ck = launch_keys(chosen_obj)
lost = {}
for k, v in valid.items():
    if k == chosen:
        continue
    lk = launch_keys(v[0])
    miss = lk - ck
    if miss:
        lost[k] = len(miss)
if lost:
    raise SystemExit('LAUNCH LOSS DETECTED vs %s -> do not take-new blindly, escalate to union' % lost)

raw = valid[chosen][1]
with io.open(PATH_, 'wb') as f:
    f.write(raw)
rec = {'path': PATH_, 'recipe': 'R31-owner-lane-live-wins', 'side': chosen,
       'ts': {k: v[2] for k, v in cands.items()}, 'launch_count': len(ck)}
with io.open('results/_r941bma_autofill_lane.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(rec, f, ensure_ascii=False, indent=1)
print('autofill lane ->', chosen, 'ts=', rec['ts'], 'launches=', len(ck))
