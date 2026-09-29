import json
import time

p = 'state-bm-a.json'
s = json.load(open(p, encoding='utf-8'))
s['next'] = ('R424 S0 FIRST ACTION = merge-back two-step (r419/bm-c-r208 precedent): single `git merge origin/main` (NOT rebase-replay), '
             'resolve regen/data faces take-freshest-ts (twin pairs same-side coupling, ALL_FACES via merge_lane_views resolve), '
             'push main; r423 content is SAFE on origin escape branch machine/bm-a-r423 (c219dec7) per two-rejection law; '
             'then normal S0.5+ flow. W7 runner slice-2 = bm-b physical dep (funnel cmds + GENERATE pool entry); W8 window gated on W7 full-chain.')
s['current_task'] = 'r423 closed on escape branch machine/bm-a-r423 (push storm x2 rejections); next=r424 S0 merge-back two-step'
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
h['current_task'] = ('r423 closed on escape branch machine/bm-a-r423 (origin push storm x2: bm-b r417-cont closeout + bm-c r208 merge-back both in-window; '
                     '13-UU canon-resolved + reconcile 14-face ZERO-DRIFT before escape); next=r424 S0 merge-back two-step single-merge per r419 precedent')
h['task'] = 'r423-escape-branch-landed-merge-back-next-round'
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
v = json.loads(open('fleet/machines/bm-a.json', encoding='utf-8').read())
assert isinstance(v['heartbeat_epoch_utc'], int)
assert ' ' not in v['clock_read']
print('state+heartbeat next-pointers updated; epoch int OK')
