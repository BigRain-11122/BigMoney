import io, json, time, datetime

hb_path = 'fleet/machines/bm-a.json'
hb = json.load(io.open(hb_path, encoding='utf-8'))
ack = hb.get('orders_ack') or []
for oid in ('O-20261010-2350-bm-c', 'O-20261011-0012-bm-a'):
    if oid not in ack:
        ack.append(oid)
hb['orders_ack'] = ack
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hb['last_seen'] = now
hb['ts'] = now
hb['clock_read'] = now
hb['heartbeat_epoch_utc'] = int(time.time())
hb['last_orders_seen'] = ('r964 consume: fleet delta 67 files vs 269 ack -> 2 rows acked this round '
                          '(O-20261010-2350 @bm-a receipt = W205 five-face freeze+ignition, landed by r963 estate '
                          '9e3dea37f, verified; O-20261011-0012 CPU full-use = clause faces already enforced: W17 '
                          'judge burn in-flight, autofill parallel clause live, audit-face py_cpu reporting stands); '
                          'group ORD 3af479f1->f90233c7 consumed (O-0012 = same row, bm-c r854 clause-4 consumed '
                          'first, my verification zero-delta) + DEC a20664ec->caca0c6e consumed '
                          '(D-20261010-02 executed group-bookkeeping zero BigMoney action + D-20261010-03 '
                          'audit-script A-leg fix ALREADY landed group 30abf2f, zero re-execution)')
hb['last_orders_at'] = now
json.dump(hb, io.open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
back = json.load(io.open(hb_path, encoding='utf-8'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
assert len(back['orders_ack']) == len(ack)
print('acked:', len(back['orders_ack']), '| epoch int OK |', now)
