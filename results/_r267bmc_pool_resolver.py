import json
import subprocess

blob = subprocess.run(['git', 'show', '3fe1b755c:results/runnable_pool.json'], capture_output=True, check=True).stdout.decode('utf-8')
old = '"note": "ladder default shard (single-face batch, r301 family); burn complete 11:31:17 (autofill claim 11:31:01 pid 26812 same-window claim-launch r199 law)",'
new = ('"note": "ladder default shard (single-face batch, r301 family); burn complete 11:31:17 '
       '(autofill claim 11:31:01 pid 26812 same-window claim-launch r199 law); '
       'claim-collision honest note rebase r267: bm-a autofill tick stale-claim 12:00:09 in the done-flip '
       'unpushed window = r449 stale-tree family, r450 landed-state guard refuses duplicate burn, self-resolves zero-zombie",')
assert blob.count(old) == 1, 'anchor not unique: %d' % blob.count(old)
fixed = blob.replace(old, new)
with open(r'results\runnable_pool.json', 'w', encoding='utf-8', newline='') as fh:
    fh.write(fixed)
json.load(open(r'results\runnable_pool.json', encoding='utf-8'))
print('pool resolved from 3fe1b755c blob, JSON-OK')
