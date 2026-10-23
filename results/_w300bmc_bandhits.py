# -*- coding: utf-8 -*-
import io, re
t = io.open('results/_w300bmc_dry.txt', encoding='utf-8').read()
out = []
for m in re.finditer(re.escape('675_101..675_300'), t):
    out.append('[%d] %s' % (m.start(), t[max(0, m.start() - 300):m.start() + 200]))
for m in re.finditer(re.escape('675_101'), t):
    out.append('675_101@%d: %s' % (m.start(), t[max(0, m.start() - 160):m.start() + 120]))
io.open('results/_w300bmc_bandhits.txt', 'w', encoding='utf-8').write('\n\n'.join(out))
print(len(out))