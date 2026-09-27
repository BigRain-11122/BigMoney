import os
import glob
import json
import time

print('NOW:', time.strftime('%H:%M:%S'))
# 1. inbox unread for bm-a or ALL
unread = []
for f in sorted(glob.glob('fleet/inbox/*.md') + glob.glob('fleet/inbox/*.json')):
    base = os.path.basename(f)
    try:
        txt = open(f, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    low = base.lower()
    if ('bm-a' in low or 'all' in low or '-cc-' in low) and 'bmb' not in low and 'bmc' not in low:
        unread.append((f, txt[:160]))
print('inbox candidates for bm-a/ALL/cc:', len(unread))
for f, head in unread:
    print('  ', f)
    print('    ', head.replace('\n', ' ')[:150])
# 2. processed dir count
print('processed count:', len(glob.glob('fleet/inbox/processed/*')))
