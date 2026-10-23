# -*- coding: utf-8 -*-
import io, json
r = json.load(io.open('results/_w300bmc_20261024_probe_receipt.json', encoding='utf-8'))
lines = []
for k, v in r.items():
    if k == 'legs':
        for lk, lv in v.items():
            lines.append('--- %s' % lk)
            lines.append(json.dumps(lv, ensure_ascii=False, indent=1))
    else:
        lines.append('%s: %s' % (k, json.dumps(v, ensure_ascii=False)))
io.open('results/_w300bmc_seat_legs.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')