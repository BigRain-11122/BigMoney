# r699 bm-b: default-key tri-side attribution (HEAD vs MERGE_HEAD vs worktree)
import json, subprocess, io
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
def default_entry(ref):
    r = subprocess.run(['git','show',f'{ref}:results/token_usage.json'], capture_output=True, cwd=ROOT)
    d = json.loads(r.stdout.decode('utf-8'))
    return (d.get('machines') or {}).get('default'), d.get('generated')
wt = json.load(io.open(ROOT+r'\results\token_usage.json', encoding='utf-8'))
print('worktree default:', json.dumps((wt.get('machines') or {}).get('default')), 'generated=', wt.get('generated'))
for ref in ('HEAD', 'MERGE_HEAD'):
    e, g = default_entry(ref)
    print(ref, 'default:', json.dumps(e), 'generated=', g)
