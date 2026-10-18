# -*- coding: utf-8 -*-
# r1089 bm-c: heartbeat watermark mirror sync (r1052 连带律 -- d19 update --advance
# wrote the STATE face only; the heartbeat last_orders_sha/last_decisions_sha
# mirror fields must sync from the state canonical face the same window).
import io
import json

S = 'state-bm-c.json'
H = 'fleet/machines/bm-c.json'
s = json.load(io.open(S, encoding='utf-8'))
h = json.load(io.open(H, encoding='utf-8'))

synced = {}
for k in ('last_orders_sha', 'last_decisions_sha', 'last_orders_read_at',
          'last_decisions_read_at', 'last_orders_at', 'last_decisions_at',
          'last_orders_seen', 'last_decisions_seen'):
    if k in s and s[k] != h.get(k):
        synced[k] = {'from': h.get(k), 'to': s[k]}
        h[k] = s[k]

io.open(H, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(h, indent=1, ensure_ascii=False))
h2 = json.load(io.open(H, encoding='utf-8'))
ok = all(h2.get(k) == s.get(k) for k in synced)
out = {'synced': synced, 'readback_ok': ok,
       'state_ord': s['last_orders_sha'], 'state_dec': s['last_decisions_sha'],
       'heart_ord': h2['last_orders_sha'], 'heart_dec': h2['last_decisions_sha'],
       'law': 'r1052 连带律: heartbeat mirrors sync from state canonical face same-window'}
io.open('results/_r1089bmc_heart_wm_sync.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1, ensure_ascii=False))
assert ok
