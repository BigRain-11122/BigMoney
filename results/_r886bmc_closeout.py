# -*- coding: utf-8 -*-
# r886 bm-c closeout: state + heartbeat writer (epoch int law R170/R178, clock_read ISO8601 T law R262)
import json, time, datetime

# ---- state ----
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 886
st['verdict'] = ('green: W208 finalize landed (K=455520, ledger head 881389) + W209 five-face freeze + ignition 9/12 shards '
                 '(M10 row done) = real product round; engine queue refilled per CEO fill-order law')
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', st['round_no'])

# ---- heartbeat ----
hp = 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S') + ('+%02d:00' % int(now.utcoffset().total_seconds() / 3600))
epoch = int(time.time())
hb['last_seen'] = iso
hb['ts'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = epoch
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
ack = set(hb.get('orders_ack', []))
ack.add('O-20261011-1917-bm-c.md')  # bm-b dispatch, zero action for bm-c, acked r886
hb['orders_ack'] = sorted(ack)
# live resource faces (read-only best-effort)
try:
    import psutil
    hb['cpu_pct'] = round(psutil.cpu_percent(interval=0.5), 1)
    vm = psutil.virtual_memory()
    hb['free_ram_gb'] = round(vm.available / 1024**3, 1)
except Exception:
    pass
hb['now_active'] = ('W209 ignition burning (9/12 shards done, engine daemon live); M10 row done; W210 seat chain next')
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be ISO8601 T-format'
print('heartbeat ok: epoch=%d clock=%s acks=%d' % (chk['heartbeat_epoch_utc'], chk['clock_read'], len(chk['orders_ack'])))
