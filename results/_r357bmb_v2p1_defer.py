"""r357 bm-b: DECISION-CHAIN-V2-P1 ready->waiting defer (physical RAM window) + receipts evidence.

Facts:
- bm-c T-95 fix landed (53be4125): runner canonical hash now 6b850e168fad4e46 != fused
  880297a0fb0854bf -> S16c fix-is-the-unflag auto-clear armed (sig deleted at next pick).
- V2-P1 pool entry carries RAM>=4GB 3-sample precheck contract (bm-c s9-a5 + MSG-0355 ask).
- W2B (priority 1, census burn ~12.4GB no-kill precedent from W2A r356 samples
  1.31/1.96/3.96GB free) is the critical path for the trial-labor CEO 48h clock
  09-29 22:45 (MASS judge shards + C-family all gate on W2B done).
- V2-P1 est 5-15min wall, RAM peak ~4GB: firing it into the W2B burn window =
  the exact dual-4GB squeeze MSG-0345 co-signed. Serialize instead.
- Relaunch window = post-W2B-landing stable RAM (>=4GB x 3 samples), ETA today
  evening; deadline slack huge (48h clock 09-29 22:45, run needs 15min).
"""
import json

POOL = r'results\runnable_pool.json'
d = json.load(open(POOL, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('entries', d.get('items', []))

e = next(x for x in items if x.get('id') == 'DECISION-CHAIN-V2-P1')
assert e.get('status') == 'ready', f"V2-P1 status {e.get('status')} != ready"
e['status'] = 'waiting'
e['defer_note'] = (
    'r357 bm-b defer ready->waiting (bm-c MSG-0355 receipt action): T-95 fix verified '
    '(runner sha 6b850e168fad4e46 != fused 880297a0fb0854bf -> S16c fix-is-the-unflag '
    'auto-clear at next pick, sig self-deletes). Physical RAM sequencing: W2B census burn '
    '(priority 1, trial-labor CEO 48h clock critical path, ~12.4GB no-kill precedent) '
    'fires first; V2-P1 4GB peak into that burn = dual-4GB squeeze (MSG-0345 co-signed '
    'face). Relaunch window = post-W2B-landing stable RAM (>=4GB x 3 samples >=30s per '
    'r354), flip executor = bm-b round. Deadline slack: 48h clock 09-29 22:45 vs 15min run.'
)

with open(POOL, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)

d2 = json.load(open(POOL, encoding='utf-8'))
items2 = d2 if isinstance(d2, list) else d2.get('entries', d2.get('items', []))
e2 = next(x for x in items2 if x.get('id') == 'DECISION-CHAIN-V2-P1')
assert e2['status'] == 'waiting' and 'defer_note' in e2
print('OK: DECISION-CHAIN-V2-P1 -> waiting (defer_note set; fuse sig persists until next pick auto-clear)')
