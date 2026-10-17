import subprocess, hashlib, sys

G = 'K:/Fluxgroup/FluxGroup'
target = 'dbf28fbaa8a9fac1f5cb9b221e28a9c040a6d442'

# recent commits touching docs/orders.md on origin/main
out = subprocess.run(['git','-C',G,'log','origin/main','-10','--format=%h','--','docs/orders.md'],capture_output=True,text=True).stdout
shas = [s.strip() for s in out.splitlines() if s.strip()]
print('candidate commits:', shas)

found = None
for sha in shas:
    blob = subprocess.run(['git','-C',G,'show',sha+':docs/orders.md'],capture_output=True).stdout
    h = hashlib.sha1(blob).hexdigest()
    print(sha, h, 'MATCH' if h==target else '')
    if h == target and found is None:
        found = sha

# dump current raw
raw = subprocess.run(['git','-C',G,'show','origin/main:docs/orders.md'],capture_output=True).stdout
cur_sha = hashlib.sha1(raw).hexdigest()
print('current content-sha1:', cur_sha)
open('results/_r1065bmc_ord_raw2.md','wb').write(raw)

if not found:
    print('WATERMARK BLOB NOT FOUND in last-10; falling back to row-level judgment from state receipts')
    sys.exit(2)

old = subprocess.run(['git','-C',G,'show',found+':docs/orders.md'],capture_output=True).stdout.decode('utf-8',errors='replace').splitlines()
new = raw.decode('utf-8',errors='replace').splitlines()
olds = set(old)
added = [l for l in new if l not in olds]
print('OLD lines:', len(old), 'NEW lines:', len(new), 'ADDED rows:', len(added))
for l in added:
    print('ROW+', l[:500])
