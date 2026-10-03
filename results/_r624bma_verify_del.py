import re, subprocess
# Verify ALL deleted files between origin/main and HEAD match bm-a one-off script pattern
r = subprocess.run(['git', 'diff', '--name-status', 'origin/main', 'HEAD'],
                   capture_output=True, text=True, encoding='utf-8')
pat = re.compile(r'^results/_r\d+bma_[^/]*\.(py|ps1|txt|log|json|md)$')
bad, deleted = [], []
for line in r.stdout.splitlines():
    if not line.startswith('D\t'):
        continue
    p = line[2:].strip()
    deleted.append(p)
    if not pat.match(p):
        bad.append(p)
print('deleted total:', len(deleted))
print('bm-a-pattern match:', len(deleted) - len(bad))
print('NON-bm-a (must be zero):', bad if bad else 'NONE')
# also verify each basename exists in archive (zero-loss already proven this round, re-assert)
import os
arch = set(os.listdir(r'.codely-cli\scripts-archive'))
missing = [p for p in deleted if os.path.basename(p) not in arch]
print('archive-missing (must be zero):', len(missing), missing[:5] if missing else '')
