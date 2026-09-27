import subprocess, json, io, re

out = subprocess.check_output(
    ['python', 'tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py'],
    stderr=subprocess.STDOUT).decode('utf-8', errors='replace')
io.open('results/_r365bma_classify_raw.txt', 'w', encoding='utf-8').write(out)

# structure: JSON array with "entries" key per file, then trailer lines
# find the JSON payload
start = out.find('{')
# the output is a pretty-printed json doc of list of entries + "unknown" list + trailer
# find matching brace end before the trailer '== 28 classified'
end_marker = out.find('== ')
payload = out[:end_marker].strip()
# payload may contain the json doc; try progressive parse
dec = json.JSONDecoder()
doc, idx = dec.raw_decode(payload.strip())
entries = doc if isinstance(doc, list) else doc.get('entries', doc.get('classified', []))
rows = []
for e in entries:
    rows.append((e.get('class', '?'), e.get('path', '?')))
for c, p in sorted(rows, key=lambda r: (r[0], r[1])):
    print('%-24s | %s' % (c, p))
print('total:', len(rows))
# also write machine-readable table
io.open('results/_r365bma_class_table.json', 'w', encoding='utf-8').write(
    json.dumps([{'class': c, 'path': p} for c, p in rows], indent=1))
