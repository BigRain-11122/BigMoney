# r585 bm-b push surgery: my commit 3171623e9 based on 565a6b254, origin moved
# 5 commits ahead (bm-c W105 freeze + bm-a W104 union). r374 fork artifact:
# claw correctly blocked; r523 law = surgical commit-tree onto origin base.
# r581 law: my_files INTERSECT their_mod on shared derive faces -> take origin
# side (fresher re-derive, next round re-derives anyway); my bm-b-owned faces
# ride mine. No append-only ledger in the intersection (checked below).
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
CREATE = 0x08000000

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', creationflags=CREATE)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-600:]); sys.exit(1)
    return r

run(['git', 'fetch', 'origin'])
base = '565a6b254'
mine = run(['git', 'rev-parse', 'main']).stdout.strip()
origin = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
print('base=%s mine=%s origin=%s' % (base[:10], mine[:10], origin[:10]))

r = run(['git', 'diff', '--no-renames', '--name-status', base, mine])
my_files, my_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (my_del if st.startswith('D') else my_files).append(p)
r = run(['git', 'diff', '--no-renames', '--name-status', base, origin])
their_mod, their_del = [], []
for l in r.stdout.splitlines():
    if not l.strip(): continue
    st = l.split('\t')[0]; p = l.split('\t')[-1]
    (their_del if st.startswith('D') else their_mod).append(p)
print('my_files=%d my_del=%d their_mod=%d their_del=%d'
      % (len(my_files), len(my_del), len(their_mod), len(their_del)))
print('their_del:', their_del)

# unstaged working-tree inbox deletions (MSG moves pending from commit#1)
wt_del = [l[3:] for l in run(['git', 'status', '--porcelain']).stdout.splitlines()
          if l[:2] == ' D']
print('worktree unstaged deletions:', wt_del)

# intersection analysis
inter = sorted(set(my_files) & set(their_mod))
print('INTERSECTION my_files x their_mod (%d):' % len(inter))
for f in inter: print('  ', f)
APPEND_ONLY = {'results/pool_core_samples.jsonl', 'CODELY.md'}
bad = [f for f in inter if f in APPEND_ONLY]
assert not bad, 'append-only in intersection needs union: %s' % bad
# also: my_del x their_mod, their_del x my_files
c1 = sorted(set(my_del) & set(their_mod))
c2 = sorted(set(wt_del) & set(their_mod))
c3 = sorted(set(their_del) & set(my_files))
print('my_del x their_mod:', c1, '| wt_del x their_mod:', c2, '| their_del x my_files:', c3)
