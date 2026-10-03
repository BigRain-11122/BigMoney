"""r636 bm-a: re-anchor nulls.jsonl restore to CURRENT origin/main blob.

The earlier restore anchored to 01302cc2d (stale); origin has since advanced
(bm-b canonical appends + bm-c tick commits). Restoring to the current origin
blob makes the commit's nulls face identical to origin -> clean rebase, and
still strips all 50 illegal bm-a rows (they only exist in local history).
"""
import json
import subprocess

p = subprocess.run(['git', 'show', 'origin/main:results/fund_value_p1/nulls.jsonl'],
                   capture_output=True)
canon = p.stdout
rows = [json.loads(l) for l in canon.decode('utf-8').splitlines() if l.strip()]
ks = sorted(r['k'] for r in rows)
print('origin-tip canonical rows:', len(rows), '| k range:', ks[0], '..', ks[-1])

wt = [json.loads(l) for l in open(r'results\fund_value_p1\nulls.jsonl', encoding='utf-8') if l.strip()]
print('worktree rows before:', len(wt))

open(r'results\fund_value_p1\nulls.jsonl', 'wb').write(canon)
after = [json.loads(l) for l in open(r'results\fund_value_p1\nulls.jsonl', encoding='utf-8') if l.strip()]
print('worktree rows after:', len(after), '| == origin blob:',
      open(r'results\fund_value_p1\nulls.jsonl', 'rb').read() == canon)

# how does this compare to HEAD (8521bdc58 line has +25 illegal)?
r = subprocess.run(['git', 'diff', '--numstat', '--', 'results/fund_value_p1/nulls.jsonl'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('numstat vs HEAD:', r.stdout.strip())
