import io

arch = io.open('research/memory-archive/202609.md', encoding='utf-8').read()
codely = io.open('CODELY.md', encoding='utf-8').read()
probes = {
    'r332bmb tick full': 'tick 自提交落点在 fire 后',
    'r335 PS full': 'PowerShell ConvertFrom-Json 会对合法',
    'r89bmc stub-drop full': 'stub-drop 变方案锚全量归档态（指针',
}
for k, kw in probes.items():
    print(k, '| in archive:', kw in arch, '| in CODELY:', kw in codely)
# find the full text lines in CODELY for size estimate
total = 0
for l in codely.splitlines():
    for k, kw in probes.items():
        if kw in l:
            print('  CODELY line bytes:', len(l.encode('utf-8')), '|', k)
            total += len(l.encode('utf-8'))
print('sum of 3 fulls:', total, 'B')
