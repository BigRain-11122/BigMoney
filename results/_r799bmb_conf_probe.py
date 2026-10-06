# r799 bm-b: content-level diff for the 3 no-ts-key faces
import subprocess, json, difflib

def git(args):
    r = subprocess.run(['git'] + args, capture_output=True)
    return r.stdout

def pretty(b):
    j = json.loads(b.decode('utf-8'))
    return json.dumps(j, indent=1, sort_keys=True, ensure_ascii=False).splitlines()

FACES = [
    'results/daily_scorecard.json',
    'results/paper_export/export-2026-09-30.json',
    'results/paper_export/latest.json',
]

for p in FACES:
    a = pretty(git(['cat-file', '-p', f':2:{p}']))
    b = pretty(git(['cat-file', '-p', f':3:{p}']))
    d = [l for l in difflib.unified_diff(a, b, 'base(bm-c-r658)', 'mine(r799)', lineterm='', n=1)]
    print('==', p, '| diff lines:', len(d))
    for l in d[:24]:
        print('  ', l)
    print()
