# -*- coding: utf-8 -*-
# r385 bm-c surgical closeout push (r523 law): temp index on origin/main base + targeted add + assertions + CAS-style push
# Local main untouched (holds 3 GM-session commits, not ours to push).
import subprocess, os, sys
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
NW = 0x08000000

def g(args, env=None):
    return subprocess.run(['git'] + args, capture_output=True, creationflags=NW, env=env)

def gout(args, env=None):
    return subprocess.check_output(['git'] + args, creationflags=NW, env=env)

PAYLOAD = [
    'CODELY.md', 'round_reports-bm-c.md', 'state-bm-c.json',
    'fleet/machines/bm-c.json', 'research/HANDOVER.md',
    'research/PERPETUAL_N1_W115_PREREG.md', 'results/_r385bmc_w115_parked.diff',
    'results/_r384bmc_w115_band_gate.py', 'results/_r384bmc_w115_freeze_edits.py',
    'results/_r384bmc_w115_prereg_gen.py',
    'fleet/inbox/MSG-2026-10-02-2200-bmc-ALL-w115-park.md',
    'fleet/tasks/T-2026-10-02-147-P1.json',
    'results/compute_audit.bm-c.json', 'results/compute_audit.json',
    'results/pool_dualrun.bm-c.jsonl', 'results/update_status.bm-c.json',
    'results/update_status.json', 'results/regime_state.bm-c.json', 'results/regime_state.json',
    'results/token_usage.bm-c.json', 'results/token_usage.json',
    'results/fund_premium_status.json', 'results/lhb_update_status.bm-c.json',
    'results/lhb_update_status.json', 'results/futures_update_status.bm-c.json',
    'results/futures_update_status.json', 'results/autofill_state.bm-c.json',
    'results/dispatcher_state.bm-c.json', 'results/saturation_engine_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json', 'results/strategy_scorecard.json',
    'results/scorecard_v1.json', 'results/dashboard_status.json', 'results/dashboard_status.js',
    'results/fundamental_b_layer_filter.json', 'results/_attrition_guard_scan.json',
    'docs/daily_report/REPORT-2026-10-02.md', 'docs/daily_report/REPORT-2026-10-02.json',
    'docs/live_usage/LIVE-2026-10-02.md', 'docs/live_usage/LIVE-2026-10-02.json',
    'docs/live_usage/LIVE-latest.md', 'docs/live_usage/LIVE-latest.json',
]

MSG = """round 385 (bm-c): W115 PARK per O-2115 supply-priority + T-147 deep-axis family line opened/claimed + r382 stranded books healed + S6 28 legs rc0. W115 (dead r383/r384 estate adopted then order-re-checked): five-face freeze edits unwound via restore --source=origin/main (n1 selftest PASS legs-to-W114, pf 9/9), engine no-ignition verified (21:58 tick: W115 row gone, queue 0, idle), seat retained bm-c non-abandon, park estate published: PARKED-banner prereg (anchors = W114 landed values) + _r385bmc_w115_parked.diff 22,244B + r384 toolset x3 + MSG-2026-10-02-2200-bmc-ALL-w115-park. O-2100/O-2115/O-2124/O-2135 acked (orders 147/147 double-scan zero-pending): O-2100 capture-law wiring verified live (iteration_prompt 4 mentions; E07 bm-a + E08 bm-b first library evidence); O-2115 lines: line-2 deep-axis -> T-147 opened+claimed same round (P3 +55~60% 67-trade face -> family prereg, main-exam qualification at birth, exit-axis double gate, evidence inventory in ticket, due 10-09); line-1 T-145 = bm-a in-flight (yielded); O-2124 = City3D @bm-a, no bm-c duty; O-2135 = GM T-146 in-flight (no OS claim, anti-double-head). r382 pit healed + law'd: the closeout commit was the engine append commit (shard paths only) -> state/heartbeat/round-report/CODELY stranded in worktree 1.5h; all books re-landed here; pit -> CODELY. Watermark RED honest disclosure: runnable-work-idle-low-cpu = O-2115 transition window (pool ready=0 [323 done + 1 waiting-parked W14-GENERATE], N1 parked, T-146 open-GM-executing counted as work-cand); remedy = T-147/T-145 new-family preregs restore pool supply by 10-09. Verification: smoke 47/47; S6 28/28 rc0 (dualrun ZERO-DRIFT 51/3; scorecard/dscore/build_status L3 stale-takeover legal bm-a hb>20min; fund_premium lane idempotent; Golden Week paper block honest skip r588); D-19 MATCH 937A373D; attrition CLEAN 4 ledgers; self-heal 4/4 (loop pin=5 no-op, watchdog re-registered, both claws installed); HANDOVER 5x window r336-r385 filed. Local main holds 3 GM-session commits (CAS twins already on origin) -- untouched, not mine to push. [via bm-c r385]"""

msg_path = os.path.abspath('results/_r385bmc_commit_msg.txt')
open(msg_path, 'wb').write(MSG.encode('utf-8'))

# 1) freshness: execution-time rev-parse (r593 law)
g(['fetch', 'origin'])
base = gout(['rev-parse', 'origin/main']).decode().strip()
print('base =', base)

# 2) temp index seeded from origin/main
tmp_index = os.path.abspath('results/_r385bmc_tmp_index')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env_idx = dict(os.environ, GIT_INDEX_FILE=tmp_index)
r = g(['read-tree', base], env=env_idx)
assert r.returncode == 0, r.stderr

# 3) targeted add of payload (clean filters apply -> LF blobs)
for p in PAYLOAD:
    r = g(['add', '--', p], env=env_idx)
    if r.returncode != 0:
        print('ADD FAIL', p, r.stderr.decode('utf-8', 'replace'))
        sys.exit(2)
print('payload added: %d paths' % len(PAYLOAD))

# 4) write-tree
tree = gout(['write-tree'], env=env_idx).decode().strip()
print('tree =', tree)

# 5) assertions
names_new = set(gout(['ls-tree', '-r', '--name-only', tree], env=env_idx).decode().splitlines())
names_old = set(gout(['ls-tree', '-r', '--name-only', base], env=env_idx).decode().splitlines())
deletions = names_old - names_new
assert not deletions, ('DELETION SET NON-EMPTY', sorted(deletions)[:10])
delta = set(gout(['diff-tree', '--no-commit-id', '--name-only', '-r', base, tree], env=env_idx).decode().splitlines())
unexpected = delta - set(PAYLOAD)
assert not unexpected, ('UNEXPECTED FACES IN DELTA', sorted(unexpected)[:10])
print('ASSERTIONS PASS: deletions=0, delta=%d (all in payload)' % len(delta))

# 6) commit-tree
commit = gout(['commit-tree', tree, '-p', base, '-F', msg_path], env=env_idx).decode().strip()
print('commit =', commit)

# 7) push (clean env, no temp index var -> pre-push claw runs with normal repo state)
env_clean = {k: v for k, v in os.environ.items() if k != 'GIT_INDEX_FILE'}
r = g(['push', 'origin', commit + ':refs/heads/main'], env=env_clean)
print('push rc=%d' % r.returncode)
if r.stdout.strip():
    print(r.stdout.decode('utf-8', 'replace').strip())
if r.stderr.strip():
    print('[stderr]', r.stderr.decode('utf-8', 'replace').strip())
if r.returncode != 0:
    sys.exit(3)

# 8) delivery verification: fetch + rev-parse + ls-tree spot checks
g(['fetch', 'origin'], env=env_clean)
origin_now = gout(['rev-parse', 'origin/main'], env=env_clean).decode().strip()
print('origin/main now =', origin_now)
print('delivery =', 'VERIFIED' if origin_now == commit else 'MISMATCH (advanced by peer — acceptable, check reachability)')
if origin_now != commit:
    rc = g(['merge-base', '--is-ancestor', commit, 'origin/main'], env=env_clean)
    print('commit reachable in origin/main:', rc.returncode == 0)
for probe in ['state-bm-c.json', 'fleet/inbox/MSG-2026-10-02-2200-bmc-ALL-w115-park.md',
              'research/PERPETUAL_N1_W115_PREREG.md', 'fleet/tasks/T-2026-10-02-147-P1.json',
              'CODELY.md', 'round_reports-bm-c.md']:
    sha = gout(['rev-parse', 'origin/main:' + probe], env=env_clean).decode().strip()
    print('origin blob %s -> %s' % (probe, sha[:12]))
os.remove(tmp_index)
print('SURGICAL PUSH DONE')
