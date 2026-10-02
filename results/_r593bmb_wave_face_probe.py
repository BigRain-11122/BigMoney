# r593 bm-b: verify _engine_wave_state derive (isolated, read-only)
import sys, json
sys.path.insert(0, r'.')
sys.path.insert(0, r'scripts')
from monitor import build_status as bs

w = bs._engine_wave_state()
print(json.dumps(w, ensure_ascii=False, indent=1)[:1400])
assert w['present'] is True
assert w['last_registered'] == 113, w['last_registered']
assert w['last_owner'] == 'bm-c', w['last_owner']
assert w['next_registration'] == 114
assert w['next_seatable'] == 115, w['next_seatable']
assert w['chain_head'] == 610948, w['chain_head']
assert w['k'] == 244320, w['k']
assert len(w['waves']) == 3
w113 = [x for x in w['waves'] if x['wave'] == 113][0]
assert w113['shards_done'] == 12 and w113['shards_total'] == 12
assert w113['finalize_landed'] is False
w112 = [x for x in w['waves'] if x['wave'] == 112][0]
assert w112['finalize_landed'] is True and w112['ledger_total'] == 610948
assert {'wave': 114, 'machine': 'bm-a'} in w['seats'], w['seats']
print('ALL ASSERTS PASS')
