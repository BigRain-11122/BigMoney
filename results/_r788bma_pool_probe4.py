# -*- coding: utf-8 -*-
# r788 bm-a: full shard dicts for the 3 contested entries (owner/lane_owner ghost-check)
import subprocess, json

P = 'results/runnable_pool.bm-a.json'
def blob(spec):
    return json.loads(subprocess.run(['git', 'show', spec], capture_output=True).stdout)

ours = blob(':2:' + P); theirs = blob(':3:' + P)

def find(d, sid):
    for e in d['entries']:
        for sh in e.get('shards', []):
            if (sh.get('shard_id') or e['id']) == sid or e['id'] == sid:
                return e, sh
    return None, None

for sid in ('FUND-QUALITY-P1-NULLS', 'FUND-DIVLOWVOL-P1-NULLS', 'FUND-VALUE-P1-NULLS'):
    for name, d in (('ours', ours), ('theirs', theirs)):
        e, sh = find(d, sid)
        if sh is None:
            print(sid, name, 'NOT FOUND'); continue
        keep = {k: sh.get(k) for k in ('owner', 'owner_since', 'status', 'lane_owner', 'claimed_by', 'pid', 'cleared_ts', 'done_at', 'runner_sha256')}
        print(sid, name, json.dumps(keep, ensure_ascii=False))
    print()
