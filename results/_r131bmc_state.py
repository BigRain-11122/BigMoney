import json, datetime

p = 'state-bm-c.json'
s = json.load(open(p, encoding='utf-8'))
assert s['round_no'] == 130, 'expected 130, got %r' % (s['round_no'],)
s['round_no'] = 131
now = datetime.datetime.now().astimezone().isoformat(timespec='minutes')
s['updated'] = now[:16]
s['note'] = ('r131: green-maintenance watch round pre-market (orders 99/99 both-scans + decisions zero-new '
             '+ smoke 25/25 + S6 33/33 rc=0 no-op family + WM py_low_board_clear n=3 + audit CLEAN v2.3 '
             'pool-supply-gap) + T-95 watch: W2B census burning bmb (03:53 claim prio1 CEO-48h path) + V2-P1 '
             'defer_note verified in pool (S16c auto-clear at next pick, relaunch post-W2B stable-RAM >=4GB x3, '
             'flip=bmb round) + lane_io host-guard live on bmc (bma fresh-heartbeat skip x3 faces = bma r378 '
             'mechanism working) + zero bm-c-claimable (pool 81 done + 1 ready bmb-owned + 6 waiting)')
s['last_round_ts'] = now
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
r = json.load(open(p, encoding='utf-8'))
assert r['round_no'] == 131 and isinstance(r['round_no'], int), 'DISK RE-READ FAIL'
print('STATE_OK round_no=131 disk-verified ts=' + now)
