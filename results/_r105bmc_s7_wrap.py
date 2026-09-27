# r105 bm-c S7 wrap: S0.5 close rescan + round report append + state note + heartbeat refresh
# (single fresh time read -> all stamps; r96 fresh-read-at-write law; r104 lineage)
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
    now_iso + '｜R105｜bm-c (dept:engineering+fleet)｜'
    'WM verdict: green (red=false; this-round probe 20:48:25 py 0.5% py_low_board_clear legal-idle: board 0 open 93 tickets all claimed/done + job_list 0 + bandit_open 0 + bars_present=false Sunday + pool supply-gap disclosed; audit v2.3 CLEAN flags=[])｜'
    'S0 fetch ALIVE + FF onto bma R353 3dba365d (round-start clean tree zero local commits, no stash dance)｜'
    'S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan both) + orders-face cross-check: bma-R353 prose says 102/102 but tree enumeration=96 O-files=bma ack 96=bmb ack 96=bmc ack 96 four-face consistent = bma report-prose count slip, zero actual gap zero action + decisions review: D-20260927-08/09/10 new rows since 16:54 scan -- D-09 BigMoney conflict-resolve two-fix law ALREADY EXECUTED-CLOSED via bmc r84 (F-20260927-03 in-ledger, classify_conflicts.py canon + SKILL L34 both in tree), D-08 commercial-pricing council C-01 + D-10 receipt batch 6 = HQ/other-domain zero-BigMoney-action; C-01 council window 09-29 12:00 stands (seat-3 opinion delivered r102)｜'
    'S1 smoke 25/25｜S2 job_list 0 + fleet board 0 open (63 done 30 claimed, all lanes held) + next_pick status=claimed (moneyflow IC batch) not claimable + inbox 2 unread both bma->bmb W2-lane (MSG-1912 + MSG-2055), none to bm-c/ALL -> honest zero-action not moved｜'
    'S3 no claimable lane -> green-maintenance + 5x HANDOVER round: post_review full 3045-row verdict split YES 2444/WAIT 586/NO 15 with all 15 NO superseded by later YES re-derive of same id = zero unresolved red (review discipline zero P0) + 5x HANDOVER core: ledger head 286,551 read-verified zero-drift vs bma R350 baseline (_r295bmb_ledger_scan rerun INTERNAL_BALANCE_FAIL=0 DUP_BATCH_CONFLICTS=0, GAP 19 same-spectrum-as-prior, sina_construct_p1 +5 already inside R350 baseline = zero batch finalize this window) + bm-c window r101-105 zero new product rows -> HANDOVER row appended + S6 33/33 + schtasks health + claw identical｜'
    'S6 33/33 rc=0 Sunday no-op family via results/_r105bmc_s6_chain.ps1 (r104 lineage Copy-Item + header-diff 1 line verified): audit CLEAN v2.3 / probe py_low_board_clear py 0.5% / daily 0-new-rows cutoff 09-24 / regime ORANGE shadow breadth 0.77 / clock CALL-2026-09-24 ORANGE_COOL idempotent / lhb 30min-guard + heat weekend no-ops / futures cutoff-covers zero-network / 7 bma lane-guards (repo/options/moneyflow/sina_mf/ths/ah/system_v1) + 3 bmb lane-guards (astock/sigexp/alloc) + rev_osc sigexp stdout-only honest / fund_premium weekend no-op (bm-c lane, Mon 15:30 duty preflighted GREEN r101 + Monday re-seed raw snapshots) / fundamental 11.3h fresh skip / b_layer regen gates pass / live.paper OK / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent + grid no-markable-bar / export-2026-09-24 regen / scorecard 6+28+7 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 5/7 / token_meter L2 1 leg (~6450 tok today)｜'
    'S4 four-gate filter: zero-append (round clean: FF no conflict, no crash, no new pitlaw; anti-spam law)｜'
    'S7: claw CLAW_OK-identical + schtasks Loop Running (this session) Watchdog Ready 21:10 + state r105 + heartbeat fresh-epoch int + T-clock same-read + live stats (cpu/RAM/GPU) + push (non-FF resolve per canon: rebase-retry once, else origin machine/bm-c-r105 branch)｜'
    'next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium snapshot (bm-c lane, preflight GREEN r101 + Monday re-seed raw snapshots) (3) C-01 vote archival 09-29 12:00 (secretariat) (4) 10-01 month trio standing (preflighted r102) (5) r110 next 5x HANDOVER (bm-c window r106-110)｜'
    'evidence: results/_r105bmc_s6_chain.ps1 + _r105bmc_s7_wrap.py + _r295bmb_ledger_scan rerun + smoke 25/25 + S6 33/33 rc=0 + orders 96/96 + post_review NO-zero-unresolved + HANDOVER row + state-bm-c round_no=105 [via bm-c]'
)
p = repo + r'\logs\iteration-loop\round_reports-bm-c.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_line + '\n')

# ---- 2) state-bm-c.json note refresh ----
sp = repo + r'\state-bm-c.json'
state = json.load(io.open(sp, encoding='utf-8'))
state['round_no'] = 105
state['updated'] = now_iso[:16]
state['note'] = ('r105: 5x HANDOVER round (green maintenance). S0 FF onto bma R353 3dba365d; orders 96/96 double-scan zero-unacked '
                 '(bma-R353 prose 102 = count slip, four-face check 96/96/96/96 consistent); decisions D-08/09/10 reviewed '
                 '(D-09 BigMoney two-fix already executed-closed via bmc r84); smoke 25/25; board 0 open; post_review 15 NO all superseded = zero unresolved; '
                 'S6 33/33 rc=0 Sunday no-op family via _r105bmc_s6_chain.ps1; 5x HANDOVER: ledger head 286,551 zero-drift vs R350 baseline '
                 '(_r295bmb_ledger_scan FAIL=0 DUP=0, window r101-105 zero new product rows); inbox 2 unread bma->bmb not bm-c honest zero-action; '
                 'CODELY 9219B <=10KB. '
                 'next: Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane preflight GREEN + re-seed raw snapshots) + C-01 vote window 09-29 12:00 + 10-01 month trio (preflighted) + r110 5x HANDOVER')
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
hb['verdict'] = ('legal idle: board 0 open (93 tickets 63 done 30 claimed all lanes held), wm green red=false py_low_board_clear py 0.5%, audit CLEAN v2.3; '
                 'pool supply-gap disclosed (W2-A bm-b lane burning R31 no-touch, W2-B waiting double-dep); '
                 'r105=5x HANDOVER green maintenance (ledger 286,551 zero-drift vs R350 baseline + S6 33/33 + post_review zero-unresolved + orders 96/96 four-face check)')
hb['current_task'] = ('R105 done (5x HANDOVER: bm-c window r101-105 zero-drift ledger 286,551 + green maintenance S6 33/33 + post_review zero-unresolved); '
                      'next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane + re-seed raw snapshots) + C-01 vote archival 09-29 + r110 5x HANDOVER')
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify: epoch int type + orders_ack 96 + state round ----
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert len(chk.get('orders_ack', [])) == 96, 'orders_ack drift'
st = json.load(io.open(sp, encoding='utf-8'))
assert st['round_no'] == 105
print('WRAP OK r105 bm-c | now=', now_iso, '| epoch=', now_epoch, '| ack=96 | rescan unacked=0 | '
      'cpu=', cpu_pct, 'free_ram_gb=', free_gb, 'gpu_free_mb=', gpu_free, '| report appended')
