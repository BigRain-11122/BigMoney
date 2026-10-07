# r805 bm-b rebase tail-window surgical resolver (corrects r804 draft: deep-ts fact-find)
# Facts: face/state disk ts=13:55:05 (LIVE daemon, alive+idle) > st2 13:45:05 > st3 13:44:04
#   => tailface draft's verbatim-st3 recipe would REWIND live faces (r620 live-wins violated).
# Recipes (r642/r620/r825/r678 bloodline):
#   state/face: DISK live-wins verbatim (marker-free, json-valid, freshest ts).
#   history jsonl: line-union(st2, st3) + disk non-marker payload catch-all; ts-sort; no line lost.
#   pool_red_flags: line-union(fc367a58e, 2380d6730) clean git sources (heals marker pollution
#     committed at 090b6d877 via rebase-continue bypassing pre-commit claw).
# Tolerant validation only (r419 assertion-layer family): count non-strict lines, never abort mid-script.
import subprocess, json, sys, io

def blob(sha):
    return subprocess.run(['git','cat-file','-p',sha],capture_output=True).stdout

def show(rev, path):
    r = subprocess.run(['git','show',rev+':'+path], capture_output=True)
    if r.returncode != 0:
        print('SHOW FAIL', rev, path, r.stderr.decode('utf-8','replace')[:200]); sys.exit(2)
    return r.stdout

def stages_of(path):
    out = subprocess.run(['git','ls-files','-u','--',path],capture_output=True,text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip(): continue
        meta, _, fp = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 3: res[parts[2]] = parts[1]
    return res

def line_union(sources, ts_key='ts'):
    # sources: list of (bytes,) -> deduped lines, ts-sorted when every line carries parseable ts
    parsed = []
    for b in sources:
        for ln in b.decode('utf-8','replace').splitlines():
            if ln.strip(): parsed.append(ln)
    seen = set(); uniq = []
    for ln in parsed:
        if ln in seen: continue
        seen.add(ln); uniq.append(ln)
    def ts_of(ln):
        try:
            j = json.loads(ln)
            return j.get(ts_key) or j.get('tick_ts') or j.get('time') or ''
        except Exception:
            return None
    tss = [ts_of(ln) for ln in uniq]
    if all(t is not None for t in tss):
        order = sorted(range(len(uniq)), key=lambda i: (tss[i], i))
        return [uniq[i] for i in order], True
    return uniq, False

def write_lines(path, lines, crlf_ref):
    sep = '\r\n' if (b'\r\n' in crlf_ref) else '\n'
    with open(path, 'wb') as f:
        f.write((sep.join(lines) + sep).encode('utf-8'))

def tolerant_count(lines):
    bad = 0; dec = json.JSONDecoder()
    for ln in lines:
        s = ln.strip()
        try:
            obj, end = dec.raw_decode(s)
            if s[end:].strip(): bad += 1
        except Exception:
            bad += 1
    return bad

def marker_free(data, path):
    assert b'<<<<<<<' not in data and b'>>>>>>>' not in data and b'=======' not in data, 'marker survived: '+path

receipt = {'round':'r805','machine':'bm-b','event':'rebase tail-window surgical resolve (pick d6af69ce2; 3 satengine UU + pool_red_flags heal)','faces':{}}

# ---- 1. state/face: DISK live-wins verbatim ----
for p in ['results/saturation_engine/state_bm-b.json','results/saturation_engine/face_bm-b.json']:
    data = open(p,'rb').read()
    marker_free(data, p)
    j = json.loads(data)  # hard assert json-valid (small face files, r825 read-path)
    st = stages_of(p)
    t2 = json.loads(blob(st['2'])); t3 = json.loads(blob(st['3']))
    dts = (j.get('last_tick') or {}).get('ts') or j.get('ts') or ''
    t2s = (t2.get('last_tick') or {}).get('ts') or t2.get('ts') or ''
    t3s = (t3.get('last_tick') or {}).get('ts') or t3.get('ts') or ''
    assert dts >= t2s and dts >= t3s, 'disk not freshest for '+p
    receipt['faces'][p] = {'recipe':'disk live-wins verbatim','disk_ts':dts,'st2_ts':t2s,'st3_ts':t3s}
    print('%s: disk live-wins ts=%s (st2=%s st3=%s)' % (p.split('/')[-1], dts, t2s, t3s))

# ---- 2. history jsonl: union(st2, st3) + disk payload catch-all ----
p = 'results/saturation_engine/history_bm-b.jsonl'
st = stages_of(p)
b2, b3 = blob(st['2']), blob(st['3'])
assert b'<<<<<<<' not in b2 and b'<<<<<<<' not in b3, 'marker in history git sources'
disk = open(p,'rb').read()
disk_payload = [ln for ln in disk.decode('utf-8','replace').splitlines()
                if ln.strip() and not ln.startswith(('<<<<<<<','=======','>>>>>>>'))]
lines, sorted_by_ts = line_union([b2, b3, '\n'.join(disk_payload).encode('utf-8')])
set2 = set(l for l in b2.decode('utf-8','replace').splitlines() if l.strip())
set3 = set(l for l in b3.decode('utf-8','replace').splitlines() if l.strip())
uset = set(lines)
assert set2 <= uset and set3 <= uset, 'history union lost lines'
for dl in disk_payload:
    assert dl in uset, 'disk live line lost: '+dl[:80]
bad = tolerant_count(lines)
write_lines(p, lines, b2)
back = open(p,'rb').read(); marker_free(back, p)
receipt['faces'][p] = {'recipe':'3-source line-union (st2+st3+disk payload)','st2_lines':len(set2),'st3_lines':len(set3),
                       'union':len(lines),'ts_sorted':sorted_by_ts,'non_strict':bad}
print('history union: st2=%d st3=%d disk_payload=%d -> %d lines (ts_sorted=%s, nonstrict=%d)' % (len(set2),len(set3),len(disk_payload),len(lines),sorted_by_ts,bad))

# ---- 3. pool_red_flags heal: union(fc367a58e, 2380d6730) ----
p = 'results/pool_red_flags.jsonl'
b2 = show('fc367a58e', p); b3 = show('2380d6730', p)
assert b'<<<<<<<' not in b2 and b'<<<<<<<' not in b3, 'marker in pool_red_flags git sources'
lines, sorted_by_ts = line_union([b2, b3])
set2 = set(l for l in b2.decode('utf-8','replace').splitlines() if l.strip())
set3 = set(l for l in b3.decode('utf-8','replace').splitlines() if l.strip())
uset = set(lines)
assert set2 <= uset and set3 <= uset, 'pool union lost lines'
bad = tolerant_count(lines)
write_lines(p, lines, b2)
back = open(p,'rb').read(); marker_free(back, p)
receipt['faces'][p] = {'recipe':'git-source line-union heal (heals 090b6d877 marker pollution committed via rebase-continue claw bypass)',
                       'fc367_lines':len(set2),'r804_lines':len(set3),'union':len(lines),'ts_sorted':sorted_by_ts,'non_strict':bad}
print('pool_red_flags heal union: fc367=%d r804=%d -> %d lines (nonstrict=%d)' % (len(set2),len(set3),len(lines),bad))

# ---- 4. stage everything + evidence chain ----
RESOLVED = ['results/saturation_engine/state_bm-b.json','results/saturation_engine/face_bm-b.json',
            'results/saturation_engine/history_bm-b.jsonl','results/pool_red_flags.jsonl']
EVIDENCE = ['results/_r804bmb_generic_resolve.py','results/_r804bmb_tailface_resolve.py',
            'results/_r805bmb_rebase_tail_resolve.py']
with io.open('results/_r805bmb_rebase_tail_resolve.json','w',encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
r = subprocess.run(['git','add','--'] + RESOLVED + EVIDENCE + ['results/_r805bmb_rebase_tail_resolve.json'],
                   capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr); sys.exit(3)
print('staged: %d resolved + %d evidence + receipt' % (len(RESOLVED), len(EVIDENCE)))
print('RESOLVE_OK')
