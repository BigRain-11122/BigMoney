# r1028 bm-b: materialize NATS bus scripts from group origin to stable install
# root C:\Fluxgroup\Tools\nats (OUTSIDE any git repo - zero tree-touch law;
# group tree 32-behind + Tools/nats is in the incoming set, so writing the ps1
# faces into the tree would abort the fleet worker's next pull).
# Byte-identical extraction via git show origin/main (fresh-read law).
import subprocess, os, hashlib, json

G = 'C:/Fluxgroup/FluxGroup'
DEST = 'C:/Fluxgroup/Tools/nats'
FILES = [
    'Tools/nats/bootstrap-nats.ps1',
    'Tools/nats/register-nats-bus.ps1',
    'Tools/nats/nats-heartbeat.ps1',
    'Tools/nats/nats-bus-server.ps1',
    'Tools/nats/fleet-live-status.ps1',
]
os.makedirs(DEST, exist_ok=True)
receipt = []
for f in FILES:
    r = subprocess.run(['git', '-C', G, 'show', 'origin/main:' + f],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git show failed for ' + f)
    data = r.stdout
    # verify against origin blob sha
    h = subprocess.run(['git', '-C', G, 'rev-parse', 'origin/main:' + f],
                       capture_output=True).stdout.decode().strip()
    actual = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
    if actual != h:
        raise SystemExit('blob sha mismatch for ' + f)
    p = os.path.join(DEST, os.path.basename(f))
    with open(p, 'wb') as fh:
        fh.write(data)
    receipt.append({'file': f, 'sha': h, 'bytes': len(data), 'dest': p})

# task-register.ps1: on-disk known-good version (daily daemon use on this box)
tr_src = 'C:/Fluxgroup/FluxGroup/Tools/task-register.ps1'
with open(tr_src, 'rb') as fh:
    trd = fh.read()
with open('C:/Fluxgroup/Tools/task-register.ps1', 'wb') as fh:
    fh.write(trd)
receipt.append({'file': 'Tools/task-register.ps1 (disk copy)', 'sha': hashlib.sha1(trd).hexdigest(), 'bytes': len(trd), 'dest': 'C:/Fluxgroup/Tools/task-register.ps1'})

# fleet-nodes.json: fresh from origin (has bm-d row + bm-b host=BIGMONEY)
r = subprocess.run(['git', '-C', G, 'show', 'origin/main:Tools/fleet-nodes.json'],
                   capture_output=True)
if r.returncode != 0:
    raise SystemExit('fleet-nodes.json show failed')
with open('C:/Fluxgroup/Tools/fleet-nodes.json', 'wb') as fh:
    fh.write(r.stdout)
receipt.append({'file': 'Tools/fleet-nodes.json (origin)', 'bytes': len(r.stdout), 'dest': 'C:/Fluxgroup/Tools/fleet-nodes.json'})

print(json.dumps(receipt, indent=1))
