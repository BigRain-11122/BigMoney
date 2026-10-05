# r717 town.html alignment probe: building names vs org_chart v2 dept table
import io, re, sys, json

t = io.open('town.html', encoding='utf-8', errors='replace').read()
out = ['town.html LEN=' + str(len(t))]

# buildings array / objects: capture quoted strings near id/name/dept keys
names = re.findall(r'"name"\s*:\s*"([^"]{2,40})"', t)
titles = re.findall(r'"title"\s*:\s*"([^"]{2,60})"', t)
depts = re.findall(r'"dept"\s*:\s*"([^"]{2,40})"', t)
out.append('names: ' + json.dumps(names, ensure_ascii=False))
out.append('titles: ' + json.dumps(titles[:30], ensure_ascii=False))
out.append('depts: ' + json.dumps(depts[:40], ensure_ascii=False))

org = io.open('firm/org_chart.md', encoding='utf-8', errors='replace').read()
out.append('org_chart.md LEN=' + str(len(org)))
# dept table rows: | name | ... |
rows = [l for l in org.splitlines() if l.strip().startswith('|')]
out.append('org table rows (' + str(len(rows)) + '):')
for r in rows[:80]:
    out.append('  ' + r[:150])

io.open(r'results\_r717bmb_town_probe.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('WROTE probe', len(out))
