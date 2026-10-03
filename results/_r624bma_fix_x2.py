import io, json
p = 'results/x2_watch_log.jsonl'
t = io.open(p, encoding='utf-8', errors='replace').read()
needle = '}{"ts"'
n = t.count(needle)
t2 = t.replace(needle, '}\n{"ts"')
rows = [json.loads(l) for l in t2.splitlines() if l.strip()]
print('glued fixed:', n, '| rows:', len(rows), '| all-dict:', all(isinstance(r, dict) for r in rows))
io.open(p, 'w', encoding='utf-8', newline='\n').write(t2)
