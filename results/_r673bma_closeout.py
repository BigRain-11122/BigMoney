# r673 bm-a closeout: state round_no 673 + heartbeat (epoch int, clock T-sep), programmatic + self-verify
import json, time, datetime

# --- state-bm-a.json: round_no +1, programmatic write, reparse self-check
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s['round_no'] = 673
with open('state-bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
chk = json.load(open('state-bm-a.json', encoding='utf-8'))
assert chk['round_no'] == 673 and isinstance(chk['round_no'], int)
print('state round_no=673 written, reparse PASS')

# --- heartbeat fleet/machines/bm-a.json: epoch int + clock_read T-sep ISO8601
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
assert isinstance(epoch, int) and 'T' in clock and '+' in clock
h['last_seen'] = clock
h['current_task'] = 'fund trio finalize-readiness chain: VALUE-SENS acceptance receipt landed (3/3 complete); NULLS watch (V721/Q559/D408 of 2000)'
h['cpu_cores'] = 32
h['idle_ram_gb'] = None
h['gpu_idle_vram_gb'] = None
h['verdict'] = 'green (audit flags=[]; py_low_board_clear golden-week legal idle; satengine alive rc0 queue 0)'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk2 = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk2['clock_read'] and chk2['clock_read'].count(':') >= 2
print('heartbeat written: epoch int', chk2['heartbeat_epoch_utc'], 'clock', chk2['clock_read'], '-- self-check PASS')
