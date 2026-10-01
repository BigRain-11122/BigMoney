import subprocess, json, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run(*args):
    return subprocess.run(list(args), capture_output=True)

FILES = [
    'results/perpetual_faces/n1_w20_results.json',
    'research/PERPETUAL_N1_W20_PREREG.md',
    'results/_r331bmc_chain_check.py',
    'results/_r331bmc_dec_check.py',
    'results/_r331bmc_w20_read.py',
]
SRC = 'e772def0d'   # bm-c r331 W20 finalize one-pass closed loop

# pre-state: what does origin/main currently hold?
for f in FILES:
    r = run('git', 'cat-file', '-e', f'origin/main:{f}')
    print(('PRESENT  ' if r.returncode == 0 else 'MISSING  ') + f)

# check the MSG-195x inbox-move legitimacy (deleted from inbox by bm-a)
r = run('git', 'cat-file', '-e',
        'origin/main:fleet/inbox/processed/MSG-20261001-195x-bmc-bmb-bma-ALL-w20-finalize-and-surgical-commitment.md')
print('MSG-195x in inbox/processed on origin:',
      'PRESENT (legit move, no restore)' if r.returncode == 0 else 'ABSENT')

# byte-exact restore from SRC into working tree + index
for f in FILES:
    blob = run('git', 'show', f'{SRC}:{f}').stdout
    assert blob, f'empty blob for {f}'
    with open(f, 'wb') as fh:
        fh.write(blob)
    run('git', 'add', '--', f)
    r = run('git', 'cat-file', '-e', f'HEAD:{f}')
    print(('restored-over ' if r.returncode == 0 else 'restored-new   ') + f
          + f' ({len(blob)} bytes from {SRC})')

# post-state verification
d = json.loads(open('results/perpetual_faces/n1_w20_results.json', 'rb').read())
assert d['audit']['machine'] == 'bm-c', 'ownership fail'
assert d['science_gates']['ledger']['total'] == 408548
assert d['null_pool_cumulative']['merged']['n_values'] == 41920
print('VERIFY: audit.machine=bm-c, ledger 406,348->408,548, K=41,920, json.loads OK')

pr = open('research/PERPETUAL_N1_W20_PREREG.md', 'rb').read().decode('utf-8')
assert 'r331 bm-c' in pr, 'prereg backfill section missing'
print('VERIFY: W20 prereg S7/S8 backfill (r331 bm-c) present')

r = run('git', 'diff', '--cached', '--stat')
print('staged:')
print(r.stdout.decode('utf-8', errors='replace'))
