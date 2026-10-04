import json, io
d = json.load(open('results/runnable_pool.json', encoding='utf-8'))
out = io.open('results/_r497bmc_pool_peek.txt', 'w', encoding='utf-8')
out.write("entries=%d\n" % len(d.get('entries', [])))
for e in d.get('entries', []):
    key = e.get('key', '')
    if 'N2-W15' in e.get('id', '') or 'N2-W15' in key or 'W3' in str(e.get('id', ''))[:60]:
        out.write(json.dumps({k: e[k] for k in e if k not in ('shards',)}, ensure_ascii=False, indent=1)[:900] + "\n")
        for s in e.get('shards', []):
            out.write("  SHARD " + json.dumps({k: s.get(k) for k in ('key', 'status', 'owner', 'owner_since', 'done_at', 'cmd', 'args', 'eta_min', 'claim_ref') if k in s}, ensure_ascii=False) + "\n")
# status summary
from collections import Counter
c = Counter()
for e in d.get('entries', []):
    for s in e.get('shards', []):
        c[s.get('status')] += 1
out.write("shard status counts: " + json.dumps(dict(c)) + "\n")
ready = [(e.get('id'), s.get('key'), s.get('owner'), s.get('owner_since')) for e in d.get('entries', []) for s in e.get('shards', []) if s.get('status') == 'ready']
out.write("ready shards: " + json.dumps(ready, ensure_ascii=False) + "\n")
out.close()
print("WROTE results/_r497bmc_pool_peek.txt")
