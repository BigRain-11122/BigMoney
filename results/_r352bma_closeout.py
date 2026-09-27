import json, time, datetime

now = datetime.datetime.now()
iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())

# 1) state-bm-a.json
state = json.load(open('state-bm-a.json', encoding='utf-8'))
state['round_no'] = 352
state['did'] = ("R352: launch-eve pure-maintenance round: orders 96/96 double-scan zero-unacked (round-start full diff + S7 fetch rescan) + decisions re-read through D-20260927-10 zero-new-line zero-action (D-04/D-09 BigMoney faces already executed-closed; council C-01 window 09-29 12:00 not yet) + smoke 25/25 + S6 33/33 rc=0 Sunday no-op family (audit v2.3 CLEAN flags=[] py 0.3% load_state pool-supply-gap + WM probe insufficient_history n=2 span 7.3min legal window-rebuild + daily 0-new-rows cutoff 09-24 + regime ORANGE shadow breadth 0.77 + scorecard 6/28/7 + clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 + collectors honest: lhb min-interval + heat weekend + futures/repo/options/sina_mf cutoff-covered zero-network + MF rank throttle 5.9min spawn-20:23 alive + AH spawn-throttle 5min detached-refresh continues + astock/rev_osc/alloc/fund_premium lane-guard no-op + ths same-day + fundamental 22.8h fresh-skip + b_layer pass + paper family idempotent live.paper/t35v PASS/t24 22-22/promo 0-22/aggr+grid+sysv1 no-op + export 09-24 6traders 18pos equity 5,996,645 + scorecard+report regen token=1 + build_status) + S3 closure = T-91 LAUNCH-EVE zero-gap re-verify (both accounts initial=equity=1,000,000 zero-pos zero-bars armed, first mark = first trading day strictly after 2026-09-24 = Mon 09-28; IntradayMarks Next Mon 09:25 Ready; bm-b bridge SIG/BARS-2026-09-24 in-tree) + bm-b watch HELD (heartbeat 20:02 28min + W2-A burn in-flight = busy-not-dead r341 law no takeover, ETA ~21:10) + S7 schtasks 4/4 + claw identical + post_review 3045 rows zero X")
state['verify'] = "smoke 25/25 + S6 33/33 rc=0 zero-masked + orders 96/96 both scans + schtasks 4/4 (IterationLoop Running / Watchdog Ready / Autofill Ready 20:40 / IntradayMarks Mon 09:25) + claw OK + watermark green + post_review zero X-rows + T-91 armed-state real-read (initial=equity=1e6, 0 pos, 0 bars)"
state['next'] = "Mon 09-28: T-91 s3 auto-fires 09:15 both accounts (IntradayMarks 09:25; first bar ~15:30 -> accrue + t35 verify + exports + sysv1 first marks via bm-b BARS evening); MF panel watch (EM block 30-min self-heal; complete = MF_IC_P1 unblock); AH refresh completion watch; bm-b W2-A finalize ETA ~21:10 escalate-if-passed -> D8 receive -> probe-once -> W2-B; council opinion window 09-29 12:00+; next 5x=R355 HANDOVER"
state['last_round_at'] = iso
state['current_task'] = "r352: launch-eve maintenance (S6 33/33, T-91 armed-verified zero-gap, orders 96/96)"
state['updated'] = iso
json.dump(state, open('state-bm-a.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

# 2) round report append
line = f"{iso} | R352 bm-a (dept:总经办+舰队·launch-eve 纯维护轮) | WM first-line verdict: GREEN (red=false @20:26 tick lane healthy; probe 20:29 insufficient_history n=2 span 7.3min legal window-rebuild, audit v2.3 CLEAN py 0.3% flags=[] load_state pool-supply-gap starvation=false; pool ready=1 W2-A lane=bm-b burning r341 no-touch) | did: S0 up-to-date; S0.5 orders 96/96 double-scan zero-unacked (round-start full diff + S7 fetch rescan count=96) + decisions through D-20260927-10 zero-new zero-action (D-04/D-09 BigMoney faces executed-closed; council C-01 window 09-29 12:00 not yet); S1 smoke 25/25; S6 33/33 rc=0 Sunday no-op family (daily 0-new-rows cutoff 09-24 Mid-Autumn Fri closed + regime ORANGE shadow hs300<MA200 #10 breadth 0.77 + scorecard 6strat/28trader/7port S=2 A=4 best VOLATILITY-CE-01 87.0 + clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 + collectors honest: lhb min-interval + heat weekend + futures/repo/options/sina_mf cutoff-covered + MF rank throttle 5.9min<30min spawn 20:23 + AH spawn-throttle 5min<30min detached continues + lane-guards astock/rev_osc/alloc/fund_premium stdout-no-op + ths same-day + fundamental 22.8h fresh-skip + b_layer all-gates-pass ok_static 3517 excluded 1705 + paper family idempotent: live.paper OK 2 bars shadow + t35v PASS zero-pending + t24 22/22 drift=0 + promo 0/22 honest + aggr/grid/sysv1 no-op + t35 export 09-24 6traders 18pos equity 5,996,645 + daily_scorecard + daily_report REPORT-2026-09-27 regen + build_status + token L2 1 leg delta=284); S3 closure = T-91 LAUNCH-EVE zero-gap re-verify: both accounts SYSTEM-V1+REV-OSC-STD initial=equity=1,000,000 zero-position zero-bars armed, first-mark=first trading day strictly after 2026-09-24 (=Mon 09-28), IntradayMarks schtask Next 2026-09-28 09:25 Ready, bm-b bridge SIG/BARS-2026-09-24 in-tree = Monday 09:15 auto-fire fully armed; bm-b watch HELD (heartbeat 20:02 28min + W2-A burn = busy-not-dead r341 no-takeover, ETA ~21:10); S7 schtasks 4/4 + claw CR-normalized identical + post_review 3045 rows zero X-rows + inbox 2 msgs both my outbound to bm-b left for pickup | verify: smoke 25/25 + S6 33/33 rc=0 zero-masked + orders 96/96 both scans + schtasks 4/4 + claw OK + watermark green + post_review zero X + T-91 armed real-read | next: Mon 09-28 T-91 s3 auto-fire 09:15 both accounts (first bar ~15:30 -> accrue+verify+exports; bm-b BARS-2026-09-28 evening -> sysv1 marks); MF panel watch; AH completion watch; bm-b W2-A finalize ETA ~21:10 escalate-if-passed -> D8 -> probe-once -> W2-B; council 09-29 12:00+; next 5x=R355 HANDOVER"
with open('logs/iteration-loop/round_reports-bm-a.md','a',encoding='utf-8') as f:
    f.write('\n'+line+'\n')

# 3) heartbeat
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['current_task'] = "r352 closed: launch-eve maintenance round (T-91 armed-verified zero-gap for Mon 09:15 auto-fire)"
hb['cpu_pct'] = 2.9
hb['cpu_util_pct'] = 2.9
hb['free_ram_gb'] = 50.5
hb['free_ram_mb'] = int(50.5*1024)
hb['idle_ram_gb'] = 50.5
hb['verdict'] = "healthy"
hb['task'] = "idle-round-done"
hb['round_no'] = 352
hb['round'] = 352
hb['loop_round'] = 352
json.dump(hb, open('fleet/machines/bm-a.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify epoch int + parseback
chk = json.load(open('fleet/machines/bm-a.json',encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read T-format'
print('state+report+heartbeat written; epoch', chk['heartbeat_epoch_utc'], 'type', type(chk['heartbeat_epoch_utc']).__name__, 'clock', chk['clock_read'])
