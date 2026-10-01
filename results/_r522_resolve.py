"""r522 round-1 rebase resolver (crashed r521 closeout recovery).

Context: r521 closeout session died mid-rebase at 15:22:43 on the FINAL pick
(de3ec842a, the only pick, onto 9135d6cf1 = bm-b r509 integration).
13 UU faces per classifier:
  - 12 snapshot regen faces -> take-new via hardened deep-ts probe (r100/R350:
    value-shape gate ^20\\d{2}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}, key-EXCLUDE lists
    forbidden, probe STAGED blobs :2:/:3: never working tree)
  - 1 append-log (x2_watch_log.jsonl) -> line-level union zero loss (r188),
    chronology preserved by ts-field sort, base-blob line ending mirrored.

Probe tie -> HEAD side (:2:) per r140. Parse-verify before write-back (r185).
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

SNAPSHOTS = [
    'results/daily_scorecard.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json',
    'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/t35_open_fill_verify.json',
]
LOG = 'results/x2_watch_log.jsonl'

report = []

for p in SNAPSHOTS:
    a, b = blob(':2', p), blob(':3', p)
    ja, jb = json.loads(a), json.loads(b)
    ta, tb = deep_max_ts(ja), deep_max_ts(jb)
    if tb > ta:
        win, side = b, 'local(:3:)'
    elif ta > tb:
        win, side = a, 'origin(:2:)'
    else:
        win, side = a, 'origin(:2: tie->HEAD r140)'
    with open(os.path.join(REPO, p), 'wb') as f:
        f.write(win)
    json.loads(open(os.path.join(REPO, p), 'rb').read().decode('utf-8'))
    git('add', p)
    report.append((p, ta or '(none)', tb or '(none)', side))

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
out = nl.join(union) + trailing
with open(os.path.join(REPO, LOG), 'wb') as f:
    f.write(out.encode('utf-8'))
for l in union:
    json.loads(l)
git('add', LOG)
report.append((LOG, 'origin=%d' % len(la), 'local=%d' % len(lb),
               'union=%d lines (zero-loss: |A∪B|=%d)' % (len(union), len(set(la) | set(lb)))))

print(json.dumps(report, indent=1, ensure_ascii=False))

# post-resolution staged-set parse audit (r185): every staged .json must parse
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
