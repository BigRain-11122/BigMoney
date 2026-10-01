import json
raw = open('results/runnable_pool.json', 'rb').read().decode('utf-8')
i = raw.find('"LOWAMP-P3-CELL-LAREP-LEGACY-BASE"')
blk = raw[i:i + 3000]
k = blk.find('"shards"')
print(blk[k:k + 800].replace('\r', ''))
print()
# ghost entries: shard layer raw
for eid in ('LOWAMP-P3-SENS', 'LOWAMP-P3-CELL-LAEDGE-LEGACY-X2'):
    j = raw.find('"' + eid + '"')
    b2 = raw[j:j + 3000]
    k2 = b2.find('"shards"')
    print('=== ' + eid + ' shards:')
    print(b2[k2:k2 + 800].replace('\r', ''))
    print()
