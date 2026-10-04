# r699 bm-b: fetch group docs/orders.md from origin (r677 ssh-first sparse-clone recipe)
import subprocess, tempfile, os, shutil, sys
CAND = [
    'git@github.com:BigRain-11122/FluxGroup.git',
    'https://github.com/BigRain-11122/FluxGroup.git',
]
d = tempfile.mkdtemp(prefix='fg_orders_r699_')
ok = False
for url in CAND:
    r = subprocess.run(['git','clone','--depth','1','--filter=blob:none','--sparse',url,d], capture_output=True)
    if r.returncode == 0:
        ok = True
        break
    shutil.rmtree(d, ignore_errors=True)
    d = tempfile.mkdtemp(prefix='fg_orders_r699_')
if not ok:
    print('CLONE_FAIL'); sys.exit(2)
r = subprocess.run(['git','-C',d,'sparse-checkout','set','--skip-checks','docs/decisions.md','docs/orders.md'], capture_output=True)
r = subprocess.run(['git','-C',d,'show','origin/main:docs/orders.md'], capture_output=True)
open(r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r699bmb_group_orders.md','wb').write(r.stdout)
print('saved bytes=', len(r.stdout), 'sha1=', __import__('hashlib').sha1(r.stdout).hexdigest())
shutil.rmtree(d, ignore_errors=True)
