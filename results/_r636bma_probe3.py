import json
import os
import subprocess
import time

# divlowvol nulls file state
fp = r'results\fund_divlowvol_p1\nulls.jsonl'
n = sum(1 for _ in open(fp, encoding='utf-8'))
mt = time.strftime('%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fp)))
print('divlowvol nulls.jsonl rows:', n, '| mtime:', mt)

# pool divlowvol shard state (worktree)
data = open(r'results\runnable_pool.json', 'rb').read()
i = data.find(b'fund-divlowvol-p1-nulls-0of1')
seg = data[i:i + 1200]
print('--- divlowvol shard owner-bm-a:', b'"owner": "bm-a"' in seg,
      '| 18:38 in seg:', b'18:38' in seg)
j = seg.find(b'"owner"')
print(seg[j:j + 120].decode('utf-8', errors='replace'))

# fuse divlowvol sig state (worktree)
cf = json.load(open(r'results\crash_fuse.json', encoding='utf-8'))
sig = cf['sigs'].get('scripts/fund_divlowvol_p1.py|run,--nulls')
print('--- fuse divlowvol-nulls sig present:', sig is not None)
if sig:
    print('refusals:', sig.get('refusals'), '| last_refusal_ts:', sig.get('last_refusal_ts'),
          '| code_sha256:', sig.get('code_sha256'), '| machine:', sig.get('machine'))
cl = cf['cleared'].get('scripts/fund_divlowvol_p1.py|run,--nulls')
print('--- fuse cleared entry:', json.dumps(cl, ensure_ascii=False)[:300] if cl else None)

# value sig too
sv = cf['sigs'].get('scripts/fund_value_p1.py|run,--nulls')
print('--- fuse value-nulls sig present:', sv is not None)
cv = cf['cleared'].get('scripts/fund_value_p1.py|run,--nulls')
print('--- value cleared entry:', json.dumps(cv, ensure_ascii=False)[:300] if cv else None)

# quality sig (should be intact)
sq = cf['sigs'].get('scripts/fund_quality_p1.py|run,--nulls')
print('--- quality sig present:', sq is not None, '| sha:', sq.get('code_sha256') if sq else None,
      '| refusals:', sq.get('refusals') if sq else None)

# HEAD state of shared pool (what daemon committed at 18:38)
r = subprocess.run(['git', 'show', 'HEAD:results/runnable_pool.json'], capture_output=True)
hd = r.stdout
for key in (b'fund-value-p1-nulls-0of1', b'fund-divlowvol-p1-nulls-0of1'):
    k = hd.find(key)
    seg2 = hd[k:k + 1000]
    print('--- HEAD', key.decode(), '| owner-bm-a:', b'"owner": "bm-a"' in seg2,
          '| rel-note:', b'rel-bm-a-r636' in seg2)
