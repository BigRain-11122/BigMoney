# post-landing integrity check: working-tree file vs branch blob (EOL-transport-aware)
import hashlib, subprocess

BRANCH = 'origin/transfer/t80-deep-bcd-basis'
PREFIX = 'results/t54/'
FILES = ['cells_deep_base_dB.jsonl', 'cells_deep_base_dC.jsonl', 'cells_deep_base_dD.jsonl',
         'cells_deep_x2_dB.jsonl', 'cells_deep_x2_dC.jsonl', 'cells_deep_x2_dD.jsonl']

def sha(b):
    return hashlib.sha256(b).hexdigest()

ok = True
for name in FILES:
    r = subprocess.run(['git', 'show', f'{BRANCH}:{PREFIX}{name}'], capture_output=True)
    blob_lfn = r.stdout.replace(b'\r\n', b'\n')
    with open(PREFIX + name, 'rb') as fh:
        wt_lfn = fh.read().replace(b'\r\n', b'\n')
    same = sha(blob_lfn) == sha(wt_lfn)
    ok &= same
    print(name, 'LANDED_LF_NORMALIZED_IDENTICAL' if same else 'MISMATCH')
print('ALL_LANDED_OK' if ok else 'LANDING_DEFECT')
