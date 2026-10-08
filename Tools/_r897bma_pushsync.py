# -*- coding: utf-8 -*-
# r897 post-push sync: state push_verified + heartbeat sync faces
import json, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
TIP = '3791f3403'

ST = 'state-bm-a.json'
st = json.load(open(ST, encoding='utf-8'))
st['push_verified'] = {"ts": now, "origin_tip": TIP, "ahead_behind": "0/0"}
json.dump(st, open(ST, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)

HB = 'fleet/machines/bm-a.json'
hb = json.load(open(HB, encoding='utf-8'))
hb['sync'] = {"ahead": 0, "behind": 0, "behind_origin": 0, "last_push_ts": now,
              "last_sync_at": now,
              "note": "r897 closeout push verified 0/0 @%s (QA per-machine-suffix first-proof delivered)" % TIP}
json.dump(hb, open(HB, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)

c1 = json.load(open(ST, encoding='utf-8'))
c2 = json.load(open(HB, encoding='utf-8'))
assert c1['push_verified']['origin_tip'] == TIP
assert c2['sync']['behind'] == 0
print('sync faces ok @', TIP)
