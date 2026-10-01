# r498 re-fire D-19 group ledger watermark check (bm-b temp partial clone recipe, raw-bytes sha)
# case-normalized compare per r503; raw-bytes per r292/r294 (no PS pipeline transcode)
import subprocess, os, sys, hashlib, json

TMP = os.path.join(os.environ.get('TEMP', r'C:\Users\Administrator\AppData\Local\Temp'), 'fg-dec-bmb')
REPO = 'git@github.com:BigRain-11122/FluxGroup.git'

def git(args, cwd=None, check=True):
    r = subprocess.run(['git'] + args, cwd=cwd, capture_output=True)
    if check and r.returncode != 0:
        print('GITFAIL', args[:3], r.stderr.decode('utf-8', 'replace')[:400]); sys.exit(2)
    return r

if not os.path.isdir(os.path.join(TMP, '.git')):
    if os.path.isdir(TMP):
        import shutil; shutil.rmtree(TMP, ignore_errors=True)
    git(['clone', '--depth', '1', '--filter=blob:none', '--no-checkout', REPO, TMP])
else:
    fr = git(['fetch', 'origin'], cwd=TMP, check=False)
    if fr.returncode != 0:
        print('FETCH_FAIL_OPEN (transient-net family, non-blocking):', fr.stderr.decode('utf-8', 'replace')[:200])

def show(path):
    r = git(['show', 'origin/main:' + path], cwd=TMP, check=False)
    if r.returncode != 0:
        return None
    return r.stdout  # raw bytes

dec = show('docs/decisions.md')
if dec is None:
    print('DECISIONS_UNREADABLE'); sys.exit(2)
sha = hashlib.sha256(dec).hexdigest().upper()

state_path = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json'
with open(state_path, encoding='utf-8') as f:
    state = json.load(f)
prev = str(state.get('last_decisions_sha', '')).upper()

print('NEW_SHA', sha)
print('PREV_SHA', prev)
if sha == prev:
    print('VERDICT UNCHANGED -- zero action')
    sys.exit(0)

print('VERDICT CHANGED -- consuming dispatch-board rows for this-company lines:')
text = dec.decode('utf-8', 'replace')
lines = text.splitlines()
# print tail section (latest 80 lines) where dispatch board + new rows live
for ln in lines[-80:]:
    print('DEC|', ln)
# orders.md CEO physical-item section rows mentioning this company
orders = show('docs/orders.md')
if orders:
    otext = orders.decode('utf-8', 'replace')
    for ln in otext.splitlines():
        low = ln.lower()
        if ('bigmoney' in low) or ('quant' in low and ('待办' in ln or '物理' in ln)):
            print('ORD|', ln)
print('REMEMBER: update state last_decisions_sha to', sha)
