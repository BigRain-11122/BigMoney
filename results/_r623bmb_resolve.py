# r623 bm-b rebase conflict resolver -- 14 UU faces vs bm-a r630 same-window S6 chain
# Laws: r98/r99/r100 twin-same-side snapshot, r188/R208 rolling-ledger union zero-loss,
# r311/r100/R350 deep-scan ts probe (staged blobs), r223/r234 format mirror, r185 verify-before-write
import subprocess, json, re, io

def blob_bytes(rev, path):
    r = subprocess.run(['git', 'show', rev + ':' + path], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('blob fail %s %s: %s' % (rev, path, r.stderr[:120]))
    return r.stdout

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def deep_ts(obj, best=''):
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best:
            best = obj
    return best

def detect_format(bs):
    crlf = b'\r\n' in bs
    m = re.search(br'\n(\s+)"', bs)
    indent = len(m.group(1)) if m else 1
    return crlf, indent

def write_back(path, data, base_bs):
    crlf, indent = detect_format(base_bs)
    s = json.dumps(data, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace('\n', '\r\n')
        if not s.endswith('\r\n'):
            s += '\r\n'
    else:
        if not s.endswith('\n'):
            s += '\n'
    io.open(path, 'wb').write(s.encode('utf-8'))

def side_pair(path):
    return blob_bytes(':2', path), blob_bytes(':3', path)

def pick_snapshot(path):
    a, b = side_pair(path)
    da, db = json.loads(a), json.loads(b)
    ta, tb = deep_ts(da), deep_ts(db)
    win = 'origin' if ta >= tb else 'ours'
    data = da if win == 'origin' else db
    return data, (a if win == 'origin' else b), ta, tb, win

def row_fp(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True)

def union_ledger_rows(ra, rb):
    seen, out = set(), []
    for row in ra + rb:
        fp = row_fp(row)
        if fp not in seen:
            seen.add(fp)
            out.append(row)
    ts_key = None
    if out and isinstance(out[0], dict):
        for k in out[0].keys():
            if 'ts' in str(k).lower() and isinstance(out[0][k], str):
                ts_key = k
                break
    if ts_key:
        out.sort(key=lambda r: str(r.get(ts_key, '')))
    return out

report = []

def resolve_twin_group(json_path, md_path, label):
    data, base, ta, tb, win = pick_snapshot(json_path)
    a_md, b_md = side_pair(md_path)
    md_bytes = a_md if win == 'origin' else b_md
    write_back(json_path, data, base)
    io.open(md_path, 'wb').write(md_bytes)
    report.append('%s: %s win (json ts %s vs %s), twins same-side' % (label, win, ta, tb))

resolve_twin_group('docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md', 'REPORT twins')
for jp, mp in (('docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md'),
               ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')):
    resolve_twin_group(jp, mp, 'LIVE twins')

for p in ('results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/update_status.json', 'results/token_usage.json',
          'results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json'):
    data, base, ta, tb, win = pick_snapshot(p)
    write_back(p, data, base)
    report.append('%s: %s win (ts %s vs %s)' % (p, win, ta, tb))

a, b = side_pair('results/compute_audit.json')
da, db = json.loads(a), json.loads(b)
merged_hist = union_ledger_rows(da['history'], db['history'])
ta, tb = deep_ts(da.get('latest', {})), deep_ts(db.get('latest', {}))
latest = da['latest'] if ta >= tb else db['latest']
write_back('results/compute_audit.json', {'latest': latest, 'history': merged_hist}, a)
report.append('compute_audit.json: history union %d+%d->%d rows, latest take-new (%s vs %s)' %
              (len(da['history']), len(db['history']), len(merged_hist), ta, tb))

a, b = side_pair('results/regime_state.json')
da, db = json.loads(a), json.loads(b)
merged = dict(da)
ta, tb = str(da.get('updated', '')), str(db.get('updated', ''))
newer = db if tb >= ta else da
for k in ('updated', 'asof', 'mode', 'state', 'state_cn', 'raw_level', 'green_streak',
          'days_in_state', 'thresholds_fp', 'dims', 'triggers', 'rule'):
    if k in newer:
        merged[k] = newer[k]
merged['history'] = union_ledger_rows(da.get('history', []), db.get('history', []))
merged['transitions'] = union_ledger_rows(da.get('transitions', []), db.get('transitions', []))
write_back('results/regime_state.json', merged, a)
report.append('regime_state.json: state take-new (updated %s vs %s), history union->%d, transitions union->%d' %
              (ta, tb, len(merged['history']), len(merged['transitions'])))

paths = ['docs/daily_report/REPORT-2026-10-03.json', 'docs/daily_report/REPORT-2026-10-03.md',
         'docs/live_usage/LIVE-2026-10-03.json', 'docs/live_usage/LIVE-2026-10-03.md',
         'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
         'results/futures_update_status.json', 'results/lhb_update_status.json',
         'results/update_status.json', 'results/token_usage.json',
         'results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json',
         'results/compute_audit.json', 'results/regime_state.json']
for p in paths:
    if p.endswith('.json'):
        json.load(io.open(p, encoding='utf-8'))
for line in report:
    print('[resolve]', line)
print('ALL 14 FACES RESOLVED+VERIFIED')
