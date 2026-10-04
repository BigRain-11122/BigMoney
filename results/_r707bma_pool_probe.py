import json, io, glob, os
p = json.loads(io.open('results/runnable_pool.json', 'rb').read().decode('utf-8', errors='replace'))
out = []
for x in p.get('entries', []):
    if 'N2-W15-JUDGE' in str(x.get('id', '')):
        for sh in x.get('shards', []):
            out.append(f"{sh.get('key')}: status={sh.get('status')} owner={sh.get('owner')} since={sh.get('owner_since')}")
io.open('results/_r707bma_shard_status.txt', 'w', encoding='utf-8').write('\n'.join(out))

# claim files
out2 = []
for f in sorted(glob.glob('results/pool_claims/PERPETUAL-N2-W15-JUDGE/*.json')):
    try:
        c = json.loads(io.open(f, 'rb').read().decode('utf-8', errors='replace'))
        out2.append(os.path.basename(f) + ' :: ' + json.dumps({k: c.get(k) for k in ('state','status','owner','closed','done','settled')}, ensure_ascii=False))
    except Exception as e:
        out2.append(os.path.basename(f) + ' ERR ' + str(e))
io.open('results/_r707bma_claims.txt', 'w', encoding='utf-8').write('\n'.join(out2))
print('ok')
