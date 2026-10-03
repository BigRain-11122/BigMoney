import json, io, time
p = 'fleet/machines/bm-a.json'
hb = json.load(io.open(p, encoding='utf-8'))
ack = hb.get('orders_ack', [])
if 'O-20261003-1210-bm-c.md' not in ack:
    ack.append('O-20261003-1210-bm-c.md')
    ack.sort()
hb['orders_ack'] = ack
hb['last_seen'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
hb['current_task'] = ('r624: CEO O-20261003-1210 three orders executed same-round (Q3=Qwen3-8b resident 88tok/s; '
                      'Q2=1065-script archive sweep pushed; Q3=R0 diag root-caused: Avatar valid=True isHuman=True '
                      'mappedBones=41, R0 FAIL root=FindAssets search-face empty, evidence FluxVerse 44b603c); '
                      'S0 ride-rebase adopted r623 dead-session products')
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(hb, ensure_ascii=False, indent=2) + '\n')
v = json.load(io.open(p, encoding='utf-8'))
print('epoch int:', isinstance(v['heartbeat_epoch_utc'], int), '| ack has 1210:', 'O-20261003-1210-bm-c.md' in v['orders_ack'])
