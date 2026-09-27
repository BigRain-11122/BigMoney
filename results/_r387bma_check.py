import re
src = open('Tools/autofill.py', encoding='utf-8').read()
calls = re.findall(r'_claim_shard\((.*?)\)\n', src)
sig = [c for c in calls if 'myid' not in c]
legs = [c for c in calls if c == '{"key": "s0"}, "bm-b", "E1"']
resid = [c for c in calls if c == '{"key": "s0"}, "bm-b"']
prod = [c for c in calls if 'rec["machine"]' in c]
print('total _claim_shard call/def lines:', len(calls))
print('E1 3-arg legs:', len(legs))
print('2-arg residual:', len(resid))
print('production calls:', prod)
print('other:', [c for c in calls if c not in legs and c not in resid and c not in prod and 'myid' not in c])
