"""r522 S7 third-hop rebase resolver (replay r522 commit 21024fdd3 onto 642e2bc94).

28 UU, same families as round 2 -- resolver2 pattern reused with this hop's
exact file set. Sides: :2: = origin (bm-b r509 S6 run ~15:5x-16:0x),
:3: = replay (bm-a r522 S6 run 16:1x-16:3x, NEWER) -- deep-ts probes decide
per file; ties -> HEAD (:2:) per r140. merge_lane_views for ALL_FACES (r376).
"""
import subprocess, json, re, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    return subprocess.check_output(['git', '-C', REPO] + list(args))

def blob(stage, path):
    return git('show', stage + ':' + path)

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def deep_max_ts(obj, cur=''):
    if isinstance(obj, dict):
        for v in obj.values():
            cur = deep_max_ts(v, cur)
    elif isinstance(obj, list):
        for v in obj:
            cur = deep_max_ts(v, cur)
    elif isinstance(obj, str) and TS_RE.match(obj) and obj > cur:
        cur = obj
    return cur

def probe_side(path):
    a, b = blob(':2', path), blob(':3', path)
    ta = deep_max_ts(json.loads(a))
    tb = deep_max_ts(json.loads(b))
    if tb > ta:
        return 'local', ta, tb, b
    return 'origin', ta, tb, a  # tie->HEAD r140

def take_snapshot(path):
    side, ta, tb, win = probe_side(path)
    with open(os.path.join(REPO, path), 'wb') as f:
        f.write(win)
    json.loads(open(os.path.join(REPO, path), 'rb').read().decode('utf-8'))
    git('add', path)
    return (path, 'origin-ts=' + (ta or '(none)'), 'local-ts=' + (tb or '(none)'),
            'take-' + side + (' (tie->HEAD)' if ta == tb else ''))

report = []

TWINS = [
    ('docs/daily_report/REPORT-2026-10-01.json', 'docs/daily_report/REPORT-2026-10-01.md'),
    ('docs/live_usage/LIVE-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]
for jpath, mpath in TWINS:
    side, ta, tb, winj = probe_side(jpath)
    winm = blob(':3' if side == 'local' else ':2', mpath)
    with open(os.path.join(REPO, jpath), 'wb') as f:
        f.write(winj)
    with open(os.path.join(REPO, mpath), 'wb') as f:
        f.write(winm)
    json.loads(open(os.path.join(REPO, jpath), 'rb').read().decode('utf-8'))
    git('add', jpath)
    git('add', mpath)
    report.append((jpath, ta, tb, 'take-' + side))
    report.append((mpath, 'bytes-from-same-side', '', 'take-' + side))

side, ta, tb, winj = probe_side('results/dashboard_status.json')
with open(os.path.join(REPO, 'results/dashboard_status.json'), 'wb') as f:
    f.write(winj)
winjs = blob(':3' if side == 'local' else ':2', 'results/dashboard_status.js')
with open(os.path.join(REPO, 'results/dashboard_status.js'), 'wb') as f:
    f.write(winjs)
json.loads(open(os.path.join(REPO, 'results/dashboard_status.json'), 'rb').read().decode('utf-8'))
git('add', 'results/dashboard_status.json')
git('add', 'results/dashboard_status.js')
report.append(('results/dashboard_status.json', ta, tb, 'take-' + side))
report.append(('results/dashboard_status.js', 'same-side-bytes', '', 'take-' + side))

SNAPSHOTS = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
]
for p in SNAPSHOTS:
    report.append(take_snapshot(p))

LOG = 'results/x2_watch_log.jsonl'
a, b = blob(':2', LOG), blob(':3', LOG)
crlf = b'\r\n' in a
la = a.decode('utf-8').splitlines()
lb = b.decode('utf-8').splitlines()
sa = set(la)
union = la + [l for l in lb if l not in sa]

def tskey(l):
    try:
        return json.loads(l).get('ts', '')
    except Exception:
        return ''

union.sort(key=tskey)
nl = '\r\n' if crlf else '\n'
trailing = nl if (a.endswith(b'\n') or a.endswith(b'\r\n')) else ''
with open(os.path.join(REPO, LOG), 'wb') as f:
    f.write((nl.join(union) + trailing).encode('utf-8'))
for l in union:
    json.loads(l)
git('add', LOG)
report.append((LOG, 'origin=%d' % len(la), 'local=%d' % len(lb),
               'union=%d (|A∪B|=%d)' % (len(union), len(set(la) | set(lb)))))

ALL_FACES = ['results/compute_audit.json', 'results/regime_state.json',
             'results/update_status.json', 'results/lhb_update_status.json',
             'results/futures_update_status.json', 'results/token_usage.json']
for p in ALL_FACES:
    out = subprocess.run(['python', os.path.join(REPO, 'scripts', 'merge_lane_views.py'),
                          'resolve', p], capture_output=True, text=True,
                         cwd=REPO).stdout
    json.loads(open(os.path.join(REPO, p), 'rb').read().decode('utf-8'))
    git('add', p)
    report.append((p, out.strip().splitlines()[-2][:80] if out else '(no output)', '', 'canon r376'))

print(json.dumps(report, indent=1, ensure_ascii=False))
staged = git('diff', '--cached', '--name-only').decode('utf-8').split()
bad = []
for p in staged:
    if p.endswith('.json'):
        try:
            json.loads(open(os.path.join(REPO, p), 'rb').read().decode('utf-8'))
        except Exception as e:
            bad.append((p, str(e)[:80]))
print('staged json parse audit: %d files, %d bad' % (len([p for p in staged if p.endswith('.json')]), len(bad)))
for p, e in bad:
    print('BAD:', p, e)
print('REMAINING_UNMERGED=%d' % len(git('diff', '--name-only', '--diff-filter=U').decode('utf-8').split()))
