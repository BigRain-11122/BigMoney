import re

t = open('scripts/perpetual_faces.py', encoding='utf-8').read()
rows = [(m.start(), m.group(0)) for m in re.finditer(r'^\s+1\d\d:\s*\{.*$', t, re.M)]
print('pf N1_BANDS numbered rows:', len(rows))
print('tail row:', rows[-1][1][:100])
print('prev row:', rows[-2][1][:100])

n = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
wc = [m.group(1) for m in re.finditer(r'^\s+(\d+):\s*\{"batch":\s*"PERPETUAL-N1-W(\d+)"', n, re.M)]
print('n1 WAVE_CONFIGS rows count:', len(wc), 'tail:', wc[-3:])
i2 = n.find('W173 materializer face')
print('W173 mat block at', i2)
i3 = n.find('materializer face', i2 + 100)
print('next mat mention at', i3)
if i3 > 0:
    print('ctx:', n[i3-80:i3+150].replace('\n', ' | '))
# find the materializer block chain pattern
i4 = n.find('chain 138..172')
print('chain 138..172 at', i4)
i5 = n.find('PASS-claim r822')
print('PASS-claim r822 at', i5)
