# r1011 token_usage union fix for temp index (r1008 per-machine union law). ASCII only.
import json, os, subprocess

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise SystemExit('show failed for ' + ref + ': ' + (r.stderr or '')[:200])
    return r.stdout

O = json.loads(show('e326344c93:results/token_usage.json'))
M = json.loads(show('d8bc4f4891:results/token_usage.json'))
print('ORG-MACHINE-KEYS :', sorted(O.get('machines', {}).keys()))
print('MINE-MACHINE-KEYS:', sorted(M.get('machines', {}).keys()))
ombi = O.get('machines', {}).get('-bm-b')
mbi = M.get('machines', {}).get('-bm-b')
print('ORG -bm-b  :', json.dumps(ombi))
print('MINE -bm-b :', json.dumps(mbi))
if mbi is not None:
    O.setdefault('machines', {})['-bm-b'] = mbi
    print('UNION-APPLIED: -bm-b row <- mine')
else:
    print('UNION-SKIPPED-HONEST: mine has no -bm-b row, origin face kept whole')
blob = json.dumps(O, indent=2, ensure_ascii=False) + '\n'
with open('_r1011bmb_token_union.json', 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(blob)
print('WROTE _r1011bmb_token_union.json bytes=%d' % len(blob))
