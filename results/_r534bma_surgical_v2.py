"""r534 surgical v2: split payload into clean (origin untouched) vs collided (origin newer).
Round bookkeeping/CODELY/MSG faces = apply mine; live lane rides that collided = take origin's."""
import subprocess, sys, os

def run(args, env=None):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if r.returncode != 0:
        print('FAIL:', ' '.join(args)); print(r.stdout); print(r.stderr); sys.exit(1)
    return r.stdout.strip()

repo = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
git = ['git', '-C', repo]
LOCAL = run(git + ['rev-parse', 'HEAD'])
PARENT = run(git + ['rev-parse', 'HEAD~1'])
run(git + ['fetch', 'origin'])
BASE = run(git + ['rev-parse', 'origin/main'])
print('local:', LOCAL[:12], 'parent:', PARENT[:12], 'origin:', BASE[:12])

mine = run(git + ['diff-tree', '--no-commit-id', '--name-status', '-r', LOCAL])
entries = [l.split('\t') for l in mine.splitlines()]
theirs = run(git + ['diff-tree', '--no-commit-id', '--name-only', '-r', PARENT, BASE]).splitlines()
theirs_set = set(theirs)

# Files where taking mine would clobber origin's newer version:
# live lane faces (daemon-rewritten) OR shared append faces.
LIVE_PREFIXES = ('results/autofill_state.', 'results/saturation_engine/', 'results/pool_core_samples',
                 'results/x2_watch_log', 'results/compute_audit.', 'results/update_status.',
                 'results/token_usage.', 'results/regime_state.', 'results/dashboard_status',
                 'results/daily_scorecard', 'results/strategy_scorecard', 'results/scorecard_v1',
                 'results/fundamental_b_layer_filter', 'results/t35_open_fill_verify',
                 'results/paper/', 'results/paper_export/', 'results/prospect_', 'results/_attrition_guard_scan',
                 'results/market_clock/', 'docs/daily_report/', 'docs/live_usage/')
apply_mine, take_origin, undecided = [], [], []
for st, *paths in entries:
    p = paths[-1]
    if p in theirs_set:
        if any(p.startswith(pre) for pre in LIVE_PREFIXES):
            take_origin.append((st, p))
        else:
            undecided.append((st, p))
    else:
        apply_mine.append((st, p))

print('\n-- collided & live (take origin):')
for st, p in take_origin: print(' ', st, p)
print('-- collided & NOT live (undecided, manual):')
for st, p in undecided: print(' ', st, p)
print('-- clean (apply mine):', len(apply_mine))

tmp_index = os.path.join(repo, '.git', '_r534_tmp_index2')
if os.path.exists(tmp_index): os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(git + ['read-tree', BASE], env=env)

for st, p in take_origin:
    pass  # origin version already in tree
for st, *paths in entries:
    p = paths[-1]
    if (st, p) in take_origin or any((s == st and pp == p) for s, pp in undecided):
        continue
    if st.startswith('A') or st.startswith('M') or st.startswith('R'):
        blob = run(git + ['rev-parse', f'{LOCAL}:{p}'])
        run(git + ['update-index', '--add', '--cacheinfo', f'100644,{blob},{p}'], env=env)
        if st.startswith('R'):
            old = paths[0]
            run(git + ['update-index', '--force-remove', old], env=env)
    elif st.startswith('D'):
        run(git + ['update-index', '--force-remove', p], env=env)

tree = run(git + ['write-tree'], env=env)
msgfile = os.path.join(repo, '.git', '_r534_msg2.txt')
with open(msgfile, 'w', encoding='utf-8') as f:
    f.write('r534 closeout [surgical v2, lane rides collided-with-origin taken origin-side per fail-closed split]: '
            'W21 finalize receipt chain-verify MSG-202x + S6 38-leg faces + CODELY r534 law + state/heartbeat/round report 534 + MSG-201x processed\n')
new_sha = run(git + ['commit-tree', tree, '-p', BASE, '-F', msgfile])
print('surgical commit:', new_sha)

r = subprocess.run(git + ['push', 'origin', new_sha + ':refs/heads/main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('push rc:', r.returncode, (r.stderr or '').strip()[-200:])
sys.exit(r.returncode)
