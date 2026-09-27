import re

p = 'CODELY.md'
b = open(p, 'rb').read()
t = b.decode('utf-8')
eol = '\r\n' if b'\r\n' in b else '\n'
pat = re.compile(r'<<<<<<< HEAD\r?\n(.*?)\r?\n?=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*', re.S)
blocks = pat.findall(t)
print('marker blocks:', len(blocks))
# keep MINE side (pointer stub; origin deleted the line entirely; full verbatim lives in both archive 20th sections)
t2 = pat.sub(lambda m: m.group(2), t)
bad = [l for l in t2.splitlines() if l.startswith(('<<<<<<<', '>>>>>>>')) or l.strip() == '=======']
assert not bad, 'markers remain: %d' % len(bad)
open(p, 'wb').write(t2.encode('utf-8'))
print('CODELY fixed, size:', len(t2.encode('utf-8')), 'B')
print('r332bmb stub kept:', '二十批外迁·指针）：autofill tick' in t2)
print('r338 entry kept:', '共享 JSON 面' in t2)
print('r90 entry kept (bm-c):', 'r90' in t2 or 'r89 bm-c' in t2)
