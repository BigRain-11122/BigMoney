# -*- coding: utf-8 -*-
# R264 (bm-a): heartbeat update -- R170/R178/R262 laws (epoch JSON int, clock_read T-separated ISO)
import json
import time
from datetime import datetime

P = 'fleet/machines/bm-a.json'
raw = open(P, 'rb').read()
has_bom = raw[:3] == b'\xef\xbb\xbf'
crlf = raw.count(b'\r\n') > 0
d = json.loads(raw.decode('utf-8-sig'))

try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024**3, 1)
except Exception:
    cpu_pct, free_ram_gb = d.get('cpu_pct'), d.get('free_ram_gb')

now = datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

d['last_seen'] = now
d['current_task'] = 'R264 closed: T-73 s3 verdict consolidation ledger delivered (CN_COMBO_VERDICTS.md five families x 19 cells ALL NEGATIVE honest; T-73 science faces fully closed)'
d['cpu_pct'] = cpu_pct
d['free_ram_gb'] = free_ram_gb
d['round_no'] = 264
d['verdict'] = ('GREEN R264: red(18:50 runnable-work-idle)->probe flip py_low_board_clear legal-idle; O-0926 closing face = five CN combo '
                 'families honestly judged NEGATIVE 0/19 (null-line dominates = beta not alpha, corroborates T-28); zero registry + no-reopen + '
                 'no-paper-for-negative GM ruling; smoke 25/25; S6 24 legs exit 0; push 132d40db')
d['heartbeat_epoch_utc'] = epoch
d['clock_read'] = now
d['task'] = ('R264 done: CN combo verdict ledger closed O-0926 face; next = 09-28 Mon new-bar chain (cutoff 09-24), R265 5x HANDOVER, '
             '10-01 trio + REGIME_GUARD v3, T-70 verdict 10-09')

txt = json.dumps(d, ensure_ascii=False, indent=1)
if crlf:
    txt = txt.replace('\n', '\r\n')
out = txt.encode('utf-8')
if has_bom:
    out = b'\xef\xbb\xbf' + out
if raw.endswith(b'\n'):
    out += b'\n'
with open(P, 'wb') as fh:
    fh.write(out)

# self-verify per prompt law
chk = json.loads(open(P, 'rb').read().decode('utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat ok: epoch', chk['heartbeat_epoch_utc'], 'type', type(chk['heartbeat_epoch_utc']).__name__, '| clock', chk['clock_read'])
