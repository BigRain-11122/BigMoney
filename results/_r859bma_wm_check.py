import hashlib, subprocess, sys

def sha_of(repo, path):
    r = subprocess.run(['git', '-C', repo, 'show', f'origin/main:{path}'],
                       capture_output=True)
    if r.returncode != 0:
        print(f'ERR {path}:', r.stderr.decode(errors='replace')[:100]); sys.exit(1)
    return hashlib.sha256(r.stdout).hexdigest()

repo = r'C:\Users\sjs20\Desktop\FluxGroup'
dec = sha_of(repo, 'docs/decisions.md')
ordr = sha_of(repo, 'docs/orders.md')
print('dec-sha(raw):', dec)
print('ord-sha(raw):', ordr)
print('dec-changed:', dec != 'ee6594516c01856ecd1bd4131e49cafd8f95a61293c131ce5d45c574c20ff6ce')
print('ord-changed:', ordr != '2bb2ee75edfcd506501608c422f94c7ca8ca3255d3612e38803e14eaf4baf416')
