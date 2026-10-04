# r660 bm-b S0: verify trio NULLS burn liveness + QUALITY shard pool row (MSG-0915 response)
import json, os, time

# 1) pool QUALITY shard row (shared face, read-only)
with open('results/runnable_pool.json', encoding='utf-8') as f:
    raw = f.read()
pool = json.loads(raw)
hits = []
def walk(o, path=''):
    if isinstance(o, dict):
        if any('FUND-QUALITY-P1-NULLS' in str(v) for v in o.values() if isinstance(v, str)):
            hits.append((path, o))
        for k, v in o.items():
            walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '/' + str(i))
walk(pool)
print('POOL QUALITY ROWS:', len(hits))
for p, o in hits:
    print(json.dumps({k: o.get(k) for k in ('id', 'owner', 'owner_since', 'status', 'shards') if k in o}, ensure_ascii=False))

# 2) trio nulls files: line counts + mtime (growth = burn alive)
for fam in ('fund_quality_p1', 'fund_value_p1', 'fund_divlowvol_p1'):
    fp = f'results/{fam}/nulls.jsonl'
    if os.path.exists(fp):
        with open(fp, 'rb') as f:
            n = sum(1 for _ in f)
        mt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fp)))
        print(f'{fam}: lines={n} mtime={mt}')
    else:
        print(f'{fam}: MISSING')

# 3) autofill state (bm-b own lane face): what claims does daemon hold now
try:
    with open('results/autofill_state.bm-b.json', encoding='utf-8') as f:
        af = json.load(f)
    keep = af.get('keepalive_claims') or af.get('claims') or {}
    print('AUTOFILL keepalive_claims:', json.dumps(keep, ensure_ascii=False)[:400])
    print('AUTOFILL last_tick:', json.dumps({k: af.get(k) for k in ('last_tick', 'last_run', 'verdict')}, ensure_ascii=False)[:300])
except Exception as e:
    print('AUTOFILL read err:', e)
