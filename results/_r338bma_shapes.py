import json
import io

out = []

# 1. T19 pool entry done-shape (mirror conventions)
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
for e in pool['entries']:
    if e.get('id') == 'T19-PHANTOM-P1':
        out.append('T19 done fields: done_at=%s' % e.get('done_at'))
        out.append('T19 note_done: %s' % json.dumps(e.get('note_done'), ensure_ascii=False)[:600])
        out.append('T19 shard: %s' % json.dumps(e.get('shards'), ensure_ascii=False)[:400])

# 2. T-46 ticket progress tail
t = json.load(open('fleet/tasks/T-2026-09-25-46-P1.json', encoding='utf-8'))
prog = t.get('progress') or []
out.append('T-46 keys: %s' % list(t.keys()))
out.append('T-46 progress type=%s len=%s' % (type(prog).__name__, len(prog) if isinstance(prog, list) else 'dict'))
if isinstance(prog, list):
    for p in prog[-3:]:
        out.append('  PROGRESS: %s' % json.dumps(p, ensure_ascii=False)[:400])
else:
    out.append('  PROGRESS-VAL: %s' % json.dumps(prog, ensure_ascii=False)[:600])

# 3. SINA_MF_PREREG amendment precedent (grep 修正案)
txt = io.open('research/shortline/SINA_MF_PREREG.md', encoding='utf-8').read()
out.append('SINA_MF_PREREG size: %d' % len(txt.encode('utf-8')))
idx = 0
count = 0
while count < 6:
    i = txt.find('修正案', idx)
    if i < 0:
        break
    out.append('  AMEND@%d: %s' % (i, txt[max(0, i - 100):i + 160].replace('\n', ' | ')))
    idx = i + 3
    count += 1

io.open('results/_r338bma_shapes.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out))
