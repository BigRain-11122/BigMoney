# -*- coding: utf-8 -*-
import io, json
out = io.open('results/_r904bma_provcheck.txt', 'w', encoding='utf-8', newline='\n')
for path in ('results/saturation_engine/history_bm-a.jsonl',
             'results/saturation_engine/state_bm-a.json',
             'results/saturation_engine/face_bm-a.json'):
    try:
        txt = io.open(path, encoding='utf-8').read()
    except Exception as e:
        out.write('%s READ-ERR %s\n' % (path, e)); continue
    hits = [ln for ln in txt.splitlines() if ('w193' in ln.lower() or 'W193' in ln) and ('final' in ln.lower() or 'material' in ln.lower())]
    out.write('== %s == hits=%d\n' % (path, len(hits)))
    for h in hits[-6:]:
        out.write(h[:600] + '\n')
# also tail of history for recent W193 rows
txt = io.open('results/saturation_engine/history_bm-a.jsonl', encoding='utf-8').read()
rows = [ln for ln in txt.splitlines() if 'w193' in ln.lower()]
out.write('== history w193 rows total=%d tail4 ==\n' % len(rows))
for h in rows[-4:]:
    out.write(h[:500] + '\n')
out.close()
print('done')
