# r699 bm-b: verify resolved token_usage.json bm-b key freshness (r456/r690 dual-side review law)
import json, subprocess, io
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
def show(ref, path):
    r = subprocess.run(['git','show',f'{ref}:{path}'], capture_output=True, cwd=ROOT)
    return json.loads(r.stdout.decode('utf-8'))
wt = json.load(io.open(ROOT+r'\results\token_usage.json', encoding='utf-8'))
ours = show('HEAD', 'results/token_usage.json')
theirs = show('MERGE_HEAD', 'results/token_usage.json')
print('keys top-level:', sorted(wt.keys()))
mach = wt.get('machines') or {}
print('machines keys:', sorted(mach.keys()))
for mk in sorted(mach.keys()):
    w = mach[mk]; o = (ours.get('machines') or {}).get(mk); t = (theirs.get('machines') or {}).get(mk)
    print(mk, '| worktree ts=', w.get('ts'), '| ours(HEAD) ts=', (o or {}).get('ts'), '| theirs(MERGE_HEAD) ts=', (t or {}).get('ts'))
