# r674 bm-a: state round_no bump + heartbeat write (programmatic, self-verified per R170/R178/R262 laws)
import json, time, datetime, platform, os

# 1) state-bm-a.json round_no 674
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 674
st['next'] = ('r674: fund trio NULLS watch (origin truth: 3 shards owner bm-b since 10-04 11:36:12, live V36.3%/Q28.0%/D20.6% @11:44, '
              'rate slower than r673 probe -- ETA risk to 10-05..09 finalize window flagged honestly); '
              '10-06+ theme redirect-batch candidates draft (bl=0.75 deep-break E24-ii); '
              '10-08 market-open window external run-11/run-7 dual legs + governance day; '
              'W14 GM-parked maintained; moneyflow IC batch still panel-blocked (source-fuse)')
json.dump(st, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('state-bm-a.json', encoding='utf-8'))
assert chk['round_no'] == 674, 'round_no write failed'

# 2) heartbeat fleet/machines/bm-a.json
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hb_path = 'fleet/machines/bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = clock
hb['current_task'] = ('r674: S0 pre-alignment netpath (2-wave merge, crash_fuse origin-newer zero-loss checkout) + orders 153/153 + D-19 MATCH '
                      '+ smoke 48/48 + S6 36/36 rc0 (all CEO faces refreshed) + trio NULLS origin-truth readout (owner bm-b, V/Q/D 36/28/21%)')
try:
    import psutil
    cores = psutil.cpu_count(logical=True)
    ram_free_gb = round(psutil.virtual_memory().available / 1e9, 1)
    cpu_pct = psutil.cpu_percent(interval=0.5)
except Exception:
    cores, ram_free_gb, cpu_pct = 32, None, None
hb['cpu_cores'] = cores
hb['free_ram_gb'] = ram_free_gb
hb['cpu_pct'] = cpu_pct
hb['gpu_free_vram_gb'] = None
hb['verdict'] = 'green'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
# orders_ack unchanged (153/153 both scans zero unacked)
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk2 = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk2['clock_read'] and '+' in chk2['clock_read'], 'clock_read must be ISO8601 T-separated with offset'
print('state round_no=674 OK; heartbeat epoch int', chk2['heartbeat_epoch_utc'], 'clock', chk2['clock_read'])
