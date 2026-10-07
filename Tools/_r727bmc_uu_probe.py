import subprocess
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
r = subprocess.run(['git', 'status'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
print(r.stdout[:900])
print('rebase-merge dir exists:', os.path.exists('.git/rebase-merge'))
if os.path.exists('.git/rebase-merge'):
    print('done:', open('.git/rebase-merge/done', encoding='utf-8', errors='replace').read()[:200])
    for f in ('msgnum', 'end'):
        p = os.path.join('.git/rebase-merge', f)
        print(f, ':', open(p).read().strip() if os.path.exists(p) else None)
