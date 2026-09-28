"""r382 bm-b: state round_no++ + heartbeat update (bm-c MSG-1205 wording correction absorbed)."""
import json, time, subprocess
from datetime import datetime, timedelta

# --- state.json round_no 381 -> 382 ---
s = json.load(open('state.json', encoding='utf-8'))
assert s['round_no'] == 381
s['round_no'] = 382
s['machine_id'] = 'bm-b'
s['note'] = ('r382: W4-GENERATE landed 12:27:41 (n=3810 distinct, G-VOL raw-face anchors '
             'production-validated = r381 fix closed) + harvest flip + screen-prep PASS + '
             'W4-SCREEN pool entry opened (waiting, flip=any machine RAM>=4GB 3-sample); census '
             'W2B slow-tail 4200/5620 alive no-kill ETA ~15:00; V2-P1 fused-inert (pre-fix sha) '
             'remaining latch=RAM window per MSG-1205 correction; S6 29 legs rc=0; smoke 25/25')
open('state.json', 'w', encoding='utf-8').write(json.dumps(s, ensure_ascii=False, indent=1))

# --- heartbeat fleet/machines/bm-b.json ---
now_local = datetime.now().astimezone().replace(microsecond=0)
iso = now_local.isoformat(timespec='seconds')
epoch = int(time.time())
out = subprocess.run(['powershell', '-NoProfile', '-Command',
                      "$os=Get-CimInstance Win32_OperatingSystem;[math]::Round($os.FreePhysicalMemory/1MB,2);"
                      "$c=Get-CimInstance Win32_Processor|Measure-Object -Property LoadPercentage -Average;"
                      "[math]::Round($c.Average,1)"], capture_output=True, text=True)
lines = [x for x in out.stdout.splitlines() if x.strip()]
free_ram, cpu_pct = float(lines[0]), float(lines[1])

h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
h['last_seen'] = iso
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso
h['current_task'] = ('r382 done: W4-GENERATE harvested (landed 12:27:41, n=3810 distinct, G-VOL raw-face '
                     'anchors {519,1523,1441} production-validated = r381 fix full closure; seven-source '
                     'exclusion consumed, grammar d498e9343ee57460, ledger wave-4 row) + screen-prep PASS '
                     '12:30:56 + TRIAL-LABOR-W4-SCREEN pool entry opened waiting (flip=any machine '
                     'RAM>=4GB 3-sample per r203; bm-b gated by census); census W2B slow-tail 4200/5620 '
                     'alive no-kill ETA ~15:00; next: W4-SCREEN flip+burn (he machine or post-census '
                     'self) -> screen-finalize -> W4-JUDGE entry; RAM window post-census -> judge-prep '
                     'W2/W3 + judge flips W1/W2/W3 eval + V2-P1 relaunch (fused-inert pre-fix sha, '
                     'remaining latch=RAM window per bm-c MSG-1205)')
h['cpu_cores'] = 16
h['free_ram_gb'] = free_ram
h['total_ram_gb'] = 23.92
h['cpu_util_pct'] = cpu_pct
h['round_no'] = 382
h['verdict'] = ('healthy: smoke 25/25, orders 99/99 dual-scan clean, S6 29 legs rc=0 (bma stale 2.5h '
                'takeover derives lawful); W4-GENERATE landed+harvested (r381 face-fix '
                'production-validated through real-fire anchors); W4-SCREEN entry open waiting for '
                'RAM>=4GB flip (census W2B 4200/5620 slow-tail holds 12.3GB no-kill, ETA ~15:00); '
                'V2-P1 fused-inert (pre-fix sha 880297a0; canonical 67946e83 unfused) remaining '
                'latch=RAM window post-census relaunch, zero new fix per bm-c MSG-1205; judge family '
                'W1/W2/W3 queued per MASS sec.9.1 + RAM r354 gate = lawful structural occupancy, not '
                'idle; watermark insufficient_history (15min window n=2 post-restart, honest); board 0 '
                'open; migration executor armed precheck waiting (Tuanjie editor), zero interference')
h['round'] = 382
h['loop_round'] = 382
h['idle_ram_gb'] = free_ram
h['idle_ram_mb'] = int(free_ram * 1024)
h['free_ram_mb'] = int(free_ram * 1024)
assert isinstance(h['heartbeat_epoch_utc'], int)
json.dump(h, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
v = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int)
assert 'T' in v['clock_read'] and v['clock_read'].endswith('+08:00')
print('state 382 + heartbeat OK; epoch=%d clock=%s free_ram=%.2f cpu=%.1f' % (epoch, iso, free_ram, cpu_pct))
