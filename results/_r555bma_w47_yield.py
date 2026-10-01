"""r555 helper: W47 yield surgery.
1) Archive provenance diff (my freeze suite vs origin/main = bm-b r534 version)
2) Restore the 4 freeze files from origin/main (adopt bm-b's canonical)
3) Unstage + delete my duplicate W47 shard products (bm-b owns the wave;
   engine ledger rows kept in the lane rides)
"""
import subprocess, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 1) provenance diff: staged (mine) vs origin/main (bm-b's) ---
FREEZE_FILES = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
    'research/PERPETUAL_N1_W47_PREREG.md',
]
diff = subprocess.run(
    ['git', 'diff', '--cached', 'origin/main', '--'] + FREEZE_FILES,
    capture_output=True)
open(os.path.join(ROOT, 'results', '_r555bma_w47_yield_discard.diff'), 'wb'
     ).write(diff.stdout)
print('provenance diff saved:', len(diff.stdout), 'bytes '
      '(my freeze suite vs origin bm-b canonical)')

# --- 2) restore the 4 freeze files from origin/main (staged + worktree) ---
for f in FREEZE_FILES:
    subprocess.run(['git', 'restore', '--staged', '--worktree',
                    '--source=origin/main', f], check=True)
    print('restored from origin:', f)

# --- 3) unstage + delete my duplicate shard products ---
shards = sorted(glob.glob(os.path.join(ROOT, 'results', 'p2cal_ext', 'n1_w47',
                                       'shard-*.json')))
for s in shards:
    subprocess.run(['git', 'reset', 'HEAD', '--',
                    os.path.relpath(s, ROOT)], capture_output=True)
    os.remove(s)
    print('discarded duplicate shard product:', os.path.basename(s))
# remove the dir if empty
d = os.path.join(ROOT, 'results', 'p2cal_ext', 'n1_w47')
if os.path.isdir(d) and not os.listdir(d):
    os.rmdir(d)
    print('removed empty dir n1_w47/')
print('yield surgery done')
