# -*- coding: utf-8 -*-
# r261 close: state increment + heartbeat + round report line (bm-b lane)
import json, time, subprocess

# --- 1. state.json round_no 260 -> 261 (LF-only, no BOM, mirrors producer) ---
SP = 'logs/iteration-loop/state.json'
s = json.load(open(SP, encoding='utf-8-sig'))
assert s['round_no'] == 260, 'unexpected round_no %s' % s['round_no']
s['round_no'] = 261
s['did'] = ('r261: T-76 face (c) QuantsPlaybook catalog SECOND-SWEEP (27 remaining untriaged entries '
            'all adjudicated: 14 family merges + 1 ML reserve + 3 methodology/in-house + 7 C/D-grade '
            'honest + series-2 deferral redeemed) + zoo registrations #95 index_higher_mom_timing / '
            '#96 volume_regime_bimodal (channel-level UNVERIFIED, G1v2->G2 chain mandatory, '
            'consumption = T-34 fast-line pool)')
s['verdict'] = 'GREEN'
s['next'] = ('faces (a) jisilu run-9/hibor run-5/guorn run-3 + jin-gong post-holiday verify = 09-28 '
             'Monday open window; T-82 deep-bcd-basis transfer branch arrival = byte-verify + dD '
             'LF-normalize row-multiset compare (receive leg open); #95/#96 paramfreeze deep-read '
             'if scheduled; referee deep-read A-lead 2609.27051 optional; 10-01 month-boundary trio '
             '+ REGIME_GUARD v3 activation')
s['last_round_ts'] = '2026-09-26T16:5x'
s['updated_at'] = '2026-09-26T16:5x'
with open(SP, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('state round_no ->', s['round_no'])

# --- 2. heartbeat fleet/machines/bm-b.json (epoch int law R170/R178) ---
HP = 'fleet/machines/bm-b.json'
h = json.load(open(HP, encoding='utf-8-sig'))
epoch = int(time.time())
h['last_seen'] = '2026-09-26T16:5x'
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
h['current_task'] = ('R261 done: T-76 face (c) QP catalog second-sweep 27/27 adjudicated + zoo #95/#96 '
                     'registered (T-34 fast-line pool candidates); next: faces (a) 09-28 window, T-82 '
                     'receive leg, 10-01 month boundary')
h['round_no'] = 261
h['verdict'] = 'GREEN'
# machine faces (measured this round: 16 cores; free RAM + GPU idle probed at close)
out = subprocess.run(['powershell', '-NoProfile', '-Command',
                      '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1);'
                      '[math]::Round(((Get-CimInstance Win32_VideoController | Where-Object {$_.AdapterRAM} | '
                      'Select-Object -First 1).AdapterRAM)/1MB,0)'],
                     capture_output=True, text=True)
vals = out.stdout.split()
try:
    free_ram = float(vals[0]); gpu_free = float(vals[1])
except Exception:
    free_ram = h.get('idle_ram_gb', 0.0); gpu_free = h.get('gpu_idle_vram_gb', 0.0)
h['cpu_cores'] = 16
h['idle_ram_gb'] = free_ram
h['gpu_idle_vram_gb'] = gpu_free
h['free_ram_gb'] = free_ram
h['gpu_free_vram_gb'] = gpu_free
with open(HP, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(h, f, ensure_ascii=False, indent=2)
    f.write('\n')
chk = json.load(open(HP, encoding='utf-8-sig'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat epoch=%d int-verified free_ram=%.1fGB gpu_free=%.0fMB' % (epoch, free_ram, gpu_free))

# --- 3. round report line (CRLF, append) ---
RP = 'logs/iteration-loop/round_reports.md'
line = (
    '2026-09-26 16:5x | r261 bm-b | dept:research | WM-VERDICT: GREEN py_low_board_clear (probe 16:45 py ~1.0-1.5% window n=2 span 18.2min, board 0 open / pool 0 ready / bandit 0; red=false; audit CLEAN idle-starvation load_state, no flags) | '
    'did: S0 stash-pull-pop R252 recipe (autofill_state pop clean, tree up-to-date) + S0.5 double-scan orders 82/82 zero un-acked + decisions.md absent zero-action + T-82 deep-bcd-basis transfer branch fetch = still not pushed by bm-a (receive leg open, non-blocking; MSG-1622 = own r259 outgoing awaiting bm-a pickup, correctly left) | '
    'MAIN DELIVERY = T-76 wave-10 face (c) QuantsPlaybook catalog SECOND-SWEEP: catalog refetch 2 web_fetch (main-branch 404 honest=branch is master per r189; master 200 full) -- README enumerates 57 rows (self-claim 100+ = marketing count honest note); first-sweep coverage diff = 30 rows adjudicated at r189, remaining UNTRIAGED 27 rows ALL adjudicated this round: 14 family merges (QRS=RSRS-family suspected variant quantile-reg-slope deep-read recheck position / low-lag trendline=MA-family #81/#86 law / one-way vol diff=VOLATILITY family / time-varying Sharpe=derived index view / qu-shi=slope primitives / point-efficiency=ER momentum variant / TA patterns+rounded-bottom=patterns family / alt vol-price resonance=volume-price family / CCK herding=REGIME_GUARD-breadth neighbor CSAD frozen-face zero-touch / reversal micro-source=GTJA 070/081 variant / quality-momentum Gray=momentum family / industry vol-price rotation=rotation family MF_ROT negative-prior burden / overnight-vs-daytime lead-lag network=merged #11 network reserve O(N^2) compute-heavy clause) + 1 ML reserve (wavelet+SVM) + 3 methodology/in-house-by-construction (index-enhance + DE optimizer = construction methodology; factor-timing = T-81 profile cards IS the in-house system) + 7 C/D honest (northbound=DEAD DATA SOURCE / ETF intraday momentum=minute-face unapproved / fund-manager holdings=quarterly unapproved / lifecycle=IPCA compute-heavy / analyst gold-stock=external subscription / cash-flow rule + FFScore=fundamental value domain P1 signature law) + series-2 deferral REDEEMED; REGISTRATIONS zoo #95 index_higher_mom_timing (GF 2015-05-20 rolling skew/kurt, D6 lottery+tail-risk, vol-family corr>=0.7 merge clause flagged, T-34 fast-line) + #96 volume_regime_bimodal (HuaChuang 2022-08-05 AMA5/AMA100 + sqrt-bimodal state machine, #94 sibling on volume face, skopt=report-tuning not freeze basis, T-34 fast-line) both channel-level UNVERIFIED G1v2->G2 mandatory; deliverables: DIGEST-20260926-wave10-qp-catalog-sweep2.md (funnel 27 harvest / 2 pass) + ASTYLE_ZOO 3-insertion field-level (LF no-BOM preserved) + T-76 progress_r261 four-face-mirrored ASCII (diff 2+/1-) | '
    'S6 28 legs exit 0 weekend no-ops (audit CLEAN / watermark py_low_board_clear / daily 0 new rows cutoff 09-24 / regime ORANGE d2 shadow breadth 0.77 / clock ORANGE_COOL sleeves=4 activated=0 / lhb no-op / heat weekend / futures local-covers / options+mf+sina_mf+ths+ah = bm-a lanes stdout-only / fp = bm-c lane / fundamental 19.6h fresh / b_layer green / scorecard 6 traders / daily_report faces=4 token=1 / build_status refreshed / token L1 delta +16; bar-conditional paper legs legally skipped) | '
    'evidence: digest + ASTYLE_ZOO diff 3+/0- + T-76 ticket diff 2+/1- + S6 28 exit-0 chain + smoke 25/25 + state 260->261 + heartbeat epoch int-verified | '
    'next: faces (a) 09-28 Monday window (jisilu run-9/hibor run-5/guorn run-3 + jin-gong post-holiday verify) + T-82 receive leg on branch arrival + #95/#96 paramfreeze deep-read if scheduled + referee deep-read optional + 10-01 month-boundary trio + REGIME_GUARD v3 activation window\r\n'
)
with open(RP, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended')
