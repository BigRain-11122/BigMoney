# -*- coding: utf-8 -*-
import io

p = r'results\_r1141bmc_prereg_derive_w283.py'
s = io.open(p, encoding='utf-8', newline='').read()

anchor = 'add("R283", "R284")\n'
assert s.count(anchor) == 1
s = s.replace(anchor,
              anchor + 'add("→W280 **0.000312**→W282 **0.000312**", "→W280 **0.000312**→W281 **0.000312**→W282 **0.000312**")\n', 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched ok')