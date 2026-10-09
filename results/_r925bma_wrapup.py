import json, time, datetime, subprocess, re

NOW = datetime.datetime.now().astimezone()
ISO = NOW.strftime('%Y-%m-%dT%H:%M:%S') + ('+' if NOW.utcoffset() >= datetime.timedelta(0) else '-') + NOW.strftime('%H:%M')
EPOCH = int(time.time())

# ---------- 1. state-bm-a.json: round_no +1 + current face ----------
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
prev_round = st.get('round_no', 0)
st['round_no'] = prev_round + 1
st['last_round'] = prev_round
st['current'] = 'r%d maintenance round: S6 39/39 gates green, CEO faces refreshed, W202 seat MSG processed' % st['round_no']
st['current_task'] = 'W202 freeze next (W201 pattern) + moneyflow IC batch awaits panel'
st['did'] = 'S0 pull/0-0; S0.5 orders 0-unacked+DEC unchanged; S1 smoke 49/49; S6 39/39 rc0 (update_daily probe_no_new sina 10-09 pending; moneyflow+AH detached spawn; options gate retired face per O-20261009-1105); CEO pages: REPORT-2026-10-09/LIVE-2026-10-09/daily_scorecard/CALL-2026-09-30; W202 seat MSG processed->processed/; S7 loop pin8+watchdog+claws+attrition CLEAN+HANDOVER fresh'
st['last_action'] = 'r%d wrap-up commit' % st['round_no']
st['last_artifact'] = 'docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/LIVE-2026-10-09.md (19:44)'
st['clock_read'] = ISO
st['heartbeat_epoch_utc'] = EPOCH
st['ts'] = ISO
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- 2. heartbeat fleet/machines/bm-a.json ----------
hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
# resource snapshot
r = subprocess.run(['powershell', '-NoProfile', '-Command',
    "$os=Get-CimInstance Win32_OperatingSystem; $cpu=(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; $ram=[math]::Round(($os.FreePhysicalMemory/$os.TotalVisibleMemorySize)*100,1); Write-Output \"$cpu $ram\""], capture_output=True, text=True)
m = re.match(r'([\d.]+) ([\d.]+)', (r.stdout or '').strip())
cpu_pct, ram_free = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
hb['last_seen'] = ISO
hb['current_task'] = 'W202 freeze (next window) + moneyflow IC batch when panel completes'
hb['cpu_cores'] = 32
hb['cpu_pct'] = cpu_pct
hb['free_ram_pct'] = ram_free
hb['gpu_free_vram_gb'] = 0.29
hb['verdict'] = 'green (watermark red=false; smoke 49/49; S6 39/39 rc0; engine alive idle)'
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = ISO
hb['ts'] = ISO
hb['active'] = 'r%d maintenance: gates green, CEO pages refreshed, W202 seat consumed' % st['round_no']
hb['recent_artifact'] = 'docs/daily_report/REPORT-2026-10-09.md + docs/live_usage/LIVE-2026-10-09.md (2026-10-09 19:44)'
hb['next_milestone'] = 'W202 five-face freeze->engine self-burn->finalize (W201 r923 pattern) + moneyflow IC reference batch on panel completion (window <=48h)'
# orders_ack unchanged (zero unacked this round); keep as-is
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
v = json.load(open(hp, encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'

# ---------- 3. round report line ----------
LINE = ('{ts} | r{r} | maintenance: S0 autostash up-to-date 0/0; S0.5 orders 0-unacked + DEC sha UNCHANGED(31e85972); '
        'round-zero orphan=0; S1 smoke 49/49 PASS; S2 board no-open (W17 9-shards bm-c lane respected); '
        'S3 watermark green + engine alive idle + idle_trigger green_idle=false(RAM low, no claim duty); '
        'W202 seat MSG consumed->processed/ (own-lane r924 publication); '
        'S6 39/39 rc0: reconcile ZERO-DRIFT streak5 / compute_audit clean / update_daily probe_no_new (sina 10-09 bar pending, self-heal legs cover) / '
        'moneyflow+AH detached refresh spawned / options gate retired-face per O-20261009-1105 / paper legs no-op at cutoff 10-08 / '
        'CEO faces: daily_scorecard.html(6 traders) + REPORT-2026-10-09.md faces=5 + LIVE-2026-10-09.md + CALL-2026-09-30 cell=ORANGE_COOL + export-2026-10-08.json + dashboard_status.js; '
        'S7 loop pin=8 no-op + watchdog registered + precommit/prepush claws + attrition CLEAN(4 files) + HANDOVER verified fresh(17:19); '
        '| evidence: results/update_status.json cutoff 2026-10-08 / results/daily_scorecard.html / docs/daily_report/REPORT-2026-10-09.md / _orphan_face_probe.bm-a.json py27/orph0 '
        '| next: W202 five-face freeze+prereg registry edits (pit-engine-freeze pre-read) -> engine self-burn -> finalize; moneyflow IC batch on panel complete; 本地未达 origin commit 数=0').format(ts=ISO, r=st['round_no'])
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write('\n' + LINE + '\n')
print('round_no ->', st['round_no'])
print('heartbeat epoch int ok, cpu=%.0f%% ram_free=%.1f%%' % (cpu_pct, ram_free))
print('report line appended, len', len(LINE))
