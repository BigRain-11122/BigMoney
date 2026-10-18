# r1073 UU resolver: 8 faces from rebase replay onto origin (bm-c r1110 S6-light 06:52-06:58 vs my chain 07:04-07:13)
# Rules: REPORT twins = generator-face equal (attribution both YES) -> ts newer-wins -> MINE;
#        append-only history faces (compute_audit, regime_state) -> r419 UNION (row-dump dedupe, ts-sort);
#        flat derived faces -> newer ts -> MINE (all probed newer).
# LAW (this window's new pit): assert markers-absent BEFORE git add.
import subprocess, json, io, sys

def obj(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('show fail ' + ref)
    return r.stdout.decode('utf-8')

MARKS = ('<<<<<<<', '>>>>>>>')

def assert_clean(text, p):
    for m in MARKS:
        assert m not in text, f'MARKER {m} in {p}'
    for line in text.splitlines():
        assert line.strip() != '=======', f'MARKER-LINE ======= in {p}'

def write(p, text):
    assert_clean(text, p)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    subprocess.run(['git', 'add', p], check=True)
    print('resolved+added:', p)

MINE = [  # whole-side take-mine faces (newer ts / same-generator newer twin)
    'docs/daily_report/REPORT-2026-10-19.json',
    'docs/daily_report/REPORT-2026-10-19.md',
    'results/fundamental_b_layer_filter.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/watermark_red.json',
]
for p in MINE:
    write(p, obj(':3:' + p))

UNION = ['results/compute_audit.json', 'results/regime_state.json']  # append-only history faces -> r419 UNION
for p in UNION:
    o, t = json.loads(obj(':2:' + p)), json.loads(obj(':3:' + p))
    ho, ht = o.get('history', []), t.get('history', [])
    seen, merged = set(), []
    def rowkey(r):
        return json.dumps(r, ensure_ascii=False, sort_keys=True)
    def rts(r):
        return str(r.get('ts') or r.get('time') or r.get('asof') or r.get('round') or r.get('generated') or '')
    for r in sorted(ho, key=rts) + sorted(ht, key=rts):
        k = rowkey(r)
        if k not in seen:
            seen.add(k); merged.append(r)
    o['history'] = merged
    for k in t:
        if k != 'history':
            o[k] = t[k]  # top-level scalars: take mine (newest envelope)
    txt = json.dumps(o, ensure_ascii=False, indent=1) + '\n'
    write(p, txt)
    print('  union:', p, 'orig_n', len(ho), 'mine_n', len(ht), '->', len(merged))

# final belt: staged faces marker scan
r = subprocess.run(['git', 'diff', '--cached', '--check'], capture_output=True, text=True)
staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True).stdout.split()
bad = []
for p in staged:
    c = subprocess.run(['git', 'show', ':' + p], capture_output=True).stdout.decode('utf-8', 'replace')
    if '<<<<<<<' in c or '>>>>>>> ' in c:
        bad.append(p)
print('staged marker scan bad:', bad if bad else 'CLEAN')
sys.exit(1 if bad else 0)
