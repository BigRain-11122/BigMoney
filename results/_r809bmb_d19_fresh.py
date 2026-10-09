# r809 bm-b D-19 FULL fresh read attempt (r804/r789 sparse-clone recipe, fresh temp dir
# after corrupt-shell cleanup; bounded clone + lazy blob fetch; progress prints keep shell alive)
import hashlib, json, os, shutil, subprocess, sys

REPOS = ['git@github.com:BigRain-11122/FluxGroup.git',
         'https://github.com/BigRain-11122/FluxGroup.git']
tmp = os.path.join(os.environ['TEMP'], 'd19_r809b')
if os.path.isdir(tmp):
    shutil.rmtree(tmp, ignore_errors=True)

print('clone: starting (depth1 blob:none, ssh-first)...', flush=True)
got = None
for r0 in REPOS:
    try:
        k = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', r0, tmp],
                           capture_output=True, text=True, timeout=240)
        if k.returncode == 0:
            got = r0
            break
        print('clone failed via %s: %s' % (r0[:28], (k.stderr or '')[-160:].replace(chr(10), ' ')), flush=True)
    except subprocess.TimeoutExpired:
        print('clone TIMEOUT via %s' % r0[:28], flush=True)
if not got:
    print('FRESH-READ-DEFERRED: all clone paths failed', flush=True)
    sys.exit(2)

print('clone: ok via', got[:40], flush=True)
st = {'round': 'r809', 'mode': 'full-fresh sparse clone', 'clone_url': got}
b1 = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/decisions.md'], capture_output=True, timeout=120)
b2 = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/orders.md'], capture_output=True, timeout=120)
for tag, b in [('decisions', b1), ('orders', b2)]:
    st[tag + '_sha1'] = hashlib.sha1(b.stdout).hexdigest().upper()
    st[tag + '_sha256'] = hashlib.sha256(b.stdout).hexdigest().upper()
    st[tag + '_bytes'] = len(b.stdout)

st['decisions_sha1_fleet_match'] = st['decisions_sha1'].startswith('BD94A27B')
st['orders_sha1_fleet_match'] = st['orders_sha1'].startswith('F26E1A37')
dec_txt = b1.stdout.decode('utf-8', 'replace')
ord_txt = b2.stdout.decode('utf-8', 'replace')
st['decisions_tail40'] = dec_txt.splitlines()[-40:]
hits = [l for l in ord_txt.splitlines() if ('BigMoney' in l or 'bigmoney' in l or 'bm-b' in l)]
st['orders_bmb_rows'] = hits[-30:]
st['orders_tail25'] = ord_txt.splitlines()[-25:]
json.dump(st, open('results/_r809bmb_d19_read.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('FRESH-READ-DONE dec_sha1=%s orders_sha1=%s fleet_match dec=%s ord=%s' % (
    st['decisions_sha1'][:16], st['orders_sha1'][:16], st['decisions_sha1_fleet_match'], st['orders_sha1_fleet_match']), flush=True)
