import subprocess, hashlib, json, os

REPO = os.path.join(os.environ['TEMP'], 'fg-dec-bmb')
blob = subprocess.check_output(['git', '-C', REPO, 'show', 'origin/main:docs/decisions.md'])
sha = hashlib.sha256(blob).hexdigest().upper()
d = json.load(open('state.json'))
old = str(d.get('last_decisions_sha', '')).upper()
print('new_sha:', sha[:16], 'old:', old[:16])
if sha == old:
    print('MATCH-unchanged')
else:
    print('CHANGED')
    text = blob.decode('utf-8', errors='replace')
    lines = text.splitlines()
    print('total_lines:', len(lines))
    # print last 40 lines for consumption review
    for ln in lines[-40:]:
        print(ln)
