raw = open('results/runnable_pool.json', encoding='utf-8', newline='').read()
i = raw.find('"FUND-VALUE-P1-NULLS"')
j = raw.rfind('{', 0, i)
depth = 0
k = j
while k < len(raw):
    if raw[k] == '{':
        depth += 1
    elif raw[k] == '}':
        depth -= 1
        if depth == 0:
            break
    k += 1
block = raw[j:k + 1]
lines = block.split('\r\n')
print('total lines:', len(lines))
for n, l in enumerate(lines):
    if l.strip().startswith('"runner":') or l.strip().startswith('"runner_args"'):
        for m in range(max(0, n - 1), min(len(lines), n + 3)):
            print(f'{m}: {lines[m]!r}')
        print('...')
