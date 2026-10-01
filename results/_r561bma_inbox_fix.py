import subprocess, os, shutil, hashlib

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

# 1. MSG-0640 (addressed to bm-a): verify identical copy exists in processed/
# on origin before moving ours (processed face on origin per bm-b r560 diff)
r = subprocess.run(['git', '-C', REPO, 'ls-tree', 'origin/main', '--',
                    'fleet/inbox/processed/MSG-20261002-0640-bm-b.md'],
                   capture_output=True, text=True)
if r.stdout.strip():
    # origin already moved it to processed (bm-b r560 S7 did the move) --
    # then our local inbox copy would be a stale leftover; verify identity
    # with the processed blob, then remove local stale.
    print('origin has processed/MSG-0640')
else:
    print('origin still has MSG-0640 in inbox/ (unprocessed on origin)')

# 2. stale untracked inbox leftovers: verify byte-identity with processed/ copies then remove
stale = ['fleet/inbox/MSG-20261002-0552-bm-b.md',
         'fleet/inbox/MSG-20261002-0615-bm-a.md',
         'fleet/inbox/MSG-20261002-063x-bm-b.md']
for p in stale:
    local = os.path.join(REPO, p)
    if not os.path.exists(local):
        print('absent:', p)
        continue
    proc = os.path.join(REPO, p.replace('inbox/', 'inbox/processed/'))
    if os.path.exists(proc):
        if sha(local) == sha(proc):
            os.remove(local)
            print('verified-identical, stale local copy removed:', p)
        else:
            print('CONTENT DIVERGENCE -- kept for manual review:', p)
    else:
        # pull the processed blob from origin for comparison
        r = subprocess.run(['git', '-C', REPO, 'show', 'origin/main:' + p.replace('inbox/', 'inbox/processed/')],
                           capture_output=True)
        if r.returncode == 0 and hashlib.sha256(r.stdout).hexdigest()[:16] == sha(local):
            os.remove(local)
            print('verified-identical vs origin processed blob, removed:', p)
        else:
            print('no processed twin on origin -- kept:', p)

# 3. state of MSG-0640 handling: our ack = the implemented cure (W57 freeze tool)
#    + reply MSG to bm-b
print('inbox scan done')
