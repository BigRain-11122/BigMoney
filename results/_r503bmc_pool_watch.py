# r503 bm-c pool watch: N2-W15 12 shards + fund trio (owner at entries[].shards[] layer per r692 law)
# lineage: r502bmc_pool_watch.py verbatim copy, receipt -> r503
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
# boards: fleet/tasks open tickets
import os
tasks_dir = REPO + r'\fleet\tasks'
open_t, claimed_t, done_t = [], [], []
for f in sorted(os.listdir(tasks_dir)):
    if not f.endswith('.json'):
        continue
    try:
        t = json.load(open(os.path.join(tasks_dir, f), encoding='utf-8'))
    except Exception:
        continue
    st = t.get('status', '')
    if st == 'open':
        open_t.append(f)
    elif st in ('claimed', 'in_progress'):
        claimed_t.append(f)
    elif st == 'done':
        done_t.append(f)
out.append('BOARDS: open=%d claimed/in_progress=%d done=%d' % (len(open_t), len(claimed_t), len(done_t)))
for f in open_t:
    out.append('OPEN: ' + f)
txt = '\n'.join(out)
open(REPO + r'\results\_r503bmc_pool_watch.txt', 'w', encoding='utf-8').write(txt)
print(txt)
