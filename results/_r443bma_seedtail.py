import re
src = open('scripts/science_gates.py', encoding='utf-8').read()
start = src.index('SEED_REGISTRY = {')
i = src.index('{', start)
depth = 0
for j in range(i, len(src)):
    if src[j] == '{':
        depth += 1
    elif src[j] == '}':
        depth -= 1
        if depth == 0:
            end = j
            break
body = src[i:end]
pairs = re.findall(r'"(\w+)":\s*([\d_]+)', body)
print('total keys:', len(pairs))
for k, v in pairs[-14:]:
    print(k, v)
vals = sorted(int(v.replace('_', '')) for _, v in pairs)
print('max base:', vals[-1])
