# r104 bm-c S7 wrap: S0.5 close rescan + round report append + state note + heartbeat refresh
# (single fresh time read -> all stamps; r96 fresh-read-at-write law; r103 lineage)
import json, time, datetime, io, os, subprocess

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now_epoch = int(time.time())
now_iso = datetime.datetime.fromtimestamp(now_epoch).astimezone().isoformat(timespec='seconds')  # T-sep + tz offset

# ---- 0) S0.5 close rescan: orders set-diff vs heartbeat ack ----
hp = repo + r'\fleet\machines\bm-c.json'
hb = json.load(io.open(hp, encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
files = {f for f in os.listdir(repo + r'\fleet\orders') if f.startswith('O-') and f.endswith('.md')}
unacked = sorted(files - ack)
assert not unacked, 'UNACKED ORDERS PRESENT: %s' % unacked

# ---- 0b) live machine stats (fresh at write) ----
cpu_pct = None; free_gb = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_gb = round(psutil.virtual_memory().available / (1024**3), 1)
except Exception:
    pass
gpu_free = None
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
    if out:
        gpu_free = int(out[0])
except Exception:
    pass

# ---- 1) round report line append (append-only) ----
report_line = (
    now_iso + '｜R104｜bm-c (dept:engineering+fleet)｜'
    'WM verdict: green (red=false; this-round probe 20:39:09 py 0.0% py_low_board_clear legal-idle: board 0 open 93 tickets all claimed/done (63 done 30 claimed; honest delta vs r103 count 96->93 = ticket closes in git history, zero open either way) + job_list 0 + bars_present=false Sunday + pool state disclosed supply-gap; audit v2.3 CLEAN)｜'
    'S0 fetch ALIVE + FF onto bma R352 b1fda925 (round-start clean tree zero local commits, no stash dance)｜'
    'S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan both) + decisions mtime 16:54 zero-new (receipted through D-10; D-04/D-09 BigMoney rows executed-closed; C-01 council seat-3 opinion delivered r102, vote window 09-29 12:00 stands)｜'
    'S1 smoke 25/25｜S2 job_list 0 + fleet board 0 open (63 done 30 claimed, all lanes held) + inbox 2 unread both bma->bmb W2-lane (MSG-1912 D8-transfer + MSG-2055 mirror-landed receipt), none to bm-c/ALL -> honest zero-action not moved｜'
    'S3 no claimable lane -> green-maintenance round: post_review REPORT-20260927 verdict x0 (v44/janto5 zero P0 rows; T-28 J4 honest-negative line is judged-face record not action item) + verifiable closure = S6 chain re-run 33/33 rc=0 + schtasks health (Loop Running this-session / Watchdog Ready) + precommit claw CLAW_OK identical + CODELY 9582B <=10KB hard line verified｜'
    'S6 33/33 rc=0 Sunday no-op family via results/_r104bmc_s6_chain.ps1 (r103 lineage Copy-Item + header-diff 1 line verified): audit CLEAN v2.3 / probe py_low_board_clear py 0.0% window avg 0.0 / daily 0-new-rows cutoff 09-24 / regime ORANGE shadow breadth 0.77 / clock CALL-2026-09-24 ORANGE_COOL idempotent / lhb 30min-guard + heat weekend no-ops / futures cutoff-covers zero-network / 7 bma lane-guards (repo/options/moneyflow/sina_mf/ths/ah/system_v1) + 3 bmb lane-guards (astock/sigexp/alloc) + rev_osc sigexp stdout-only honest / fund_premium weekend no-op (bm-c lane, Mon 15:30 duty preflighted GREEN r101 + Monday re-seed raw snapshots) / fundamental 11.2h fresh skip / b_layer regen gates pass / live.paper OK / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent + grid no-markable-bar / export-2026-09-24 regen / scorecard 6+28+7 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 5/7 / token_meter L2 1 leg (~6450 tok today)｜'
    'S4 four-gate filter: zero-append (round clean: FF rebase no conflict, no crash, no new pitlaw; anti-spam law)｜'
    'S7: claw CLAW_OK-identical + schtasks Loop Running (this session) Watchdog Ready 20:40 + state r104 + heartbeat fresh-epoch int + T-clock same-read + live stats (cpu/RAM/GPU) + push (non-FF resolve per canon: rebase-retry once, else origin machine/bm-c-r104 branch)｜'
    'next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium snapshot (bm-c lane, preflight GREEN r101 + Monday re-seed raw snapshots) (3) C-01 vote archival 09-29 12:00 (secretariat) (4) 10-01 month trio standing (preflighted r102) (5) r105 next 5x HANDOVER (bm-c window r101-105)｜'
    'evidence: results/_r104bmc_s6_chain.ps1 + _r104bmc_s7_wrap.py + smoke 25/25 + S6 33/33 rc=0 + orders 96/96 + post_review x0 + state-bm-c round_no=104 [via bm-c]'
)
p = repo + r'\logs\iteration-loop\round_reports-bm-c.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_line + '\n')

# ---- 2) state-bm-c.json note refresh ----
sp = repo + r'\state-bm-c.json'
state = json.load(io.open(sp, encoding='utf-8'))
state['round_no'] = 104
state['updated'] = now_iso[:16]
state['note'] = ('r104: green-maintenance round. S0 FF onto bma R352 b1fda925; orders 96/96 double-scan zero-unacked; '
                 'decisions 16:54 zero-new; smoke 25/25; board 0 open (63 done 30 claimed); post_review x0; '
                 'S6 33/33 rc=0 Sunday no-op family via _r104bmc_s6_chain.ps1; inbox 2 unread = bma->bmb W2-lane, none to bm-c honest zero-action; '
                 'CODELY 9582B <=10KB. '
                 'next: Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane preflight GREEN + re-seed raw snapshots) + C-01 vote window 09-29 12:00 + 10-01 month trio (preflighted) + r105 5x HANDOVER')
state['last_round_ts'] = now_iso
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- 3) heartbeat fleet/machines/bm-c.json (fresh epoch int + clock_read same-read + live stats) ----
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = now_epoch          # python int -> JSON int (smoke F7)
hb['clock_read'] = now_iso
if cpu_pct is not None:
    hb['cpu_util_pct'] = cpu_pct
    hb['cpu_pct'] = cpu_pct
if free_gb is not None:
    hb['free_ram_gb'] = free_gb
if gpu_free is not None:
    hb['gpu_free_vram_mb'] = gpu_free
hb['verdict'] = ('legal idle: board 0 open (93 tickets 63 done 30 claimed all lanes held), wm green red=false py_low_board_clear py 0.0%, audit CLEAN v2.3; '
                 'pool supply-gap disclosed (W2-A bm-b lane burning R31 no-touch, W2-B waiting double-dep); '
                 'r104=green maintenance (S6 33/33 + post_review x0 + zero-unacked double-scan)')
hb['current_task'] = ('R104 done (green maintenance: S6 33/33 rc=0 + post_review x0 + double-scan zero-unacked); '
                      'next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane + re-seed raw snapshots) + C-01 vote archival 09-29 + r105 5x HANDOVER')
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify: epoch int type + orders_ack 96 + state round ----
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert len(chk.get('orders_ack', [])) == 96, 'orders_ack drift'
st = json.load(io.open(sp, encoding='utf-8'))
assert st['round_no'] == 104
print('WRAP OK r104 bm-c | now=', now_iso, '| epoch=', now_epoch, '| ack=96 | rescan unacked=0 | '
      'cpu=', cpu_pct, 'free_ram_gb=', free_gb, 'gpu_free_mb=', gpu_free, '| report appended')
