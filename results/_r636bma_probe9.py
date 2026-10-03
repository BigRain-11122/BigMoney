import glob
import json
import os
import time

# 1) divlowvol nulls file: any new rows since 18:48?
fp = r'results\fund_divlowvol_p1\nulls.jsonl'
n = sum(1 for _ in open(fp, encoding='utf-8'))
mt = time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(fp)))
print('divlowvol nulls rows:', n, '| mtime:', mt)

# 2) w2 judge shard-2 checkpoint face: what does the runner write?
for pat in (r'results\mass_trial*', r'results\*w2*'):
    for d in glob.glob(pat):
        if os.path.isdir(d):
            print('dir:', d, '|', len(os.listdir(d)), 'items')

# 3) claim files for w2-judge-2of4 (both owners)
for fp2 in sorted(glob.glob(r'results\pool_claims\MASS-TRIAL-W2-JUDGE-SHARD-2\*')):
    c = json.load(open(fp2, encoding='utf-8'))
    print(os.path.basename(fp2), '->', c.get('state'), c.get('owner'), c.get('outcome'),
          c.get('claimed_at') or c.get('owner_since'), c.get('closed_at', ''))

# 4) pool face: w2-judge-2of4 + divlowvol-nulls shard states
data = open(r'results\runnable_pool.json', 'rb').read()
for key in (b'"key": "w2-judge-2of4"', b'"key": "fund-divlowvol-p1-nulls-0of1"'):
    i = data.find(key)
    if i < 0:
        print(key, 'NOT FOUND')
        continue
    eol = b'\r\n'
    end = data.find(b'}' + eol, i)
    blk = data[i:end]
    own = b'"owner": "bm-a"' in blk
    ownc = b'"owner": "bm-c"' in blk
    ts = [t.decode() for t in (b'18:47', b'18:48', b'18:46', b'18:38') if t in blk]
    print(key.decode(), '| bm-a owner:', own, '| bm-c owner:', ownc, '| ts hits:', ts)
