import json, glob, os, datetime

rows = []
for f in glob.glob('results/**/*.json', recursive=True):
    try:
        d = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    tl = d.get('trials_ledger') if isinstance(d, dict) else None
    if isinstance(tl, dict):
        t = tl.get('total')
        if isinstance(t, (int, float)):
            rows.append((t, tl.get('batch'), f, tl.get('prev_total'), tl.get('batch_trials'),
                         datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime('%m-%d %H:%M')))
rows.sort()
for r in rows[-12:]:
    print(r)
