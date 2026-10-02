import re, sys, json

raw = open('results/runnable_pool.json', 'rb').read()
txt = raw.decode('utf-8')
print('CRLF:', raw.count(b'\r\n'), 'LF-only:', raw.count(b'\n') - raw.count(b'\r\n'))
for m in re.finditer(r'"id": "FUND-VALUE[^"]*"', txt):
    s = max(0, m.start() - 70)
    print(repr(txt[s:m.end() + 60]))
    print('---')
p = json.loads(txt)
ids = [e['id'] for e in p['entries'] if 'FUND-VALUE' in e['id']]
print('entries:', len(ids), ids)
