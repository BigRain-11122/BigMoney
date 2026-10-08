# r807 bm-b S0 rebase UU resolver #2 -- absorb pick dbbbf1c1c replay conflicts (80 files)
# Recipes per bigmoney-conflict-resolve SKILL.md (classifier + manual classification):
#  - data/daily/*.csv (12): content-identical, EOL-only (ours LF vs theirs CRLF) -> take ours bytes (origin face, no EOL noise)
#  - firm/traders/*.json (29) + results/prospect_paper/*.json (22): deep-ts max probe -> take-new whole doc
#    (probes verified: only-diff fields are as_of/updated/generated; theirs newer in traders/prospect)
#  - snapshot results (paper x6, futures/lhb status, t35, scorecards, update_status, promotion summary): deep-ts max -> take-new
#  - rolling-ledger (compute_audit.json, regime_state.json): union history/transitions by ts + take-new state fields
#  - append-log (t24_prospect_paper_cells.jsonl, x2_watch_log.jsonl): line-level union, merge-sorted by ts
import json, subprocess, sys

REPO = r'C:\\Fluxgroup\\FluxGroup\\quant\\bigmoney'
receipt = {}

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        sys.exit(f'blob fail {stage}:{path}')
    return r.stdout

def write(path, data):
    with open(REPO + '\\' + path.replace('/', '\\'), 'wb') as f:
        f.write(data)

def deep_ts_max(o, path=''):
    best = ''
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) >= 10 and v[:4] == '2026' and (v[4] == '-') and (len(v) == 10 or v[10] in 'T '):
                if v > best:
                    best = v
            elif isinstance(v, (dict, list)):
                b = deep_ts_max(v)
                if b > best:
                    best = b
    elif isinstance(o, list):
        for v in o[:50]:
            b = deep_ts_max(v)
            if b > best:
                best = b
    return best

uu = []
st = subprocess.run(['git', '-C', REPO, 'status', '--porcelain'], capture_output=True).stdout.decode('utf-8')
for ln in st.splitlines():
    if ln.startswith('UU '):
        uu.append(ln[3:].strip())

csvs = [p for p in uu if p.startswith('data/daily/') and p.endswith('.csv')]
jsonls = [p for p in uu if p.endswith('.jsonl')]
ledgers = ['results/compute_audit.json', 'results/regime_state.json']
snapshots = [p for p in uu if p not in csvs and p not in jsonls and p not in ledgers]

# ---------- CSVs: take ours bytes (EOL-only diff, content identical) ----------
for p in csvs:
    ob, tb = blob(2, p), blob(3, p)
    ol = ob.decode('utf-8').splitlines()
    tl = tb.decode('utf-8').splitlines()
    assert set(ol) == set(tl), f'{p}: content sets differ -- manual look needed'
    write(p, ob)
    receipt[p] = {'recipe': 'csv-eol-only take-ours(LF origin face)', 'lines': len(ol)}

# ---------- jsonl append-log: line union merge-sorted by ts ----------
def jline_ts(l):
    try:
        d = json.loads(l)
        return d.get('ts') or d.get('updated') or ''
    except Exception:
        return ''
for p in jsonls:
    ob, tb = blob(2, p), blob(3, p)
    otxt, ttxt = ob.decode('utf-8', errors='replace'), tb.decode('utf-8', errors='replace')
    ol = [l for l in otxt.splitlines() if l.strip()]
    tl = [l for l in ttxt.splitlines() if l.strip()]
    src_lines = set(ol) | set(tl)
    merged = {}
    for l in ol + tl:
        merged[l] = None
    lines = sorted(merged.keys(), key=lambda l: (jline_ts(l), l))
    out = ('\n'.join(lines) + '\n').encode('utf-8')
    crlf = b'\r\n' in ob[:3000]  # mirror ours' EOL style
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    write(p, out)
    bad_pre = 0
    for l in lines:
        try:
            json.loads(l)
        except json.JSONDecodeError:
            # pre-existing historical corruption tolerated only if verbatim in a source blob (both-sides-inherited)
            assert l in src_lines, f'{p}: NEW malformed line from merge: {l[:100]}'
            bad_pre += 1
    receipt[p] = {'recipe': 'append-log line-union merge-sort ts', 'ours': len(ol), 'theirs': len(tl), 'union': len(lines), 'preexisting_corrupt_lines_kept': bad_pre}

# ---------- rolling-ledger ----------
# compute_audit.json: history ts-union + latest take-new
p = 'results/compute_audit.json'
ours = json.loads(blob(2, p).decode('utf-8'))
theirs = json.loads(blob(3, p).decode('utf-8'))
by_ts = {}
for e in theirs['history'] + ours['history']:
    by_ts[e['ts']] = e
merged_hist = [by_ts[k] for k in sorted(by_ts)]
lat = ours['latest'] if ours['latest']['ts'] >= theirs['latest']['ts'] else theirs['latest']
merged = {'history': merged_hist, 'latest': lat}
txt = json.dumps(merged, indent=2, ensure_ascii=False)
write(p, (txt + '\n').encode('utf-8'))
receipt[p] = {'recipe': 'rolling-ledger history ts-union + latest take-new', 'ours_hist': len(ours['history']), 'theirs_hist': len(theirs['history']), 'union': len(merged_hist), 'latest_side': 'ours' if lat is ours['latest'] else 'theirs', 'latest_ts': lat['ts']}
json.loads(open(REPO + '\\results\\compute_audit.json', 'rb').read().decode('utf-8'))

# regime_state.json: union history/transitions by ts + take-new state fields
p = 'results/regime_state.json'
ours = json.loads(blob(2, p).decode('utf-8'))
theirs = json.loads(blob(3, p).decode('utf-8'))
def union_lists(key):
    a, b = ours.get(key, []), theirs.get(key, [])
    d = {}
    for e in b + a:
        k = e.get('ts') or e.get('asof') or json.dumps(e, sort_keys=True)
        d[k] = e
    return [d[k] for k in sorted(d)]
state = ours if (ours.get('updated') or '') >= (theirs.get('updated') or '') else theirs
merged = dict(state)
for key in ('history', 'transitions'):
    if key in ours or key in theirs:
        merged[key] = union_lists(key)
txt = json.dumps(merged, indent=2, ensure_ascii=False)
write(p, (txt + '\n').encode('utf-8'))
receipt[p] = {'recipe': 'rolling-ledger union history/transitions + take-new state', 'updated': merged.get('updated'), 'history': len(merged.get('history', []))}
json.loads(open(REPO + '\\results\\regime_state.json', 'rb').read().decode('utf-8'))

# ---------- snapshots: deep-ts max take-new ----------
for p in snapshots:
    ob, tb = blob(2, p), blob(3, p)
    try:
        od = json.loads(ob.decode('utf-8'))
        td = json.loads(tb.decode('utf-8'))
    except Exception as e:
        sys.exit(f'{p}: parse fail {e}')
    o_ts, t_ts = deep_ts_max(od), deep_ts_max(td)
    if t_ts > o_ts:
        winner, wb = 'theirs', tb
    else:
        winner, wb = 'ours', ob  # tie -> ours (r140 law)
    write(p, wb)
    receipt[p] = {'recipe': 'snapshot deep-ts take-new', 'ours_ts': o_ts, 'theirs_ts': t_ts, 'winner': winner}
    json.loads(open(REPO + '\\' + p.replace('/', '\\'), 'rb').read().decode('utf-8'))

rec_path = REPO + r'\results\_r807bmb_s0_resolve2_receipt.json'
with open(rec_path, 'w', encoding='utf-8') as f:
    json.dump({'round': 'r807-bm-b S0', 'pick': 'dbbbf1c1c absorb', 'files': receipt}, f, indent=2, ensure_ascii=False)
print('RESOLVE2-OK', len(receipt), 'files')
from collections import Counter
print(Counter(v['recipe'].split()[0] for v in receipt.values()))
sn = [v for v in receipt.items() if 'snapshot' in v[1]['recipe']]
for k, v in sn:
    if v['winner'] == 'theirs':
        print(' theirs-newer:', k)
