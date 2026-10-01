# r312 bm-c: SHARD-10 ghost-ready flip (r488/r489 burn-without-flip face).
# Evidence: product results/p2cal_ext/n1_w7/shard-10-of-12.json in tree
# (machine=bm-c, 184 runs, 17.2s), claim receipt committed at S0
# (pool_claims/PERPETUAL-N1-W7-SHARD-10/n1w7-10of12.bm-c.json), core sample
# line 10:54:22 committed. r509 raw-text surgical law: id-anchored first
# status line + key-anchored shard status line, no re-serialization.
raw = open('results/runnable_pool.json', 'rb').read()
OLD = b'"status": "ready",'
NEW = b'"status": "done",'

id_anchor = b'"id": "PERPETUAL-N1-W7-SHARD-10",'
i = raw.find(id_anchor)
assert i >= 0, 'id anchor missing'
j = raw.find(OLD, i)
assert j >= 0, 'entry status not found after id'
raw = raw[:j] + NEW + raw[j + len(OLD):]

key_anchor = b'"key": "n1w7-10of12",'
k = raw.find(key_anchor)
assert k >= 0, 'key anchor missing'
m = raw.find(OLD, k)
assert m >= 0, 'shard status not found after key'
next_id = raw.find(b'\n{\r\n"id"', k)
limit = next_id if next_id > 0 else len(raw)
assert m < limit, 'shard status escaped block'
raw = raw[:m] + NEW + raw[m + len(OLD):]

open('results/runnable_pool.json', 'wb').write(raw)
print('flipped: PERPETUAL-N1-W7-SHARD-10 entry+shard ready->done (double-layer r489)')
