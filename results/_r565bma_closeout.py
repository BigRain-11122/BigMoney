# -*- coding: utf-8 -*-
"""r565 bm-a closeout: state + heartbeat + round report line (atomic single writer)."""
import io, json, time, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

# ---- state-bm-a.json ----
sp = r'state-bm-a.json'
s = json.loads(io.open(sp, encoding='utf-8').read())
s['round_no'] = 565
s['did'] = ('r565: W61 same-band window collision YIELDED to bm-b r564 (commit-order law; '
            'MSG-0640 FIX-A origin-freshness leg caught it PRE-EDIT = zero burns zero pushes, '
            'pure draft discard -- first collision-prevention-level live-fire of the r561 tooling) '
            '+ W62 FREEZE same-window re-engage (seat declared published=reserved MSG-0818-bma, '
            'r518-1 law; five-face + ADMIT gate + banned ADMIT + selftest x3; tick self-ignited 8/12 '
            'at closeout) + S6 28 legs green holiday no-ops (REPORT/LIVE-2026-10-02 regen)')
s['verify'] = ('smoke 47/47; W62 band gate ADMIT (leg0 61-keys + N3-R1 + probe-cluster + origin '
               'vacancy); banned gate ADMIT; selftest n1 full-face PASS + pf 8/8 + engine 8 legs; '
               'dualrun streak 31/3 zero-drift; attrition CLEAN; D-19 4FD50184 MATCH; orders 143/143')
s['next'] = ('W62 12/12 burn harvest (tick auto, ~4 min) -> W62 finalize one-pass AFTER bm-b W61 '
             'finalize lands (chain-gated FAIL-CLOSED r307); W63 freeze window open seat (B-side '
             'forced-skip warning: SEED_REGISTRY p4_ext_tilt_q=49_000 + p4_ext_tilt_d20=49_100 '
             'refuse the 48_801..49_000 arithmetic window, machine-proven by W62 gate projection leg)')
s['current_task'] = 'W62 engine burn in flight (8/12 at closeout, tick-fed)'
s['last_round_at'] = now
s['updated'] = now
s['last_round'] = 'r565'
s['last_round_ts'] = now
io.open(sp, 'w', encoding='utf-8', newline='\n').write(json.dumps(s, ensure_ascii=False, indent=2) + '\n')

# ---- heartbeat fleet/machines/bm-a.json ----
hp = r'fleet/machines/bm-a.json'
h = json.loads(io.open(hp, encoding='utf-8').read())
try:
    import psutil
    cpu = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    ram_free = round(vm.available / 1024**3, 1)
except Exception:
    cpu, ram_free = h.get('cpu_pct', 0.0), h.get('free_ram_gb', 0.0)
h['last_seen'] = now
h['current_task'] = 'r565: W61 yield (zero-cost FIX-A catch) + W62 FREEZE (51st engine wave, bm-a 14th owned per machine-derive) + tick burn 8/12 in flight; S6 chain rc0'
h['cpu_pct'] = cpu
h['cpu_util_pct'] = cpu
h['free_ram_gb'] = ram_free
h['ram_free_gb'] = ram_free
h['verdict'] = ('r565: W61 same-band yield (pure, FIX-A pre-edit catch) + W62 freeze+burn in '
                'flight + S6 green; engine saturated (own-series W62 queue)')
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
h['round_no'] = 565
io.open(hp, 'w', encoding='utf-8', newline='\n').write(json.dumps(h, ensure_ascii=False, indent=2) + '\n')

# ---- json.loads self-verification (R170/R178: epoch must be int) ----
h2 = json.loads(io.open(hp, encoding='utf-8').read())
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in h2['clock_read'], 'clock_read must be ISO T-separated'
print('heartbeat self-verify OK: epoch int', h2['heartbeat_epoch_utc'], 'clock', h2['clock_read'])

# ---- round report line ----
rp = r'round_reports-bm-a.md'
line = (
    '\n' + now + ' | r565 | dept:Research/Engineering | WM=green (py_low_board_clear, red=false, '
    'holiday window legal idle face -- engine saturating own-series W62) | Current activity: W62 engine burn in flight '
    '(tick self-ignited 8/12@closeout, queue 4, ~60s/shard) | Recent deliverable: **W62 FREEZE 381d85208** '
    '(fifty-first engine wave, bm-a 14th owned per machine-derive engine_owner==bm-a rows 13+candidate; '
    'A 167_004..169_003 / B 48_601..48_800 both-sides arithmetic continuation zero skip == W61 row W62+ projection '
    'verbatim; ADMIT receipt _r565bma_w62_band_gate.py; banned gate ADMIT; selftest x3 PASS) + '
    'MSG-20261002-0818-bma (W61 yield receipt + W62 seat declaration published=reserved) | Next milestone: W62 12/12 '
    'harvest (tick auto) -> finalize one-pass after bm-b W61 finalize lands (chain FAIL-CLOSED r307, window <=2h); '
    'W63 B-side forced-skip warning machine-proven (49_000/49_100 refusal) | did: (1) S0-1 anchor bm-a + fetch '
    'sync 0/0; (2) S0.5 orders 143/143 both scans zero un-acked + D-19 raw-bytes SHA 4FD50184 MATCH zero action; '
    '(3) S1 smoke 47/47; (4) **W61 same-window collision**: never-dry drafting window met bm-b r564 freeze '
    'b688cc1df (08:11:27 origin) -- bands bitwise identical (r530 deterministic cross-validation family 7th case) '
    '-- MSG-0640 FIX-A origin-freshness abort caught BEFORE any local edit (first collision-prevention live-fire: '
    'vs r563 W60 yield which burned 12 shards first) -> zero-cost pure yield (9 drafts discarded unpushed/unburned, '
    'tree to origin via ride e10e9b5a0, deletion-set empty); (5) **same-window re-engage**: seat declaration MSG-0818 '
    '(published=reserved r518-1, W48/W49/W55 precedent) -> W62 prereg drafted (anchor=W60 landed K=129,920 head '
    '496,548 + W61 ONE in-flight seat FAIL-CLOSED; pool projection 134,320; S5 anchors from W60 actuals machine-read '
    'mu -0.092367/sigma 0.248885/p95 0.3099/K-lift +0.0004) -> freeze edits FIX-A/B/C (+910/-0 pure insertion) -> band '
    'gate ADMIT (leg0 61 keys + leg0b prose + leg1 both-CLEAN + leg2 first-clean==arith + leg3 + N3-R1 + probe-cluster '
    '+ origin vacancy) -> banned ADMIT -> selftest n1 full-face PASS (W62 materializer leg green) + pf 8/8 + engine '
    '8 legs -> freeze push 381d85208 (9 files +910/-0) -> tick self-ignition verified by product growth (3/12->8/12 '
    'shards, active pid in flight; r325/r535 laws); W63+ projection leg discovered B-side refusal (p4_ext_tilt_q=49_000, '
    'p4_ext_tilt_d20=49_100) recorded in canon row; (6) S6 28 legs rc0 (dualrun streak 31/3 zero-drift; audit flags '
    'transient: cap_violation=at-cap sampling during W62 ignition+selftests per engine headroom gates, '
    'pool_starvation/supply_floor=engine-fed state, engine queue holds own-series supply; watermark '
    'py_low_board_clear green; data gates holiday no-ops honest; two initial rc=2 = missing-subcommand invocation, '
    'single-leg rerun green r559 law; scorecard/REPORT-2026-10-02/LIVE-2026-10-02/build_status host=bm-a regen; '
    'token 0 today); (7) S7: loop/watchdog/satengine tasks alive (schtasks via wrapper rc0), claw MATCH, attrition '
    'CLEAN, inbox 4 receipts read+processed, state/heartbeat epoch-int self-verified | verify: smoke 47/47 + ADMIT '
    'x2 + selftest x3 + ignition product-growth evidence + push ls-tree self-check | Score: 2 (W62 freeze = runnable/visible '
    'deliverable five-face + gate receipts + ADMIT x2; yield bookkeeping 0.5 counted within) | local commits not yet pushed to origin: to be self-verified after final push | next: W62 '
    'harvest->finalize (chain-gated); W63 open seat (B-side skip warning); seat-declaration mechanism first bm-a '
    'live-fire -- observe bm-b W62-draft absence as validation | [via bm-a r565]')
with io.open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report line appended')
