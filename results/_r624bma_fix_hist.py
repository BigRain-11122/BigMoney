import io, json
p = 'results/saturation_engine/history_bm-a.jsonl'
t = io.open(p, encoding='utf-8', errors='replace').read()
for needle in ('}{"ts"', '}{"tick"', '}{"round', '}{"event'):
    t = t.replace(needle, '}\n' + needle[1:])
rows = [json.loads(l) for l in t.splitlines() if l.strip()]
print('rows:', len(rows), 'all-dict:', all(isinstance(r, dict) for r in rows))
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
