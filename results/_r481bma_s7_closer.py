import json, io, os, time, datetime

# state round_no bump
sp = 'state-bm-a.json'
d = json.load(io.open(sp, encoding='utf-8'))
d['round_no'] = 481
tmp = sp + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
os.replace(tmp, sp)
print('state round_no ->', d['round_no'])

# heartbeat
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hb_path = 'fleet/machines/bm-a.json'
hb = json.load(io.open(hb_path, encoding='utf-8'))
hb['last_seen'] = clock
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
# keep current-task fields as-is; update verdict face
hb['verdict'] = 'r481: S6 chain all-green rc0 (lhb rc3 quarantine honest), WM py_low_with_work_cands legal-idle proof (board 0/bandit 0/pool 0, RW-5 freeze), Q9 post-settle rescan PASS, HANDOVER 5x catch-up r476-480 landed, no 09-30 bar yet (sina upstream tops 09-29, honest no-op), holiday-mode 10-01~10-07 one-line rounds ahead'
tmp = hb_path + '.tmp'
io.open(tmp, 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=2))
os.replace(tmp, hb_path)

# self-verify epoch int
hb2 = json.load(io.open(hb_path, encoding='utf-8'))
e = hb2.get('heartbeat_epoch_utc')
assert isinstance(e, int), 'epoch must be int'
assert 'T' in hb2.get('clock_read', ''), 'clock_read must be T-separated'
print('heartbeat epoch int OK:', e, 'clock:', hb2['clock_read'])
