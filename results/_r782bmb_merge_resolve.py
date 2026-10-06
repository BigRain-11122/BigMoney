# r782 bm-b S0 merge resolver: 22 UU + worksnap overlay (r609 blob-sha / r756 ts-normalize / r637 scoped marker scan / r781 token_usage per-key union laws)
import subprocess, json, os, re, sys

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')

def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d %s' % (a, r.returncode, r.stderr[:300].decode('utf-8', 'replace')))
    return r.stdout

def blob(ref, path):
    return git('show', '%s:%s' % (ref, path))

TS_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(\.\d+)?(\+08:00|Z)?$')
def parse_ts(v):
    if not isinstance(v, str):
        return None
    m = TS_RE.match(v.strip())
    if not m:
        return None
    import datetime
    try:
        base = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)))
    except ValueError:
        return None
    return base

def newer(a, b):
    ta, tb = parse_ts(a), parse_ts(b)
    if ta is not None and tb is not None:
        return a if ta >= tb else b   # tie -> HEAD/ours (r140)
    return None

def merge_val(a, b):
    # a=ours(HEAD), b=theirs(origin); union semantics per r781 token_usage law
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in sorted(set(a) | set(b)):
            if k in a and k in b:
                out[k] = merge_val(a[k], b[k])
            elif k in a:
                out[k] = a[k]
            else:
                out[k] = b[k]
        return out
    if isinstance(a, list) and isinstance(b, list):
        seen = set()
        out = []
        for x in b + a:
            key = json.dumps(x, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                out.append(x)
        return out
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
        return max(a, b)
    nv = newer(a, b)
    if nv is not None:
        return nv
    if isinstance(a, str) and isinstance(b, str) and a == a:
        return a
    return b  # non-ts scalar: theirs (newer round's face)

TAKE_THEIRS = [
    'docs/daily_report/REPORT-2026-10-06.json',
    'docs/daily_report/REPORT-2026-10-06.md',
    'docs/live_usage/LIVE-2026-10-06.json',
    'docs/live_usage/LIVE-2026-10-06.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/post_review/REPORT-20261006.md',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/update_status.json',
]
UNION_JSONL = ['results/post_review.jsonl']
UNION_TOK = ['results/token_usage.json']
CODELY = 'CODELY.md'

receipt = {'take_theirs': [], 'unions': {}, 'codely': {}, 'overlays': {}, 'asserts': []}

# --- leg 1: take-theirs (19) with blob-sha proof ---
for p in TAKE_THEIRS:
    theirs = blob(':3', p)
    with open(p, 'wb') as f:
        f.write(theirs)
    if p.endswith('.json'):
        json.loads(theirs.decode('utf-8'))
    receipt['take_theirs'].append(p)
git('add', '--', *TAKE_THEIRS)
for p in TAKE_THEIRS:
    st = git('ls-files', '-s', '--', p).decode().split()
    o_sha = git('rev-parse', 'origin/main:%s' % p).decode().strip()
    assert st[1] == o_sha, 'blob-sha mismatch on take-theirs: %s (%s vs %s)' % (p, st[1], o_sha)
receipt['asserts'].append('take_theirs staged blob-sha == origin/main blob-sha 19/19')

# --- leg 2: post_review.jsonl line-union + ts stable sort (r758 x2 law) ---
for p in UNION_JSONL:
    ours = blob(':2', p).decode('utf-8').splitlines()
    theirs = blob(':3', p).decode('utf-8').splitlines()
    seen = set()
    uniq = []
    for ln in ours + theirs:
        if ln not in seen and ln.strip():
            seen.add(ln)
            uniq.append(ln)
    def line_ts(ln):
        try:
            d = json.loads(ln)
            return parse_ts(d.get('ts')) or parse_ts('2000-01-01 00:00:00')
        except Exception:
            return parse_ts('2000-01-01 00:00:00')
    uniq.sort(key=line_ts)  # stable sort keeps ours-first on ties
    body = '\n'.join(uniq) + '\n'
    with open(p, 'wb') as f:
        f.write(body.encode('utf-8'))
    so, st_ = len(set(ours)), len(set(theirs))
    assert len(uniq) >= max(so, st_), 'union count regression on %s' % p
    receipt['unions'][p] = {'ours': len(ours), 'theirs': len(theirs), 'union': len(uniq)}
    git('add', '--', p)
receipt['asserts'].append('post_review.jsonl union >= max(side unique counts)')

# --- leg 3: token_usage.json per-key recursive union (r781 law) ---
for p in UNION_TOK:
    jo = json.loads(blob(':2', p).decode('utf-8'))
    jt = json.loads(blob(':3', p).decode('utf-8'))
    jm = merge_val(jo, jt)
    with open(p, 'wb') as f:
        f.write(json.dumps(jm, ensure_ascii=False, indent=1).encode('utf-8'))
    receipt['unions'][p] = {'merged_keys': sorted(jm.keys())}
    git('add', '--', p)
receipt['asserts'].append('token_usage per-key recursive union (num=max, ts=newer, tie=ours)')

# --- leg 4: CODELY.md = theirs(post-split) + ours-new not-migrated blocks ---
ours_l = blob(':2', CODELY).decode('utf-8').splitlines()
theirs_l = blob(':3', CODELY).decode('utf-8').splitlines()
pit_files = git('ls-tree', '-r', '--name-only', 'origin/main', 'research').decode().splitlines()
pit_files = [x for x in pit_files if re.search(r'pit-[a-z0-9-]+\.md$', x)]
pit_corpus = ''
for pf in pit_files:
    try:
        pit_corpus += blob('origin/main', pf).decode('utf-8', 'replace')
    except Exception:
        pass
theirs_set = set(theirs_l)
blocks = []  # (header, [lines])
cur_h, cur_b = None, []
for ln in ours_l:
    if ln in theirs_set:
        if cur_b:
            blocks.append((cur_h, cur_b))
        cur_h, cur_b = None, []
        continue
    if ln.startswith('#'):
        if cur_b:
            blocks.append((cur_h, cur_b))
        cur_h, cur_b = ln, []
        continue
    cur_b.append(ln)
if cur_b:
    blocks.append((cur_h, cur_b))
appended, migrated = 0, 0
out = list(theirs_l)
for h, b in blocks:
    b = [x for x in b if x.strip()]
    if not b:
        continue
    needle = ''
    for x in b:
        if len(x.strip()) >= 40:
            needle = x.strip()[8:68]
            break
    if needle and needle in pit_corpus:
        migrated += 1
        continue
    if h and h in theirs_l:
        idx = len(theirs_l) - 1 - theirs_l[::-1].index(h)
        nxt = len(out)
        for j in range(idx + 1, len(out)):
            if out[j].startswith('#'):
                nxt = j
                break
        out[nxt:nxt] = [''] + b
    else:
        if out and out[-1].strip():
            out.append('')
        out.extend(b)
    appended += 1
body = '\n'.join(out) + '\n'
with open(CODELY, 'wb') as f:
    f.write(body.encode('utf-8'))
receipt['codely'] = {'ours_lines': len(ours_l), 'theirs_lines': len(theirs_l), 'result_lines': len(out), 'blocks_appended': appended, 'blocks_skipped_migrated': migrated}
assert appended + migrated == len(blocks), 'block accounting mismatch'
receipt['asserts'].append('CODELY ours-unique blocks all either appended or verified-migrated-in-pit-files')
git('add', '--', CODELY)

# --- leg 5: worksnap overlays (bm-b live faces ours-live-wins, ts-gated; jsonl append-only) ---
WS = 'results/_r782bmb_s0_worksnap'
def ts_of(d, *keys):
    for k in keys:
        v = d.get(k) if isinstance(d, dict) else None
        t = parse_ts(v) if v else None
        if t is not None:
            return t
    return None
ov = []
for name, path, kind in [
    ('autofill_state.bm-b.json', 'results/autofill_state.bm-b.json', 'json-ts'),
    ('p1d_gates.json', 'results/p1d_gates.json', 'json-ts'),
    ('face_bm-b.json', 'results/saturation_engine/face_bm-b.json', 'json-ts'),
    ('state_bm-b.json', 'results/saturation_engine/state_bm-b.json', 'json-ts'),
    ('history_bm-b.jsonl', 'results/saturation_engine/history_bm-b.jsonl', 'jsonl-append'),
]:
    snap = os.path.join(WS, name)
    if not os.path.exists(snap):
        receipt['overlays'][name] = 'missing-snap'
        continue
    if kind == 'jsonl-append':
        cur = open(path, 'rb').read().decode('utf-8', 'replace').splitlines()
        snapl = open(snap, 'rb').read().decode('utf-8', 'replace').splitlines()
        missing = [x for x in snapl if x.strip() and x not in cur]
        if missing:
            with open(path, 'ab') as f:
                f.write(('\n'.join(missing) + '\n').encode('utf-8'))
        receipt['overlays'][name] = {'appended_missing': len(missing)}
        if missing:
            ov.append(path)
    else:
        try:
            ws_j = json.loads(open(snap, 'rb').read().decode('utf-8'))
            cur_j = json.loads(open(path, 'rb').read().decode('utf-8'))
        except Exception as e:
            receipt['overlays'][name] = 'parse-fail:' + str(e)[:80]
            continue
        tw = ts_of(ws_j, 'ts', 'updated', 'updated_at', 'last_tick_ts', 'generated', 'clock_read', 'asof')
        tc = ts_of(cur_j, 'ts', 'updated', 'updated_at', 'last_tick_ts', 'generated', 'clock_read', 'asof')
        if tw is not None and (tc is None or tw >= tc):
            with open(path, 'wb') as f:
                f.write(json.dumps(ws_j, ensure_ascii=False, indent=1).encode('utf-8'))
            receipt['overlays'][name] = {'overlay': 'worksnap', 'snap_ts_newer_or_equal': True}
            ov.append(path)
        else:
            receipt['overlays'][name] = {'overlay': 'kept-merged', 'snap_ts': str(tw), 'merged_ts': str(tc)}

# quality nulls worksnap append (worksnap nulls.jsonl = fund_quality copy, basename collision kept)
qn = 'results/fund_quality_p1/nulls.jsonl'
cur = open(qn, 'rb').read().decode('utf-8', 'replace').splitlines()
snapl = open(os.path.join(WS, 'nulls.jsonl'), 'rb').read().decode('utf-8', 'replace').splitlines()
missing = [x for x in snapl if x.strip() and x not in cur]
if missing:
    with open(qn, 'ab') as f:
        f.write(('\n'.join(missing) + '\n').encode('utf-8'))
receipt['overlays']['fund_quality_p1/nulls.jsonl'] = {'appended_missing': len(missing)}
if missing:
    ov.append(qn)
if ov:
    git('add', '--', *ov)

# --- leg 6: scoped marker scan on all touched files (r637: line-anchored, changed-set only) ---
touched = TAKE_THEIRS + UNION_JSONL + UNION_TOK + [CODELY] + ov
bad = []
for p in touched:
    try:
        txt = open(p, 'rb').read().decode('utf-8', 'replace')
    except Exception:
        continue
    for ln in txt.splitlines():
        if re.match(r'^(<{7}|={7}|>{7})( |$)', ln):
            bad.append((p, ln[:60]))
            break
assert not bad, 'conflict markers remain: %s' % bad
receipt['asserts'].append('line-anchored marker scan clean on %d touched files' % len(touched))

with open('results/_r782bmb_merge_resolve.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('RESOLVE-OK', json.dumps(receipt['codely']), json.dumps(receipt['unions']), 'overlay-keys:', len(receipt['overlays']))
