import json, glob, sys
rows = []
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        data = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print(f"ERR {p}: {e}"); continue
    tickets = data if isinstance(data, list) else [data]
    for t in tickets:
        if not isinstance(t, dict):
            continue
        st = t.get('status') or ''
        if st in ('open', 'claimed', 'in_progress'):
            rows.append((t.get('id'), st, t.get('claimed_by'), t.get('immediate'), (t.get('subject') or '')[:80]))
for r in rows:
    print(' | '.join(str(x) for x in r))
print(f"-- total open/claimed/in_progress: {len(rows)}")
