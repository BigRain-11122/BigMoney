# r342 bm-b addendum: push-cycle receipt (network recovered, non-FF, escape branch, fold carried to r343)
import json, time
from datetime import datetime

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
now_epoch = int(time.time())
now_iso = datetime.fromtimestamp(now_epoch).astimezone().isoformat(timespec='seconds')

# --- round_reports.md addendum line ---
rp = ROOT + r'\logs\iteration-loop\round_reports.md'
addendum = (
    now_iso + ' | round 342 addendum bm-b | dept:工程+舰队 | S7 push-cycle receipt: network RECOVERED ~21:18 '
    '(bounded 25s push CONNECTED; 21:11 fetch timeout = transient stall, not a full dead window) but main push '
    'REJECTED non-FF: origin/main advanced during the dead window (bm-a pushed; local remote-tracking ref stale, '
    'true divergence unseen until r343 fetch) -> fold NOT attempted in-window: autofill tick strike window '
    '(:X0:02) + <2min round budget = r335/r91 「解完才 add 且赶 tick 前」律不可满足, rushing multi-file UU resolve = '
    'known killer pattern -> escape valve per S7 discipline: origin machine/bm-b-r342 pushed carrying full '
    'local-ahead chain (incl 6be5993f r342 close + tick tails); r343 S0 fold FIRST MISSION (fresh budget): '
    'fetch -> pull --rebase -> classify_conflicts.py 正典解 (autofill_state UU expected per r341 pointer; '
    'CODELY.md memory-union; round_reports-bm-a.md append-log union; state-bm-a.json snapshot take-side; '
    'p1d_gates.json take-new meta) -> push main -> GC escape branches machine/bm-b-r340 + machine/bm-b-r342 '
    '-> verify ce11fad7+b2a36f94+6be5993f chain on origin/main\n'
)
with open(rp, 'rb') as f:
    raw = f.read()
sep = b'' if raw.endswith(b'\n') else b'\n'
with open(rp, 'ab') as f:
    f.write(sep + addendum.encode('utf-8'))

# --- state.json next/current refresh ---
sp = ROOT + r'\logs\iteration-loop\state.json'
with open(sp, encoding='utf-8') as f:
    st = json.load(f)
st['current_task'] = ('r342 closed: S6 30/30 + W2-A burn verify + network RECOVERED (push non-FF, origin advanced), '
                      'escape branch machine/bm-b-r342 pushed, fold = r343 first mission')
st['next'] = ('r343 S0 fold mainline FIRST MISSION (network recovered 21:18; fetch -> pull --rebase -> '
              'classify_conflicts canonical resolve: autofill_state UU expected, CODELY.md memory-union, '
              'round_reports-bm-a append-log, state-bm-a take-side -> push main -> GC escape machine/bm-b-r340 '
              '+ machine/bm-b-r342 -> verify ce11fad7+b2a36f94+6be5993f on origin/main); W2-A finalize harvest '
              '~21:40+ (r312 done-flip + T-86 bm-a receipt); Mon 09-28: 09:15 T-91 s3 auto-fire + 15:30 T-87 '
              'astock first increment + new-bar full chain; 10-01 monthly trio + REGIME_GUARD v3 date gate')
st['updated_at'] = now_iso
st['last_seen'] = now_iso
st['ts'] = datetime.fromtimestamp(now_epoch).strftime('%Y-%m-%d %H:%M:%S')
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat current_task + fresh time ---
hp = ROOT + r'\fleet\machines\bm-b.json'
with open(hp, encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = now_epoch
hb['clock_read'] = now_iso
hb['current_task'] = st['current_task']
with open(hp, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- self-verify ---
with open(sp, encoding='utf-8') as f:
    st2 = json.load(f)
with open(hp, encoding='utf-8') as f:
    hb2 = json.load(f)
assert isinstance(hb2['heartbeat_epoch_utc'], int) and hb2['heartbeat_epoch_utc'] == now_epoch
assert st2['round_no'] == 342
print('ADDENDUM OK epoch=%d(%s) clock=%s' % (hb2['heartbeat_epoch_utc'],
      type(hb2['heartbeat_epoch_utc']).__name__, hb2['clock_read']))
