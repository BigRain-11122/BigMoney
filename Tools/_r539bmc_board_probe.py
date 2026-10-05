# r539 bm-c S2 board probe: fleet tasks status counts + pool counts + watermark verdict
import json, os, glob
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
stats = {}
open_tasks = []
for p in glob.glob(os.path.join(ROOT, 'fleet', 'tasks', '*.json')):
    try:
        t = json.load(open(p, encoding='utf-8-sig'))
    except Exception:
        continue
    st = t.get('status') or 'unknown'
    stats[st] = stats.get(st, 0) + 1
    if st == 'open':
        open_tasks.append(os.path.basename(p) + ' :: ' + str(t.get('title') or t.get('subject') or '')[:90])
print('TASKS_STATS=' + json.dumps(stats, ensure_ascii=False))
for t in open_tasks[:10]:
    print('OPEN: ' + t)
try:
    pool = json.load(open(os.path.join(ROOT, 'results', 'runnable_pool.json'), encoding='utf-8-sig'))
    entries = pool.get('entries') if isinstance(pool, dict) else pool
    if isinstance(entries, dict):
        entries = list(entries.values())
    ps = {}
    for e in entries:
        ps[e.get('status') or 'unknown'] = ps.get(ps.get('status') and '' or (e.get('status') or 'unknown'), 0) + 1 if False else ps.get(e.get('status') or 'unknown', 0) + 1
    ready = [e.get('id') for e in entries if e.get('status') == 'ready']
    print('POOL_TOTAL=%d POOL_STATS=%s' % (len(entries), json.dumps(ps, ensure_ascii=False)))
    print('POOL_READY=' + json.dumps(ready))
except Exception as e:
    print('POOL_READ_FAIL=' + repr(e))
try:
    wm = json.load(open(os.path.join(ROOT, 'results', 'watermark_red.json'), encoding='utf-8-sig'))
    print('WM_TS=%s WM_RED=%s LANE=%s' % (wm.get('ts'), wm.get('red'), wm.get('lane')))
    np_ = wm.get('next_pick') or {}
    print('WM_NEXT_STATUS=%s CAND=%s' % (np_.get('status'), str(np_.get('candidate'))[:110]))
except Exception as e:
    print('WM_READ_FAIL=' + repr(e))
