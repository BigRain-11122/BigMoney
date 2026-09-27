import json
import glob
import os

# 1. watermark red flag
try:
    wm = json.load(open('results/watermark_red.json', encoding='utf-8'))
    print('watermark_red:', json.dumps(wm, ensure_ascii=False)[:400])
except Exception as e:
    print('watermark_red read fail:', e)

# 2. open tasks on board
opens = []
for f in sorted(glob.glob('fleet/tasks/T-*.json')):
    try:
        t = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print('PARSE FAIL', f, e)
        continue
    st = t.get('status')
    if st in ('open', 'claimed'):
        print('BOARD:', os.path.basename(f), '| status=', st, '| claimed_by=', t.get('claimed_by'),
              '| title=', (t.get('title') or '')[:90])
        opens.append(f)
print('open+claimed count:', len(opens))

# 3. runnable pool state
try:
    pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
    items = pool.get('batches') or pool.get('items') or []
    if isinstance(pool, dict):
        for k, v in list(pool.items())[:14]:
            if isinstance(v, (str, int, float, bool)):
                print('pool.' + k, '=', v)
            elif isinstance(v, list):
                print('pool.' + k, '= list len', len(v))
except Exception as e:
    print('pool read fail:', e)

# 4. autofill state (recent launches)
try:
    af = json.load(open('results/autofill_state.json', encoding='utf-8'))
    launches = af.get('launches') or []
    print('autofill launches:', len(launches))
    for L in launches[-5:]:
        print('  launch:', json.dumps(L, ensure_ascii=False)[:260])
except Exception as e:
    print('autofill read fail:', e)
