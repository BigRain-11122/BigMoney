# -*- coding: utf-8 -*-
"""r1100 bm-c: S0.5 ORD delta judgment (watermark 94b68e55... -> current).
Method PIN: ORD watermark = content-bytes sha1 of group origin docs/orders.md (r977).
Rows judged at commit level: newest commit whose orders.md content-sha1 == watermark
is the consumed point; rows added after that = this window's delta.
Canon clone of _r1099bmc_ord_judgment.py (OUT path rolled to r1100)."""
import subprocess, hashlib, json

G = r'K:\Fluxgroup\FluxGroup'
WATERMARK = json.load(open(r'state-bm-c.json', encoding='utf-8'))['last_orders_sha']
OUT = r'results\_r1100bmc_ord_judgment.json'

def show_bytes(path):
    return subprocess.run(['git', '-C', G, 'show', 'origin/main:' + path],
                          capture_output=True).stdout

def content_sha1(b):
    return hashlib.sha1(b).hexdigest()

cur_blob = show_bytes('docs/orders.md')
cur_sha = content_sha1(cur_blob)
rows_out = {'prev_watermark': WATERMARK, 'cur_sha1': cur_sha,
            'delta': cur_sha != WATERMARK, 'rows': [], 'verdict': 'ZERO_ACTION'}

# locate watermark commit in recent history of docs/orders.md
log = subprocess.run(['git', '-C', G, 'log', '--format=%H|%cI|%s', '-n', '30',
                      'origin/main', '--', 'docs/orders.md'],
                     capture_output=True).stdout.decode('utf-8', 'replace').strip().splitlines()
wm_commit = None
new_commits = []
for line in log:
    sha, ts, subj = line.split('|', 2)
    blob = subprocess.run(['git', '-C', G, 'show', sha + ':docs/orders.md'],
                          capture_output=True).stdout
    new_commits.append((sha, ts, subj))
    if content_sha1(blob) == WATERMARK:
        wm_commit = (sha, ts, subj)
        break

if wm_commit is None:
    # watermark not found in last 30 commits -> rows = full tail of new_commits (bounded)
    rows_out['watermark_commit_found'] = False
    span = new_commits
else:
    rows_out['watermark_commit_found'] = True
    rows_out['watermark_commit'] = {'sha': wm_commit[0][:9], 'ts': wm_commit[1], 'subj': wm_commit[2][:80]}
    idx = next(i for i, c in enumerate(new_commits) if c[0] == wm_commit[0])
    span = new_commits[:idx]  # commits strictly newer than watermark point

# extract added rows from each new commit
all_added = []
for sha, ts, subj in span:
    d = subprocess.run(['git', '-C', G, 'show', sha, '--', 'docs/orders.md'],
                       capture_output=True).stdout.decode('utf-8', 'replace')
    for ln in d.splitlines():
        if ln.startswith('+') and not ln.startswith('+++'):
            body = ln[1:].strip()
            if body and ('O-' in body or 'CEO' in body or '令' in body or '2026' in body):
                all_added.append({'commit': sha[:9], 'ts': ts, 'row': body[:400]})

rows_out['rows'] = all_added
n = len(all_added)
rows_out['row_count'] = n
# bm-c obligation scan
ob = [r for r in all_added if ('bm-c' in r['row'] or 'BigMoney' in r['row'] or '量化' in r['row']
       or 'bigmoney' in r['row'].lower())]
rows_out['bm_c_relevant_rows'] = len(ob)
if ob:
    rows_out['verdict'] = 'ACTION_REQUIRED'
rows_out['span_commits'] = [{'sha': s[:9], 'ts': t, 'subj': j[:80]} for s, t, j in span]

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rows_out, f, ensure_ascii=False, indent=1)
print(json.dumps({'cur_sha1': cur_sha, 'delta': rows_out['delta'],
                  'watermark_commit_found': rows_out['watermark_commit_found'],
                  'span_commits': len(span), 'rows_added': n,
                  'bm_c_relevant': len(ob), 'verdict': rows_out['verdict']},
                 ensure_ascii=False))
for r in all_added[:12]:
    print('ROW|', r['ts'], '|', r['row'][:200])
