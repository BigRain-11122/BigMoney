"""r636 bm-a: release fund-value-p1-nulls claim on all pool faces (r616 all-lane law).

Reads every results/runnable_pool*.json face, finds the fund-value-p1-nulls-0of1
shard block, and if it carries the 18:16:08 bm-a claim, flips owner/owner_since
back to null and appends the release trace to the shard note.
Raw-text surgical edit per r509 (no re-serialization); json.loads + numstat
asserts per r629.
"""
import glob
import json
import os
import subprocess
import sys

REL_NOTE = (" | rel-bm-a-r636 18:5x: 5th double-burn containment -- autofill claimed 18:16 after "
            "r627 per-sig newer-wins kept the pin at stale sha efd7b44a (r626d runner edit) -> "
            "code_changed auto-clear; burn killed 18:52 (tree-sweep 52 pids r618), 50 illegal rows "
            "discarded, nulls.jsonl restored origin-verbatim; bm-b canonical burn in flight")

faces = sorted(glob.glob(os.path.join('results', 'runnable_pool*.json')))
changed = []
for fp in faces:
    txt = open(fp, encoding='utf-8').read()
    i = txt.find('"key": "fund-value-p1-nulls-0of1"')
    if i < 0:
        print(os.path.basename(fp), ': no shard entry (skip)')
        continue
    end = txt.find('}\n', i)
    block = txt[i:end]
    if '"owner": "bm-a"' not in block or '18:16:08' not in block:
        print(os.path.basename(fp), ': shard present, no bm-a 18:16:08 claim (skip)')
        continue
    new_block = block.replace('"owner": "bm-a"', '"owner": null')
    new_block = new_block.replace('"owner_since": "2026-10-03 18:16:08"', '"owner_since": null')
    anchor = 'keep-block note on crash_fuse",'
    if anchor in new_block and 'rel-bm-a-r636' not in new_block:
        new_block = new_block.replace(anchor, 'keep-block note on crash_fuse' + REL_NOTE + '",', 1)
    new_txt = txt[:i] + new_block + txt[end:]
    json.loads(new_txt)  # validity assert before write
    open(fp, 'w', encoding='utf-8', newline='').write(new_txt)
    changed.append(fp)
    print(os.path.basename(fp), ': RELEASED (owner->null, note + release trace)')

for fp in changed:
    json.load(open(fp, encoding='utf-8'))
print('---changed faces:', len(changed))
for fp in changed:
    r = subprocess.run(['git', 'diff', '--', 'numstat', fp], capture_output=True, text=True)
    r2 = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True, text=True)
    print(os.path.basename(fp), 'numstat:', r2.stdout.strip())
sys.exit(0)
