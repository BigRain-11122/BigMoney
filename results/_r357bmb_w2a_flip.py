"""r357 bm-b: flip CENSUS-FUS-S2-W2A pool entry to done (anti-relaunch, anti-ledger-inflation).

Facts verified this round (2026-09-28 03:31:20 products):
- w2a_results.json complete: n_candidates=5456 + n_controls=64 + n_nulls=400 = frozen N 5,920
- ledger embed: prev 288,384 + 5,920 = 294,304 (append landed inside batch finalize)
- checkpoint 5,920/5,920 lines; log tail "[done] ... ledger=294304" clean exit, no traceback
- runner has NO idempotency guard: a relaunch would re-finalize -> double ledger append
Convention: mirror CENSUS-FUS-S2-W1 done entry (entry status done + shard done + result_ref).
"""
import json

POOL = r'results\runnable_pool.json'
d = json.load(open(POOL, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('entries', d.get('items', []))
assert isinstance(items, list) and items and isinstance(items[0], dict), 'unexpected pool shape'

flipped = False
for e in items:
    if e.get('id') == 'CENSUS-FUS-S2-W2A':
        assert e.get('status') in ('ready', 'done'), f'unexpected status {e.get("status")}'
        e['status'] = 'done'
        for sh in e.get('shards', []):
            sh['status'] = 'done'
        e['result_ref'] = ('results/census_fusion_s2/w2a_results.json '
                           '(EXPLORATION face sec.9.3; N=5,920 = 5,456 cand + 64 rs + 400 nulls; '
                           'ledger 294,304; clean exit elapsed 44,308s; finalize+flip r357 bm-b; '
                           'post_review pending)')
        flipped = True
        break
assert flipped, 'CENSUS-FUS-S2-W2A entry not found'

with open(POOL, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

# self-verify
d2 = json.load(open(POOL, encoding='utf-8'))
items2 = d2 if isinstance(d2, list) else d2.get('entries', d2.get('items', []))
w2a = next(e for e in items2 if e.get('id') == 'CENSUS-FUS-S2-W2A')
assert w2a['status'] == 'done' and all(s.get('status') == 'done' for s in w2a['shards'])
print('flip OK: CENSUS-FUS-S2-W2A entry+shard -> done; result_ref set')
print('takeable check: entry no longer picked by _pick (status!=ready)')
