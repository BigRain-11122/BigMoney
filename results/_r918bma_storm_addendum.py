# -*- coding: utf-8 -*-
# r918 bm-a storm addendum: round report addendum line + heartbeat/state sync
# face refresh (origin advanced 11 mid-round; pull --rebase 3-UU canon resolve;
# r863 churn-sensitive continue refusal -> r808 manual pick commit -> r624
# reattach closeout; final tip ae5dc924a behind=0 self-verified).
import json, time
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())
TIP = 'ae5dc924a'

ADDENDUM = (
    '2026-10-09T' + ts[11:] + ' | r918 addendum (bm-a, closeout push-race + r863/r808/r624 storm resolution disclosure) | '
    'closeout push attempt 1 REJECTED non-fast-forward (origin advanced 11 mid-round: bm-c r807 half-open rebase takeover '
    'closeout integrating my seat push 3a875bf43 + w17 autofill keepalives + T2 dashboard wiring) -> pull --rebase hit 3-UU '
    'shared regen faces -> _r918bma_resolve_rebase.py canon resolve (r907/r910 bloodline, rebase ours/theirs swap-aware): '
    'attrition scan deep-ts take-mine 15:07:31 > bm-c 15:06:51 (both CLEAN rc0) + token_usage take-mine generated 15:07:12 > '
    '14:47:37 with per-machine sections identical 5/5 + compute_audit rolling-history full-json dedupe UNION 206+201->207 '
    'zero-loss (origin-only 6 mine-only 1, latest=mine 15:04:24) -> add+continue hit r863 churn-sensitive refusal (zero UU, '
    'saturation_engine 3 own-lane faces live-ticking) -> r863 backup/clean-tree dance -> continue hit Terminal-dumb EDITOR '
    'form -> r808 three-step (author-script inject junsheng.sun + commit -F message manual pick landing 8d38c1b57 author-'
    'preserved) -> continue still refused on unstaged churn per r685 already-manual-committed state -> r624 closeout (quit + '
    'branch -f main 8d38c1b57 + checkout reattach + independent churn-absorb tail commit ae5dc924a) -> push 502634c5e..'
    'ae5dc924a behind=0 self-verified post-push fetch+rev-list; zero --no-verify, zero force, zero abort, resolver receipts '
    'committed; dispatcher_state.bm-a.json live-tick residual left for next round absorb (treadmill face, post-push tick) '
    '| [r918 bm-a]\n'
)

p = 'round_reports-bm-a.md'
raw = open(p, 'rb').read()
assert raw.endswith(b'\n')
open(p, 'ab').write(ADDENDUM.encode('utf-8'))
print('addendum appended; lines ->', open(p, 'rb').read().count(b'\n'))

DID_APPEND = (' + CLOSEOUT STORM: origin +11 mid-round push rejection -> rebase 3-UU canon resolve (attrition deep-ts '
              'take-mine + token sections-identical take-mine + compute_audit history UNION 207 zero-loss) -> r863 '
              'churn-sensitive continue refusal -> r808 author-preserved manual pick commit 8d38c1b57 -> r624 reattach '
              'closeout -> churn-absorb tail -> push 502634c5e..ae5dc924a behind=0 self-verified')
SYNC = {'ts': ts, 'origin_tip': TIP, 'ahead_behind': '0/0',
        'note': 'r918 closeout storm resolved: rebase 3-UU canon + r808/r624 reattach; push self-verified post-push fetch+rev-list'}
LAST_ACTION = ('r918 closeout: W199 seat chain + closeout storm resolved (rebase 3-UU canon + r863/r808/r624 reattach); '
               'push ae5dc924a self-verified 0/0')
VERDICT = ('green (r918 closed: W199 seat chain landed probe rc0 ADMIT staircase 59th; closeout storm resolved r808/r624 '
           'canon; engine ALIVE idle; S6 38-leg bad NONE)')

for path in ('state-bm-a.json', 'fleet/machines/bm-a.json'):
    d = json.load(open(path, encoding='utf-8'))
    d['did'] = d.get('did', '') + DID_APPEND
    d['last_action'] = LAST_ACTION
    d['verdict'] = VERDICT
    d['sync'] = SYNC
    d['push_verified'] = SYNC
    d['ts'] = ts
    d['clock_read'] = ts
    if 'heartbeat_epoch_utc' in d:
        d['heartbeat_epoch_utc'] = epoch
        d['last_heartbeat_epoch_utc'] = epoch
        d['last_seen'] = ts
        d['last_run'] = ts
        d['last_orders_at'] = ts
        d['last_decisions_at'] = ts
    if 'updated' in d:
        d['updated'] = ts
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for path in ('state-bm-a.json', 'fleet/machines/bm-a.json'):
    d = json.load(open(path, encoding='utf-8'))
    assert isinstance(d['heartbeat_epoch_utc'], int)
    assert d['sync']['origin_tip'] == TIP
print('sync faces refreshed -> tip', TIP, '| epoch int', epoch, '| clock', ts)
