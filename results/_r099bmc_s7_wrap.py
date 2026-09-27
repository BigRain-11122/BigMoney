# r99 bm-c S7 wrap: S0.5 rescan + round report append + state update + heartbeat refresh (single fresh time read -> all stamps; r96 pitlaw fresh-read-at-write law; r98 lineage)
import json, time, datetime, io, os

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
now_epoch = int(time.time())
now_iso = datetime.datetime.fromtimestamp(now_epoch).astimezone().isoformat(timespec='seconds')  # T-separator, tz offset

# ---- 0) S0.5 close rescan: orders set-diff vs heartbeat ack ----
hp = repo + r'\fleet\machines\bm-c.json'
hb = json.load(io.open(hp, encoding='utf-8'))
ack = set(hb.get('orders_ack', []))
files = {f for f in os.listdir(repo + r'\fleet\orders') if f.startswith('O-') and f.endswith('.md')}
unacked = sorted(files - ack)
assert not unacked, 'UNACKED ORDERS PRESENT: %s' % unacked  # round-start diff was zero; abort-wrap if new order landed mid-round

# ---- 1) round report line append (append-only) ----
report_line = (
    now_iso + '｜R99｜bm-c (dept:engineering+fleet)｜'
    'WM verdict: green (red=false; this-round probe 19:22:49 py 0.0% py_low_board_clear legal-idle: board 0 open 96 tickets all done/claimed + job_list 0 + bandit next_pick=claimed moneyflow-IC panel-wait + pool 1 ready CENSUS-FUS-S2-W2A=bm-b lane R31-guardrail not burnable by bm-c)｜'
    'S0 pull --rebase 5min-zero-output auto-cancelled (GitHub inbound stall, known pitlaw family); no index.lock / no rebase residue; 3 fetch-tail procs (unpack-objects) left alive not touched (not deadlock, zero-kill per pitlaw); gh api const-channel probe: origin +3 bma R345 commits (19:14-19:17 +0800 window, W2-B runner build + S6 Sunday family) = local behind origin, resolved at S7 push leg｜'
    'S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan both) + decisions tail: D-20260927-04 (BigMoney re-review anchor hot-ticket ban) + D-20260927-09 (conflict-resolve two-fix adoption) both already executed-receipted closed (bmc r84 three-proof, zero new action) + D-20260927-05-2 scan-face notice compliant (S0.5 full-file scan in force) + D-20260927-10 zero-new = zero unprocessed BigMoney-relevant lines｜'
    'S1 smoke 25/25｜S2 job_list 0 + fleet board 0 open (63 done 30 claimed, all lanes held) + inbox 1 unread=MSG-20260927-1905 to=bm-b (not bm-c, honest zero-action not moved)｜'
    'S3 no claimable lane: W2-A census=bm-b burning (r341 dual-evidence no-touch) + MF IC advisory=claimed panel-wait + T-91 s3 auto-fires Mon 09:15 (bma) -> queue recheck zero-duplicate-space: J12 town v1.0 shipped + ten buildings aligned org_chart v5/v7 (r277 close note, incl 2026-09-27 research-dept seat annotation) + J13 L2 alive (token_meter leg) + J10/J18b wired + Optuna gated (validated-count trigger unmet) -> green maintenance per protocol｜'
    'S6 33/33 rc=0 Sunday no-op family via results/_r098bmc_s6_chain.ps1 (r98 lineage reuse, zero rebuild): audit CLEAN v2.3 / probe py_low_board_clear / daily cutoff 09-24 / regime ORANGE shadow breadth 0.77 / clock CALL-0924 ORANGE idempotent / lhb 30min-guard + heat weekend no-ops / futures cutoff-covers zero-network / 7 bma lane-guards (repo/options/moneyflow/sina_mf/ths/ah/system_v1) + 3 bmb lane-guards (astock/sigexp/alloc) stdout-only honest / fund_premium weekend no-op (bm-c lane) / fundamental 9.9h fresh skip / b_layer regen gates pass / live.paper OK 6 anchors / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent + grid no-markable-bar / export-2026-09-24 regen / scorecard 6+28+7 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 5/7 / token_meter L2 1 leg｜'
    'S4 no new pitlaw this round (four-gate filter: pull-stall + fetch-tail disposal both covered by existing pitlaw entries, anti-spam zero append)｜'
    'S7: claw PRECOMMIT_OK + schtasks Loop Running (this session) Watchdog Ready 19:40 + state r99 + heartbeat fresh-epoch int + T-clock same-read + push (non-FF resolve per canon: rebase-retry once, else origin machine/bm-c-r99 branch)｜'
    'next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium snapshot (bm-c lane) (3) C-01 council window 09-29 12:00 (4) 10-01 month trio standing (5) r100 next 5x HANDOVER (bm-c window r96-100)｜'
    'evidence: results/_r099bmc_s7_wrap.py + smoke 25/25 + S6 33/33 rc=0 + orders 96/96 + state-bm-c round_no=99 [via bm-c]'
)
p = repo + r'\logs\iteration-loop\round_reports-bm-c.md'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_line + '\n')

# ---- 2) state-bm-c.json (round_no 99) ----
sp = repo + r'\state-bm-c.json'
state = json.load(io.open(sp, encoding='utf-8'))
state['round_no'] = 99
state['updated'] = now_iso[:16]
state['note'] = ('r99: green maintenance round. S0 pull inbound-stall cancelled (no lock/residue; fetch-tail unpack procs left alive per pitlaw); '
                 'gh api probe origin +3 bma R345 = local behind, push leg handles (rebase-retry once else machine branch). '
                 'orders 96/96 zero-unacked (double scan); smoke 25/25; board 0 open + job_list 0; queue recheck zero-duplicate-space '
                 '(J12 town shipped / J13 L2 alive / J10 J18b wired / Optuna gated) -> honest no new build. '
                 'S6 33/33 rc=0 Sunday no-op family via _r098bmc_s6_chain.ps1 reuse; inbox 1 unread=to bm-b zero-action. '
                 'W2-A=bm-b burning dual-evidence no-touch; MF IC=claimed panel-wait. '
                 'next: Mon 09-28 09:15 T-91 s3 watch (bma) / Mon 15:30 fund_premium (bmc) / C-01 window 09-29 / 10-01 month trio / r100 next 5x')
state['last_round_ts'] = now_iso
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- 3) heartbeat fleet/machines/bm-c.json (fresh epoch int + clock_read same-read) ----
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = now_epoch          # python int -> JSON int (smoke F7)
hb['clock_read'] = now_iso
hb['verdict'] = ('legal idle: board 0 open (96 tickets all claimed/done), wm green red=false py_low_board_clear, audit CLEAN flags=[] '
                 '(pool-supply-gap disclosed); pool 1 ready=CENSUS-FUS-S2-W2A bm-b lane burning (dual-evidence no-touch); '
                 'r99=green maintenance, S0 inbound-stall probed via gh api const-channel (origin +3 bma R345)')
hb['current_task'] = ('R99 green maintenance done (S6 33/33 rc=0 reuse r98 chain script; queue recheck zero-duplicate-space honest no-build); '
                      'next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 (bmc lane) + r100 5x')
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify: epoch int type + orders_ack 96 + state round ----
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert len(chk.get('orders_ack', [])) == 96, 'orders_ack drift'
st = json.load(io.open(sp, encoding='utf-8'))
assert st['round_no'] == 99
print('WRAP OK r99 bm-c | now=', now_iso, '| epoch=', now_epoch, '| ack=96 | rescan unacked=0 | report appended')
