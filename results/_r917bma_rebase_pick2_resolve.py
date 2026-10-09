# -*- coding: utf-8 -*-
# r917 bm-a rebase pick-2 live-face resolve v2: working tree carries merge
# markers (daemon quiesced post-burn) -> resolve from stages only.
# jsonl = S2 line-union S3 (S2 already absorbed pre-rebase wt); flat = S2/S3
# newest-ts wins (r915 daemon live-face law; r910 jsonl union family).
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'
MARKERS = ('<<<<<<<', '=======', '>>>>>>>')

def show(stage, path):
    r = subprocess.run([GIT, 'show', ':%s:%s' % (stage, path)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else ''

def try_json(s):
    try:
        return json.loads(s)
    except Exception:
        return None

def ts_of(d):
    for k in ('ts', 'time', 'generated', 'updated'):
        v = (d or {}).get(k)
        if isinstance(v, str) and v:
            return v
    return ''

def resolve_jsonl(path):
    seen, union = set(), []
    for ln in (show(2, path) + '\n' + show(3, path)).splitlines():
        s = ln.strip()
        if s and s not in seen and not s.startswith(MARKERS):
            seen.add(s)
            union.append(s)
    def ts_key(s):
        return ts_of(try_json(s))
    union.sort(key=ts_key)
    open(path, 'w', encoding='utf-8', newline='').write(
        '\n'.join(union) + ('\n' if union else ''))
    print('%s: S2+S3 line-union %d lines' % (path, len(union)))

def resolve_flat(path):
    cands = []
    for stage in (2, 3):
        d = try_json(show(stage, path))
        if d:
            cands.append((ts_of(d), stage, json.dumps(d, ensure_ascii=False, indent=1) + '\n'))
    assert cands, '%s no parsable stage' % path
    best_ts, best_stage, best_txt = max(cands, key=lambda c: c[0])
    open(path, 'w', encoding='utf-8', newline='').write(best_txt)
    print('%s: stage-%d newest-ts=%s wins' % (path, best_stage, best_ts[:19]))

for p in ['results/pool_core_samples.jsonl', 'results/saturation_engine/history_bm-a.jsonl']:
    resolve_jsonl(p)
for p in ['results/saturation_engine/face_bm-a.json', 'results/saturation_engine/state_bm-a.json']:
    resolve_flat(p)

r = subprocess.run([GIT, 'add',
                    'results/pool_core_samples.jsonl',
                    'results/saturation_engine/history_bm-a.jsonl',
                    'results/saturation_engine/face_bm-a.json',
                    'results/saturation_engine/state_bm-a.json'], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:200]
print('4 live faces resolved + staged (v2)')
