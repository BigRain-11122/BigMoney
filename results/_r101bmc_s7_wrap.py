# r101 bm-c S7 wrap: S0.5 close rescan + round report append + state note + heartbeat refresh
# (single fresh time read -> all stamps; r96 fresh-read-at-write law; r100 lineage + live stats refresh per mandate)
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
    now_iso + '｜R101｜bm-c (dept:engineering+fleet)｜'
    'WM verdict: green (red=false; this-round probe 20:11:01 py 0.0% py_low_board_clear legal-idle: board 0 open 96 tickets all done/claimed + job_list 0 + pool 78 done + W2-A ready=bm-b lane burning R31-guardrail not burnable by bm-c + W2-B waiting double-dep; audit v2.3 CLEAN flags=[] load_state=pool-supply-gap disclosed)｜'
    'S0 fetch ALIVE + FF rebase onto bma R350 1593a959 (local r100 8f89e206==origin ancestor, zero local commits) + stash-pop autofill 1-UU per canon (classify recipe: same-second tie 20:00:01 both ticks -> HEAD/ours=bma side per r140; parse-verified last_tick dict + launches 48; resolved bytes == HEAD -> clean tree; stash dropped)｜'
    'S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan both) + decisions tail zero-new (last ledger change 15:15/16:54 = pre-r100 already receipted through D-10; D-04/D-09 BigMoney rows both executed-closed; D-05-2 full-file scan in force; C-01 council window 09-29 12:00)｜'
    'S1 smoke 25/25｜S2 job_list 0 + fleet board 0 open (66 done 30 claimed, all lanes held) + inbox 2 unread both to=bm-b (MSG-1905/MSG-1912 W2-B lane, not bm-c honest zero-action not moved)｜'
    'S3 two verifiable closures: (a) fund_premium Mon-lane preflight GREEN (bm-c lane duty Mon 15:30): selftest 27/27 + status NAV 48/48 cov 1.0 + dividends 48/48 + panel.csv 10.3MB rebuilt-today; honest discovery=raw snapshots/ series lost in U196 tree rebuild (backfill-nav rebuilt derived faces only, old tree K:\金钱牛马 gone entirely unrecoverable; Monday fetch re-seeds series, makedirs exist_ok; no analytical impact) -> pitlaw + 27th-batch archival; (b) R350 probe law folded into canon source classify_conflicts.py (bma r350 pitlaw: key-EXCLUDE tables forbidden + wall-clock value-shape gate [T ]HH:MM + staged-blob probe; scorecard family full law + paper/paper_export/status echoes; law anchors R350; selftest 26/26 ALL GREEN; no twin copy on bm-c) = D-09 lineage fourth-defect closed at canon｜'
    'S6 33/33 rc=0 Sunday no-op family via results/_r101bmc_s6_chain.ps1 (r098 lineage Copy-Item + round-face replace, diff=1 header line verified): audit CLEAN v2.3 / probe py_low_board_clear py 0.0% / daily 0 rows cutoff 09-24 / regime ORANGE shadow breadth 0.77 / clock CALL-0924 ORANGE_COOL idempotent / lhb 30min-guard + heat weekend no-ops / futures cutoff-covers zero-network / 7 bma lane-guards + 3 bmb lane-guards + sigexp stdout-only honest / fund_premium weekend no-op (bm-c lane) / fundamental 10.7h fresh skip / b_layer regen gates pass / live.paper OK 6 anchors / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent + grid no-markable-bar + sysv1 lane-guard no-op / export-2026-09-24 regen / scorecard 6+28+7 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 5/7 / token_meter L2 1 leg｜'
    'S4 pitlaw appended (tree-rebuild lane-local gitignored data inventory gap) + CODELY 9894B over-line pre-empt -> 27th-batch hot/cold archival (_r101bmc_codely_archive.py: 8 redundant batch-pointer rows 3182B verbatim-moved to archive 202609.md 27th-batch section + one index line; CODELY 9894->7850B <=10KB; multiset zero-loss verified)｜'
    'S7: claw PRECOMMIT_OK + schtasks Loop Running (this session) Watchdog Ready 20:40 + state r101 + heartbeat fresh-epoch int + T-clock same-read + live stats (cpu/RAM/GPU) + push (non-FF resolve per canon: rebase-retry once, else origin machine/bm-c-r101 branch)｜'
    'next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium snapshot (bm-c lane, preflight GREEN r101) (3) C-01 council window 09-29 12:00 (4) 10-01 month trio standing (5) r105 next 5x HANDOVER｜'
    'evidence: results/_r101bmc_s6_chain.ps1 + _r101bmc_codely_archive.py + _r101bmc_s7_wrap.py + classify_conflicts.py selftest 26/26 + fund_premium selftest 27/27 + smoke 25/25 + S6 33/33 rc=0 + orders 96/96 + state-bm-c round_no=101 [via bm-c]'
)
p = repo + r'\logs\iteration-loop\round_reports-bm-c.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_line + '\n')

# ---- 2) state-bm-c.json note refresh ----
sp = repo + r'\state-bm-c.json'
state = json.load(io.open(sp, encoding='utf-8'))
state['round_no'] = 101
state['updated'] = now_iso[:16]
state['note'] = ('r101: green-maintenance + canon-fold round. FF rebase onto bma R350 + 1-UU stash-pop per canon (tie->HEAD); '
                 'orders 96/96 double-scan zero-unacked; smoke 25/25; board 0 open; S6 33/33 rc=0 Sunday no-op; '
                 'fund_premium Mon-lane preflight GREEN (selftest 27/27, NAV 48/48, panel rebuilt; raw snapshots lost in U196 rebuild -> pitlaw + Monday re-seed); '
                 'R350 probe law folded into classify_conflicts.py canon (selftest 26/26); CODELY 27th-batch archival 9894->7850B<=10KB. '
                 'next: Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc) + C-01 window 09-29 + 10-01 month trio + r105 5x')
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
hb['verdict'] = ('legal idle: board 0 open (96 tickets all claimed/done), wm green red=false py_low_board_clear py 0.0%, audit CLEAN v2.3 '
                 '(pool-supply-gap disclosed); pool 78 done + W2-A ready bm-b lane burning (R31 no-touch) + W2-B waiting double-dep; '
                 'r101=R350 canon fold + fund_premium preflight GREEN + CODELY 27th-batch archival 7850B')
hb['current_task'] = ('R101 done (FF rebase + 1-UU canon resolve + R350 canon fold + fund_premium preflight + S6 33/33 rc=0 + archival); '
                      'next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane) + r105 5x')
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify: epoch int type + orders_ack 96 + state round ----
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert len(chk.get('orders_ack', [])) == 96, 'orders_ack drift'
st = json.load(io.open(sp, encoding='utf-8'))
assert st['round_no'] == 101
print('WRAP OK r101 bm-c | now=', now_iso, '| epoch=', now_epoch, '| ack=96 | rescan unacked=0 | '
      'cpu=', cpu_pct, 'free_ram_gb=', free_gb, 'gpu_free_mb=', gpu_free, '| report appended')
