import subprocess, hashlib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GRP = r'K:\Fluxgroup\FluxGroup'
subprocess.run(['git', '-C', GRP, 'fetch', 'origin'], capture_output=True)
blob = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/orders.md'], capture_output=True).stdout
sha1 = hashlib.sha1(blob).hexdigest()
text = blob.decode('utf-8', errors='replace')
lines = text.splitlines()
print('CONTENT_SHA1', sha1)
print('TOTAL_LINES', len(lines))
print('--- TAIL 25 ---')
for ln in lines[-25:]:
    print(ln[:220])
