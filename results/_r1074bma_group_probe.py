# r1074bm-a: group-repo zero-touch read -- locate three-in-one report mandate + BigMoney section state
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
def g(*args):
    r = subprocess.run(['git','-C',GRP]+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')+(r.stderr or '')
rc,_ = g('fetch','origin')
print('fetch rc', rc)
rc, out = g('show','origin/main:cph4/fleet/GROUP-AUTOMATION-PLAN-v1.md')
print('--- GROUP-AUTOMATION-PLAN-v1.md rc', rc, 'len', len(out))
if rc == 0:
    # print head + any BigMoney section
    print(out[:1500])
    i = out.find('BigMoney')
    if i >= 0: print('...BIGMONEY_SECTION...\n', out[i:i+1800])
# orders tail rows mentioning 三合一 (three-in-one)
rc, out = g('show','origin/main:docs/orders.md')
txt = out if rc==0 else ''
lines = txt.splitlines()
print('--- orders.md len', len(txt))
for l in lines[-60:]:
    if ('三合一' in l) or ('自动化' in l and ('条线' in l or '方案' in l)):
        print('ORD|', l[:240])
# council dir scan for three-in-one case files
rc, out = g('ls-tree','--name-only','origin/main','cph4/council/')
print('--- council files:'); print(out[:1200] if rc==0 else out)
