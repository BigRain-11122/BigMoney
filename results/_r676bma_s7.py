# _r676bma_s7.py -- state round_no bump + heartbeat update (programmatic, json.loads self-check)
import json, time, psutil

# --- state bump
SP = 'state-bm-a.json'
s = json.load(open(SP, encoding='utf-8'))
s['round_no'] = 676
s['last_decisions_sha'] = '4e5be321f9b7a15d7f58bab3771ecf329534eed8d30b090cdac4e9f151d911dc'
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(SP, encoding='utf-8'))
assert chk['round_no'] == 676, 'state round_no self-check failed'

# --- heartbeat
HP = 'fleet/machines/bm-a.json'
h = json.load(open(HP, encoding='utf-8'))
now_epoch = int(time.time())
cpu = psutil.cpu_percent(interval=1.5)
mem = psutil.virtual_memory()
h['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
h['heartbeat_epoch_utc'] = now_epoch
h['last_seen'] = h['clock_read']
h['last_round'] = 'r675'
h['round_no'] = 676
h['round'] = 'r676'
h['cpu_pct'] = cpu
h['cpu_util_pct'] = cpu
h['free_ram_gb'] = round(mem.available / 1024**3, 1)
h['current'] = ('THEME-JUDGE-P2 redirect candidate prereg FROZEN (bl=0.75 R4-reserved family; '
                'T-169 s1 done same round: seed band 20589000 registered + D6 ADMIT 0.3682 + '
                'banned-gate rc0); s2 runner build next window; fund trio NULLS bm-b canonical in flight')
h['current_task'] = 'T-2026-10-04-169-P1 s1 frozen (THEME-JUDGE-P2 redirect prereg); next: s2 runner build'
h['last_action'] = 'r676: THEME-JUDGE-P2 prereg freeze + pre-freeze gates 4/4 green + S6 37/37'
h['task'] = 'T-2026-10-04-169-P1 s2 (runner theme_judge_p2.py build + pool entry)'
h['verdict'] = 'healthy'
json.dump(h, open(HP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
h2 = json.load(open(HP, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'] and '+' in h2['clock_read'], 'clock_read must be T-separated ISO8601'
print('state round_no=676 | heartbeat epoch int', h2['heartbeat_epoch_utc'], '| clock', h2['clock_read'])
