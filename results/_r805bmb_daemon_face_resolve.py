# r805 bm-b rebase daemon-face conflict resolver (reusable across picks of the same rebase)
# Faces = own-machine daemon live-faces only (r642/r620/r825/r678 lineage):
#   JSON duel faces  -> freshest CLEAN side wins (disk if marker-free, else stage blobs), internal ts duel
#   JSONL faces      -> 3-source line-union (st2 + st3 + disk non-marker payload), ts-sort when uniform
# Tolerant validation (r419 law): union line validity counted, never aborts mid-script.
# Stages re-derived per call = safe to re-run for each conflicted pick. Receipt appended per call.
import subprocess, json, sys, io, time

JSON_DUEL = ['results/saturation_engine/state_bm-b.json', 'results/saturation_engine/face_bm-b.json',
             'results/saturation_engine/p1d_gates.json'.replace('saturation_engine/', '')]
JSONL_UNION = ['results/saturation_engine/history_bm-b.jsonl', 'results/fund_divlowvol_p1/nulls.jsonl']

def blob(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

def stages_of(p):
    out = subprocess.run(['git', 'ls-files', '-u', '--', p], capture_output=True, text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

def ts_of_json(b):
    try:
        j = json.loads(b)
        for k in ('ts', 'updated', 'generated', 'date', 'generated_at'):
            v = j.get(k)
            if isinstance(v, str):
                return v
            v = (j.get('last_tick') or {}).get(k) if isinstance(j.get('last_tick'), dict) else None
            if isinstance(v, str):
                return v
        return ''
    except Exception:
        return ''

def line_ts(ln):
    try:
        j = json.loads(ln)
        for k in ('ts', 'time', 'date'):
            if isinstance(j.get(k), str):
                return j[k]
        return None
    except Exception:
        return None

receipt = {'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'), 'faces': {}}

for p in JSON_DUEL:
    st = stages_of(p)
    if not st:
        continue
    cands = {'st2': blob(st['2']), 'st3': blob(st['3'])}
    disk = open(p, 'rb').read()
    if b'<<<<<<<' not in disk:
        cands['disk'] = disk
    win_tag, win = max(cands.items(), key=lambda kv: ts_of_json(kv[1]))
    assert b'<<<<<<<' not in win and b'>>>>>>>' not in win, 'winner polluted: ' + p
    json.loads(win)
    open(p, 'wb').write(win)
    receipt['faces'][p] = {'recipe': 'freshest-clean duel', 'winner': win_tag, 'ts': ts_of_json(win)}
    print('%s <- %s (ts=%s)' % (p, win_tag, ts_of_json(win)))

for p in JSONL_UNION:
    st = stages_of(p)
    if not st:
        continue
    b2, b3 = blob(st['2']), blob(st['3'])
    assert b'<<<<<<<' not in b2 and b'<<<<<<<' not in b3, 'marker in git sources: ' + p
    disk = open(p, 'rb').read()
    dp = [ln for ln in disk.decode('utf-8', 'replace').splitlines()
          if ln.strip() and not ln.startswith(('<<<<<<<', '=======', '>>>>>>>'))]
    lines, seen = [], set()
    for src in (b2, b3, '\n'.join(dp).encode('utf-8')):
        for ln in src.decode('utf-8', 'replace').splitlines():
            if ln.strip() and ln not in seen:
                seen.add(ln)
                lines.append(ln)
    tss = [line_ts(ln) for ln in lines]
    if all(t is not None for t in tss):
        lines = [lines[i] for i in sorted(range(len(lines)), key=lambda i: (tss[i], i))]
    s2 = set(l for l in b2.decode('utf-8', 'replace').splitlines() if l.strip())
    s3 = set(l for l in b3.decode('utf-8', 'replace').splitlines() if l.strip())
    uset = set(lines)
    assert s2 <= uset and s3 <= uset, 'union lost lines: ' + p
    sep = '\r\n' if (b'\r\n' in b2) else '\n'
    open(p, 'wb').write((sep.join(lines) + sep).encode('utf-8'))
    back = open(p, 'rb').read()
    assert b'<<<<<<<' not in back and b'>>>>>>>' not in back
    bad = 0
    dec = json.JSONDecoder()
    for ln in lines:
        s = ln.strip()
        try:
            _, end = dec.raw_decode(s)
            if s[end:].strip():
                bad += 1
        except Exception:
            bad += 1
    receipt['faces'][p] = {'recipe': '3-source union', 'st2': len(s2), 'st3': len(s3),
                           'union': len(lines), 'non_strict': bad}
    print('%s union: %d+%d+disk%d -> %d (nonstrict=%d)' % (p.split('/')[-1], len(s2), len(s3), len(dp), len(lines), bad))

paths = list(receipt['faces'].keys())
if not paths:
    print('NO_CONFLICTED_FACES')
    sys.exit(0)
with io.open('results/_r805bmb_daemon_face_receipts.jsonl', 'a', encoding='utf-8') as f:
    f.write(json.dumps(receipt, ensure_ascii=False) + '\n')
r = subprocess.run(['git', 'add', '--'] + paths + ['results/_r805bmb_daemon_face_receipts.jsonl'],
                   capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr)
    sys.exit(3)
print('DAEMON_FACE_RESOLVE_OK %d faces' % len(paths))
