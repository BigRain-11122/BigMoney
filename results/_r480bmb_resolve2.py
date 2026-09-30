# r480 addendum: S7 push-reject wave-2 resolver (17 UU vs bm-c r290 same-window)
# rebase context: stage2=ours=origin/main(3159b2f74 bm-c r290), stage3=theirs=my r480 commit
# Recipes: bigmoney-conflict-resolve skill (r98/r99 twins-same-side, r188/R208 ledger union,
# R208 snapshots take-new, js-wrapper whole-blob take-new)
import subprocess, json, re, sys

def stage(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

WALLCLOCK_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def deep_ts(obj):
    best = ''
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                kk = re.sub(r'[_\-]', '', str(k).lower())
                if isinstance(v, str) and WALLCLOCK_RE.match(v):
                    if any(s in kk for s in ('ts','generated','updated','asof','stamp','time','date','cutoff','seen')) and v > best:
                        best = v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

def detect_eol(blob):
    return b'\r\n' if b'\r\n' in blob[:2000] else b'\n'

def detect_indent(blob):
    m = re.search(rb'\n([ \t]+)"', blob)
    return len(m.group(1)) if m else 1

def serialize(obj, ref):
    eol = detect_eol(ref)
    out = json.dumps(obj, indent=detect_indent(ref), ensure_ascii=False).encode('utf-8')
    if eol == b'\r\n':
        out = out.replace(b'\n', b'\r\n')
    if ref.endswith((b'\n', b'\r\n')) and not out.endswith(eol):
        out += eol
    if not ref.endswith((b'\n', b'\r\n')) and out.endswith(eol):
        out = out[:-len(eol)]
    return out

report = []

def take_new(path, side_note='snapshot'):
    o, t = stage(2, path), stage(3, path)
    jo, jt = json.loads(o), json.loads(t)
    to, tt = deep_ts(jo), deep_ts(jt)
    side = 'ours' if (not tt or (to and to >= tt)) else 'theirs'
    open(path, 'wb').write(o if side == 'ours' else t)
    report.append(f'{path}: {side_note} take-{side} (ours={to!r} theirs={tt!r})')

def take_new_twins(json_path, blob_paths):
    o, t = stage(2, json_path), stage(3, json_path)
    to, tt = deep_ts(json.loads(o)), deep_ts(json.loads(t))
    side = 'ours' if (not tt or (to and to >= tt)) else 'theirs'
    open(json_path, 'wb').write(o if side == 'ours' else t)
    for p in blob_paths:
        ob, tb = stage(2, p), stage(3, p)
        open(p, 'wb').write(ob if side == 'ours' else tb)
    report.append(f'{json_path}+{len(blob_paths)} twins: take-{side} (ours={to!r} theirs={tt!r})')

def union_ledger(path, list_key, dedup_key):
    o, t = stage(2, path), stage(3, path)
    jo, jt = json.loads(o), json.loads(t)
    ho, ht = jo.get(list_key, []), jt.get(list_key, [])
    seen, merged = set(), []
    for it in sorted(ho + ht, key=lambda x: x.get(dedup_key, '')):
        k = it.get(dedup_key) if isinstance(it, dict) else json.dumps(it, sort_keys=True)
        if k is None:
            k = json.dumps(it, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k); merged.append(it)
    jo[list_key] = merged
    # newest scalar fields take-new (updated/ts)
    if (jo.get('updated') or '') >= (jt.get('updated') or ''):
        pass
    else:
        for k, v in jt.items():
            if k != list_key:
                jo[k] = v
    open(path, 'wb').write(serialize(jo, o))
    keep = 'ours' if (jo.get('updated') or '') >= (jt.get('updated') or '') else 'theirs'
    report.append(f'{path}: ledger union {list_key} {len(ho)}|{len(ht)}->{len(merged)}, scalars take-{keep}')

# twins groups (same-side coupling law r98/r99)
take_new_twins('docs/daily_report/REPORT-2026-09-30.json', ['docs/daily_report/REPORT-2026-09-30.md'])
take_new_twins('docs/live_usage/LIVE-2026-09-30.json',
               ['docs/live_usage/LIVE-2026-09-30.md', 'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'])
take_new_twins('results/dashboard_status.json', ['results/dashboard_status.js'])  # js-wrapper whole-blob same side
take_new_twins('results/paper_export/export-2026-09-30.json', ['results/paper_export/latest.json'])
# plain snapshots
for p in ['results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/t35_open_fill_verify.json', 'results/token_usage.json',
          'results/update_status.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/prospect_paper/_summary.json',
          'results/prospect_promotion/_summary.json']:
    take_new(p)
# rolling ledgers
union_ledger('results/compute_audit.json', 'history', 'ts')
union_ledger('results/regime_state.json', 'history', 'asof')

fails = []
for p in ['docs/daily_report/REPORT-2026-09-30.json', 'docs/live_usage/LIVE-2026-09-30.json',
          'docs/live_usage/LIVE-latest.json', 'results/dashboard_status.json',
          'results/paper_export/export-2026-09-30.json', 'results/paper_export/latest.json',
          'results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/t35_open_fill_verify.json', 'results/token_usage.json', 'results/update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
          'results/compute_audit.json', 'results/regime_state.json']:
    try:
        json.loads(open(p, 'rb').read().decode('utf-8'))
    except Exception as e:
        fails.append(f'{p}: {e}')
# js wrapper sanity: starts with window.DASH_DATA
js = open('results/dashboard_status.js', 'rb').read()
if b'window.DASH_DATA' not in js:
    fails.append('dashboard_status.js lost js wrapper')
print('\n'.join(report))
print('PARSE-VERIFY:', 'ALL PASS' if not fails else 'FAIL -> ' + '; '.join(fails))
sys.exit(0 if not fails else 2)
