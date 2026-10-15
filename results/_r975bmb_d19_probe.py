import subprocess, hashlib, json, datetime

G = r'C:\Fluxgroup\FluxGroup'

def show(path):
    try:
        r = subprocess.run(['git', '-C', G, 'show', 'origin/main:' + path],
                           capture_output=True, timeout=60)
        return r.returncode, r.stdout
    except Exception as e:
        return -99, str(e).encode()

out = {'ts': datetime.datetime.now().isoformat(timespec='seconds')}
try:
    f = subprocess.run(['git', '-C', G, 'fetch', 'origin'],
                       capture_output=True, timeout=120)
    out['fetch_rc'] = f.returncode
    out['fetch_err_tail'] = f.stderr.decode('utf-8', 'replace')[-200:]
except subprocess.TimeoutExpired:
    out['fetch_rc'] = 'TIMEOUT120'
    out['fetch_err_tail'] = 'group fetch soft-cap fired (r953 law); hashes skipped, stale view stands'

if out['fetch_rc'] == 0:
    rc, dec = show('docs/decisions.md')
    out['dec_show_rc'] = rc
    if rc == 0:
        out['dec_sha256'] = hashlib.sha256(dec).hexdigest()
        out['dec_bytes'] = len(dec)
    rc, ordr = show('docs/orders.md')
    out['ord_show_rc'] = rc
    if rc == 0:
        out['ord_sha1'] = hashlib.sha1(ordr).hexdigest()
        out['ord_bytes'] = len(ordr)

with open(r'results\_r975bmb_d19_probe.json', 'w') as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
