# r502 bm-c pool watch: N2-W15 12 shards + fund trio (owner read at entries[].shards[] layer per r692 law)
import json
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
pool = json.load(open(REPO + r'\results\runnable_pool.json', encoding='utf-8'))
out = []
for e in pool.get('entries', []):
    eid = e.get('id', e.get('key', ''))
    if 'N2-W15' in eid or 'PERPETUAL-N2' in eid:
        out.append('ENTRY %s status=%s' % (eid, e.get('status')))
        for s in e.get('shards', []):
            out.append('  shard %s status=%s owner=%s owner_since=%s' % (s.get('key'), s.get('status'), s.get('owner'), s.get('owner_since')))
    if 'FUND' in eid.upper() and ('VALUE' in eid.upper() or 'DIVLOWVOL' in eid.upper() or 'QUALITY' in eid.upper()):
        out.append('ENTRY %s status=%s' % (eid, e.get('status')))
        for s in e.get('shards', []):
            out.append('  shard %s status=%s owner=%s owner_since=%s' % (s.get('key'), s.get('status'), s.get('owner'), s.get('owner_since')))
txt = '\n'.join(out)
open(REPO + r'\results\_r502bmc_pool_watch.txt', 'w', encoding='utf-8').write(txt)
print(txt)
