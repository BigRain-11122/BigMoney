# r941 bm-a pick-2/2 resolver: 5 daemon live-state faces, live-wins semantics (r813 take-worktree-live)
# autofill_state.bm-a.json handled separately via merge_lane_views (ALL_FACES union recipe).
# For snapshots: candidates = (:2: staged blob, :3: staged blob, worktree-if-valid-json) -> hardened deep-ts probe -> newest wins.
# For history jsonl: line-union across all three sources.
import subprocess, json, io, os, re

GIT = r'C:\Program Files\Git\cmd\git.exe'
WALLCLOCK_RE = re.compile(r'[T ]\d{2}:\d{2}')
TSVAL_RE = re.compile(r'^20\d{2}-')
KEY_RE = re.compile(r'(asof|ts$|_ts|time|updated|generated|cutoff|scan|lastrun|lastseen|as_at|_at$)')

def git_bytes(*a):
    r = subprocess.run([GIT] + list(a), capture_output=True)
    return r.stdout if r.returncode == 0 else None

def _nk(k):
    return k.replace('_', '').replace('-', '').lower()

def deep_ts(obj):
    wall, date = [], []
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = _nk(k)
                if isinstance(v, str) and TSVAL_RE.match(v):
                    if KEY_RE.search(nk) or nk.endswith('ts') or nk.endswith('at') or 'date' in nk or 'updated' in nk:
                        (wall if WALLCLOCK_RE.search(v) else date).append(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return (max(wall) if wall else None, max(date) if date else None)

def load_candidates(path):
    cands = {}
    for label, raw in [(':2:', git_bytes('cat-file', 'blob', ':2:' + path)),
                       (':3:', git_bytes('cat-file', 'blob', ':3:' + path)),
                       ('worktree', (lambda p: io.open(p, 'rb').read() if os.path.exists(p) else None)(path))]:
        if raw is None:
            continue
        try:
            obj = json.loads(raw.decode('utf-8', 'replace'))
            cands[label] = (obj, raw, deep_ts(obj))
        except Exception:
            cands[label] = ('INVALID', raw, (None, None))
    return cands

def resolve_snapshot(path, receipt):
    cands = load_candidates(path)
    valid = {k: v for k, v in cands.items() if v[0] != 'INVALID'}
    assert valid, 'no valid candidate for %s' % path
    best = None
    for idx in (0, 1):  # wall-clock bucket then date-only
        vals = {k: v[2][idx] for k, v in valid.items() if v[2][idx]}
        if vals:
            best = max(vals, key=vals.get)
            if len(set(vals.values())) > 1 or best:
                if vals and max(vals.values()) != min(vals.values()):
                    break
    if best is None:
        best = ':2:' if ':2:' in valid else sorted(valid)[0]  # tie -> :2: (r140)
    raw = valid[best][1]
    with io.open(path, 'wb') as f:
        f.write(raw)
    receipt.append({'path': path, 'recipe': 'daemon-live-wins-snapshot', 'side': best,
                    'probe': {k: [list(v[2])] for k, v in cands.items()}, 'bytes': len(raw)})

def resolve_jsonl_union(path, receipt):
    srcs = {}
    for label, raw in [(':2:', git_bytes('cat-file', 'blob', ':2:' + path)),
                       (':3:', git_bytes('cat-file', 'blob', ':3:' + path)),
                       ('worktree', (lambda p: io.open(p, 'rb').read() if os.path.exists(p) else None)(path))]:
        if raw is None:
            continue
        try:
            lines = raw.decode('utf-8', 'replace').splitlines()
            for ln in lines:
                if ln.strip():
                    json.loads(ln)
            srcs[label] = lines
        except Exception as e:
            srcs[label] = ['__INVALID__%s' % str(e)[:40]]
    order = [k for k in (':2:', ':3:', 'worktree') if k in srcs and not srcs[k][0].startswith('__INVALID__')]
    seen, out = set(), []
    for k in order:
        for ln in srcs[k]:
            if ln not in seen:
                seen.add(ln)
                out.append(ln)
    for ln in out:
        if ln.strip():
            json.loads(ln)
    nl = '\r\n' if any('\r' in l for l in srcs.get(order[0], []) if False) else '\n'
    if b'\r\n' in (git_bytes('cat-file', 'blob', ':2:' + path) or b''):
        nl = '\r\n'
    body = nl.join(out) + (nl if out else '')
    with io.open(path, 'wb') as f:
        f.write(body.encode('utf-8'))
    receipt.append({'path': path, 'recipe': 'daemon-history-line-union', 'sources': {k: len(v) for k, v in srcs.items()}, 'union_lines': len(out)})

def main():
    receipt = []
    resolve_snapshot('results/dispatcher_state.bm-a.json', receipt)
    resolve_snapshot('results/saturation_engine/face_bm-a.json', receipt)
    resolve_snapshot('results/saturation_engine/state_bm-a.json', receipt)
    resolve_jsonl_union('results/saturation_engine/history_bm-a.jsonl', receipt)
    with io.open('results/_r941bma_pick2_resolver.json', 'w', encoding='utf-8', newline='') as f:
        json.dump({'round': 'r941', 'pick': '2/2', 'files': receipt}, f, ensure_ascii=False, indent=1)
    for r in receipt:
        print(r['path'], '->', r.get('side') or r.get('union_lines'), '|', r['recipe'])

if __name__ == '__main__':
    main()
