import subprocess, json, sys, io

GIT = r'C:\Program Files\Git\cmd\git.exe'
FACES = ['results/saturation_engine/face_bm-b.json',
         'results/saturation_engine/history_bm-b.jsonl',
         'results/saturation_engine/state_bm-b.json']
MARKERS = ('<<<<<<<', '=======' + chr(10), '>>>>>>>')


def run(args, check=True):
    r = subprocess.run([GIT] + args, capture_output=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        print('GIT FAIL', args, (r.stderr or '')[:200])
        sys.exit(2)
    return r.stdout


def stage_shas(path):
    d = {}
    for line in run(['ls-files', '-u', '--', path]).strip().splitlines():
        p = line.split()
        d[int(p[2])] = p[1]
    return d


def blob_raw(path, stage):
    shas = stage_shas(path)
    if stage not in shas:
        print(f'MISSING stage {stage} for {path}')
        sys.exit(2)
    r = subprocess.run([GIT, 'cat-file', '-p', shas[stage]], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace')


def wt_clean(path):
    try:
        txt = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        return None
    for m in MARKERS:
        if m in txt:
            return None
    return txt


def find_ts(j):
    hits = []

    def walk(o, depth=0):
        if depth > 3 or not isinstance(o, dict):
            return
        for k, v in o.items():
            kl = str(k).lower()
            if isinstance(v, str) and ('ts' in kl or 'time' in kl or 'updated' in kl or 'generated' in kl) and len(v) >= 8:
                hits.append(v)
            elif isinstance(v, dict):
                walk(v, depth + 1)
    walk(j)
    return hits[0] if hits else ''


for p in FACES:
    s2, s3 = blob_raw(p, 2), blob_raw(p, 3)
    wt = wt_clean(p)
    if p.endswith('.jsonl'):
        lines, seen = [], set()
        for src, tag in ((wt, 'wt'), (s2, 'st2'), (s3, 'st3')):
            if not src:
                continue
            for ln in src.splitlines():
                if ln.strip() and ln not in seen:
                    seen.add(ln)
                    lines.append(ln)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'{p}: line-union wt={0 if wt is None else len(wt.splitlines())} st2={len(s2.splitlines())} st3={len(s3.splitlines())} -> {len(lines)}')
    else:
        try:
            j2, j3 = json.loads(s2), json.loads(s3)
        except Exception as e:
            print(f'{p}: STAGE PARSE FAIL {type(e).__name__}')
            sys.exit(2)
        cands = []
        if wt is not None:
            try:
                jw = json.loads(wt)
                cands.append(('wt', find_ts(jw), jw))
            except Exception:
                pass
        cands.append(('st2', find_ts(j2), j2))
        cands.append(('st3', find_ts(j3), j3))
        cands.sort(key=lambda c: c[1], reverse=True)
        side, ts, winner = cands[0]
        with open(p, 'w', encoding='utf-8', newline='') as f:
            json.dump(winner, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'{p}: newest-wins side={side} ts={ts} (wt_clean={wt is not None})')

for p in FACES:
    txt = open(p, encoding='utf-8').read()
    for m in MARKERS:
        if m in txt:
            print('MARKER PRESENT', p, m)
            sys.exit(2)
print('SATENGINE RESOLVE OK: 3 own-lane faces written clean')
