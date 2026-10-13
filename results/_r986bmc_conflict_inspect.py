import json, re, sys

def load_mine(path):
    txt = open(path, encoding='utf-8').read()
    # conflict markers: take OUR side (between <<<<<<< and =======)
    ours = re.search(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> ', txt, re.S)
    mine_raw, theirs_raw = ours.group(1), ours.group(2)
    return json.loads(mine_raw), json.loads(theirs_raw)

for path in ['results/compute_audit.json', 'results/token_usage.json']:
    mine, theirs = load_mine(path)
    print('=== ', path)
    print('mine type:', type(mine).__name__, '| keys sample:', (list(mine)[:6] if isinstance(mine, dict) else len(mine)))
    print('theirs type:', type(theirs).__name__, '| keys sample:', (list(theirs)[:6] if isinstance(theirs, dict) else len(theirs)))
