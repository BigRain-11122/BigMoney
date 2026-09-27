import re

p = 'CODELY.md'
b = open(p, 'rb').read()
t = b.decode('utf-8')
eol = '\r\n' if '\r\n' in b else '\n'
# find all marker blocks (r335 line-anchored law: ^<{7} / ^={7}$ / ^>{7})
pat = re.compile(r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*', re.S)
blocks = pat.findall(t)
print('marker blocks found:', len(blocks))
for hs, ms in blocks:
    print('  HEAD-side lines:', len([x for x in hs.split(eol) if x.strip()]), '| MINE-side lines:', len([x for x in ms.split(eol) if x.strip()]))
    print('  mine first 90:', ms.strip()[:90])
# resolution: keep MINE side (my pointer stub; origin deleted the full line entirely = entry preserved via my stub, full verbatim in both archive 20th-batch sections)
def repl(m):
    return m.group(2)
t2 = pat.sub(repl, t)
assert '<<<<<<<' not in t2 and '>>>>>>>' not in t2 and '=======' not in t2.replace('=======', '', 0) or True
assert '<<<<<<< HEAD' not in t2, 'markers remain'
# line-anchored sanity (r87 law): no leading-marker lines remain
for l in t2.splitlines():
    assert not l.startswith('<<<<<<<') and not l.startswith('>>>>>>>') and l.strip() != '======='
open(p, 'wb').write(t2.encode('utf-8'))
print('resolved size:', len(t2.encode('utf-8')), 'B')
print('r332bm-b stub present:', '二十批外迁·指针）：autofill tick' in t2)
print('r338 entry present:', '共享 JSON 面' in t2)
