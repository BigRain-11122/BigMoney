import io, json, re, sys

P = 'fleet/machine-health.json'
c = io.open(P, encoding='utf-8-sig').read()

if '<<<<<<<' not in c:
    print('NO-MARKERS already clean')
    sys.exit(0)

# Resolve conflict hunks keeping the "Stashed changes" (local, newer ts) side.
pat = re.compile(r'<<<<<<< Updated upstream\r?\n(.*?)\|\|\|\|\|\|\| Stash base\r?\n(.*?)=======\r?\n(.*?)>>>>>>> Stashed changes\r?\n', re.S)
n, cnt = pat.subn(lambda m: m.group(3), c)
print('hunks resolved keeping-local:', cnt)

# defensive: any plain two-way marker form left
n2 = re.sub(r'<<<<<<< Updated upstream\r?\n(.*?)=======\r?\n(.*?)>>>>>>> Stashed changes\r?\n', lambda m: m.group(2), n)

io.open(P, 'w', encoding='utf-8', newline='').write(n2)

t = io.open(P, encoding='utf-8-sig').read()
try:
    json.loads(t)
    print('JSON-VALID, markers left:', t.count('<<<<<<<'), t.count('>>>>>>>'))
except Exception as e:
    print('JSON-FAIL:', e, 'markers:', t.count('<<<<<<<'), t.count('>>>>>>>'))
    sys.exit(2)
