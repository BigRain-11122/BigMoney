import subprocess, hashlib, sys

G = 'K:/Fluxgroup/FluxGroup'
target = 'f321f54aca50f03e3e1c0fb7b078ae4feadfa9d8'

# recent commits touching docs/orders.md on origin/main
log = subprocess.run(['git','-C',G,'log','origin/main','--format=%h','--','-8'.replace('-8',''), '--', 'docs/orders.md'],capture_output=True)
out = subprocess.run(['git','-C',G,'log','origin/main','-8','--format=%h','--','docs/orders.md'],capture_output=True,text=True).stdout
shas = [s.strip() for s in out.splitlines() if s.strip()]
print('candidate commits:', shas)

found = None
for sha in shas:
    blob = subprocess.run(['git','-C',G,'show',sha+':docs/orders.md'],capture_output=True).stdout
    h = hashlib.sha1(blob).hexdigest()
    print(sha, h, 'MATCH' if h==target else '')
    if h == target and found is None:
        found = sha

if not found:
    print('WATERMARK BLOB NOT FOUND in last-8; falling back to row-level judgment from state receipts')
    sys.exit(2)

old = subprocess.run(['git','-C',G,'show',found+':docs/orders.md'],capture_output=True).stdout.decode('utf-8',errors='replace').splitlines()
new = open('_r1050bmc_ord_raw.md','rb').read().decode('utf-8',errors='replace').splitlines()
olds = set(old)
added = [l for l in new if l not in olds]
print('OLD lines:', len(old), 'NEW lines:', len(new), 'ADDED rows:', len(added))
for l in added:
    print('ROW+', l[:400])
