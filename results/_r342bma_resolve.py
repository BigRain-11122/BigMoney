# r342 bm-a fold-landing resolver: rebase stop-1 (9a65a94a onto origin/main post bm-c r93 chain)
# Files: results/compute_audit.json (rolling-ledger union, r188/R208/r85/r334 laws)
#        research/memory-archive/202609.md (append-ledger union, both-sides-keep, R208)
# Zero-loss asserts throughout; write-back mirrors base/ours EOL+indent face (r223/r234).
import subprocess, json, sys, time, datetime

def blob(stage, path):
    r = subprocess.run(['git', 'show', stage + ':' + path], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr)
    return r.stdout

def cur(s):
    print(datetime.datetime.now().strftime('%H:%M:%S'), s)

cur('resolver start (tick-window awareness: avoid :X0:02 +/-1min git legs)')

# ---------- 1) compute_audit.json ----------
CAP = 'results/compute_audit.json'
b, o, t = blob(':1', CAP), blob(':2', CAP), blob(':3', CAP)
B, O, T = json.loads(b), json.loads(o), json.loads(t)
bh, oh, th = B['history'], O['history'], T['history']
bts = {e['ts'] for e in bh}; ots = {e['ts'] for e in oh}; tts = {e['ts'] for e in th}
assert bts <= ots and bts <= tts, 'base survival check FAILED (real row loss)'
shared_new = sorted((ots & tts) - bts)
o_only = sorted(ots - bts - tts); t_only = sorted(tts - bts - ots)
expect = len(bts) + len(shared_new) + len(o_only) + len(t_only)
cur(f'compute_audit: |base|={len(bts)} ours={len(ots)} theirs={len(tts)} '
    f'ours-only={o_only} theirs-only#={len(t_only)} shared-new={shared_new}')

# r334 law: per-face real dedup key = ts (probed; every entry has ts; no dup-ts within either side)
from collections import Counter
for lab, seq in (('ours', [e['ts'] for e in oh]), ('theirs', [e['ts'] for e in th])):
    dup = [k for k, v in Counter(seq).items() if v > 1]
    assert not dup, f'dup-ts within {lab}: {dup}'
# r322-style: shared ts entries must be content-equal (canonical); field-supplement merge if divergent
omap = {e['ts']: e for e in oh}; tmap = {e['ts']: e for e in th}
for k in sorted(ots & tts):
    if json.dumps(omap[k], sort_keys=True) != json.dumps(tmap[k], sort_keys=True):
        fo, ft = set(omap[k]), set(tmap[k])
        assert fo <= ft or ft <= fo, f'real divergence at shared ts {k}: {fo ^ ft}'
        merged = dict(omap[k]); merged.update(tmap[k])
        omap[k] = tmap[k] = merged
        cur(f'  field-supplement merge at ts {k}: +{sorted((fo | ft) - (fo & ft))}')

# union: shared/ours-only from ours face; theirs-only from theirs face
union = {}
for e in oh: union[e['ts']] = e
for e in th:
    if e['ts'] not in union: union[e['ts']] = e
assert len(union) == expect, (len(union), expect)
hist = sorted(union.values(), key=lambda e: e['ts'])
assert all(hist[i]['ts'] <= hist[i+1]['ts'] for i in range(len(hist)-1)), 'sort check'
cur(f'union history rows={len(hist)} (== |A u B|={expect})')

# latest: canonical-equal assert (both ts 17:51:55) -> take ours face verbatim
assert json.dumps(O['latest'], sort_keys=True) == json.dumps(T['latest'], sort_keys=True), 'latest divergence'
merged = {'latest': O['latest'], 'history': hist}
out = json.dumps(merged, indent=2, ensure_ascii=False).encode('utf-8').replace(b'\n', b'\r\n')
assert not out.endswith(b'\n'), 'face: base blob has no trailing newline'
json.loads(out.decode('utf-8'))  # parse-verify before write (r185)
open(CAP, 'wb').write(out)
cur(f'compute_audit written: {len(out)}B CRLF={out.count(bytes([13,10]))} rows={len(hist)}')

# ---------- 2) research/memory-archive/202609.md ----------
MD = 'research/memory-archive/202609.md'
mb, mo, mt = blob(':1', MD), blob(':2', MD), blob(':3', MD)
wf = open(MD, 'rb').read()
# working tree is autocrlf-checkout CRLF face; marker detection on \r-stripped lines, content from LF blobs
lines = [l.rstrip('\r') for l in wf.decode('utf-8').split('\n')]
i_st = [i for i, l in enumerate(lines) if l.startswith('<<<<<<< ')]
i_mid = [i for i, l in enumerate(lines) if l == '=======']
i_en = [i for i, l in enumerate(lines) if l.startswith('>>>>>>> ')]
assert len(i_st) == 1 and len(i_en) == 1 and len(i_mid) == 1, (i_st, i_mid, i_en)
a, m, z = i_st[0], i_mid[0], i_en[0]
prefix, ours_blk, theirs_blk = lines[:a], lines[a+1:m], lines[m+1:z]
cur(f'md conflict block: marker@{a+1}/{m+1}/{z+1} prefix={len(prefix)} ours={len(ours_blk)} theirs={len(theirs_blk)} '
    f'ours-head={ours_blk[0][:40]!r} theirs-head={theirs_blk[0][:40]!r}')
# strict zero-loss: stage blobs must equal prefix+blk reconstructions (conflict at EOF)
def as_lines(bx): return bx.decode('utf-8').split('\n')
mo_l, mt_l = as_lines(mo), as_lines(mt)
# prefix/ours_blk/theirs_blk taken from canonical LF blob faces (not CRLF working tree)
prefix, ours_blk, theirs_blk = mo_l[:a], mo_l[a:a+len(mo_l)-a-(1 if mo_l and mo_l[-1]=='' else 0)], []
ours_n = len(mo_l) - a - (1 if mo_l and mo_l[-1] == '' else 0)
theirs_n = z - m - 1
ours_blk = mo_l[a:a+ours_n]
theirs_blk = mt_l[a:a+theirs_n]
assert mo_l[:a] == mt_l[:a], 'prefix divergence between stage blobs'
assert ours_n == m - a - 1 and theirs_n == z - m - 1, (ours_n, m - a - 1, theirs_n, z - m - 1)
# resolution: keep BOTH appended sections, HEAD(bm-c r93 25th-batch) first, mine(26th + cont) after
res = prefix + ours_blk + theirs_blk
assert mo.endswith(b'\n') and mt.endswith(b'\n'), 'blob trailing-newline face'
res_b = ('\n'.join(res) + '\n').encode('utf-8')
# every line of both blocks preserved verbatim (membership check)
for src, lab in ((ours_blk, 'ours'), (theirs_blk, 'theirs')):
    for l in src:
        assert l in res, ('lost line', lab, l[:60])
open(MD, 'wb').write(res_b)
cur(f'md written: {len(res)} lines {len(res_b)}B (prefix+ours+theirs append-union, zero-loss)')

# ---------- 3) stage + verify ----------
for p in (CAP, MD):
    r = subprocess.run(['git', '-c', 'core.autocrlf=false', 'add', p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr)
sg = subprocess.run(['git', 'show', ':' + CAP], capture_output=True).stdout
sm = subprocess.run(['git', 'show', ':' + MD], capture_output=True).stdout
j = json.loads(sg.decode('utf-8'))
assert len(j['history']) == expect and sg.count(b'\r\n') > 0 and b'\n' != sg[-1:], 'staged compute_audit verify'
assert not any(l.startswith('<<<<<<<') or l.startswith('>>>>>>>') or l == '=======' for l in sm.decode('utf-8').split('\n')), 'staged md marker scan'
assert sm.count(b'\r\n') == 0, 'staged md EOL'
assert len(sm.decode('utf-8').split('\n')) == len(res) + 1, 'staged md line count'
cur(f'STAGED OK: compute_audit rows={len(j["history"])} CRLF face preserved; md lines={len(res)} marker-free; '
    f'still-unmerged={subprocess.run(["git","diff","--name-only","--diff-filter=U"],capture_output=True).stdout.decode().strip()!r}')
print('RESOLVER PASS')
