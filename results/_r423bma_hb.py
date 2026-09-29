import json
import time
import psutil

p = 'fleet/machines/bm-a.json'
h = json.load(open(p, encoding='utf-8'))
now_iso = '2026-09-29T09:53:40+08:00'
epoch = int(time.time())

cpu = psutil.cpu_percent(interval=0.5)
vm = psutil.virtual_memory()
h['machine_id'] = 'bm-a'
h['last_seen'] = now_iso
h['clock_read'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['round_no'] = 423
h['current_task'] = 'r423 closed: board-empty verification + anti-dup triple hold (W7 slice bm-b origin-first honored / v4 eval found landed by bm-c r204 pre-write / W8 gated); next=W7 slice-2 watch + 10-01 month-first triple'
h['cpu_cores'] = psutil.cpu_count(logical=True)
h['cpu_pct'] = cpu
h['cpu_util_pct'] = cpu
h['free_ram_gb'] = round(vm.available / 1024**3, 1)
h['idle_ram_gb'] = round(vm.available / 1024**3, 1)
h['cores'] = psutil.cpu_count(logical=True)
h['verdict'] = ('r423 green: smoke 26/26; anti-dup triple hold (v4 eval cancelled pre-write = bm-c r204 already landed @08:1x, verdict v4-not-opened; '
                'W7 runner slice = bm-b origin-first claim honored, slice-1a landed 580,608-grammar; W8 window gated on W7 full-chain landing; '
                'post_review 3731 rows zero-X; T-106 s4 national-team arm = NOT_SUPPORTED honest negative); S6 37 legs exit-0 '
                '(dualrun bm-a streak 3/3 MET, flip gate NOT READY = bm-b streak 0 lane; regime ORANGE d2; live.paper enforce->shadow date-gate honest; '
                't35 equity 5,988,732; ceo_live ORANGE cap50 COOL); S7 trio green (pin=8 no-op, watchdog Ready, claw installed); '
                '2 ALL inbox MSGs archived; state 423')
json.dump(h, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify per law
v = json.loads(open(p, encoding='utf-8').read())
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in v['clock_read'] and ' ' not in v['clock_read'], 'clock_read must be T-separated'
print('heartbeat OK: epoch(int)=', v['heartbeat_epoch_utc'], '| clock=', v['clock_read'], '| round=', v['round_no'], '| cpu=', cpu)
