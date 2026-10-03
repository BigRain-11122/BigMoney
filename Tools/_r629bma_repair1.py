import json
raw = open('results/runnable_pool.json', 'rb').read()
txt = raw.decode('utf-8')
fix1 = 'fuse keep-blocked on bm-a",'
fix2 = 're-burns via daemon",'
c1, c2 = txt.count(fix1), txt.count(fix2)
assert c1 == 1 and c2 == 1, (c1, c2)
txt = txt.replace(fix1, 'fuse keep-blocked on bm-a"')
txt = txt.replace(fix2, 're-burns via daemon"')
open('results/runnable_pool.json', 'wb').write(txt.encode('utf-8'))
json.loads(txt)
print('REPAIRED: shared pool parses OK')
