import re, io
p = r'K:/Fluxgroup/FluxGroup/quant/bigmoney/fleet/orders/O-20261001-1058-bm-c.md'
raw = open(p, encoding='utf-8').read()
lines = raw.split('\n')
out = []
dropped = []
for ln in lines:
    s = ln.strip()
    if s.startswith('<<<<<<<') or s.startswith('>>>>>>>') or s.startswith('|||||||'):
        dropped.append(s[:30]); continue
    if s == '=======':
        dropped.append('======= (separator)'); continue
    out.append(ln)
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('markers removed:', len(dropped))
for d in dropped: print(' -', d)
tail = '\n'.join(out[-14:])
print('--- tail check ---')
print(tail)
assert '<<<<<<<' not in '\n'.join(out) and '>>>>>>>' not in '\n'.join(out)
assert 'bm-b 轮会话 r502' in raw and '追加节二' in raw
print('RESOLVED-OK')
