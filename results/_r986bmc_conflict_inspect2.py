import json, subprocess

def show(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8', errors='replace'))

for path in ['results/compute_audit.json', 'results/token_usage.json']:
    theirs = show('5036a2f07', path)   # origin tip (bm-a absorbed)
    mine = show('dbb9af2ab', path)      # my closeout commit
    print('===', path)
    print('theirs top keys:', list(theirs)[:10] if isinstance(theirs, dict) else f'list len {len(theirs)}')
    print('mine top keys:', list(mine)[:10] if isinstance(mine, dict) else f'list len {len(mine)}')
    # peek at machine mirror faces
    for key in ('machines', 'per_machine', 'bm-a', 'bm-b', 'bm-c'):
        if isinstance(theirs, dict) and key in theirs:
            v = theirs[key]
            print('theirs[', key, '] type:', type(v).__name__, (list(v)[:4] if isinstance(v, dict) else len(v)))
        if isinstance(mine, dict) and key in mine:
            v = mine[key]
            print('mine[', key, '] type:', type(v).__name__, (list(v)[:4] if isinstance(v, dict) else len(v)))
