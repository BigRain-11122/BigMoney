# r612 bm-b rebase conflict resolver -- per-file-family law resolution (r513/r589/MSG-0612).
# Run when `git rebase origin/main --autostash` stops on conflicts.
# Rebase semantics: --ours = new base (origin/main side) = take-origin;
#                   --theirs = replayed commit (bm-b local) = keep-mine.
import subprocess, sys, io, os

KEEP_MINE = {'results/runnable_pool.bm-b.json'}
UNION = {'CODELY.md'}
# Everything else that conflicts: shared derive faces -> take-origin (r513 newer-wins).
# Unknown files outside the known 23-intersect: refuse (manual adjudication).

def run(args):
    r = subprocess.run(['git'] + args, capture_output=True)
    return r.returncode, r.stdout.decode('utf-8', errors='replace'), r.stderr.decode('utf-8', errors='replace')

rc, out, err = run(['diff', '--name-only', '--diff-filter=U'])
conflicted = [l for l in out.splitlines() if l.strip()]
print('CONFLICTED:', len(conflicted))
if not conflicted:
    print('NO CONFLICTS -- nothing to do')
    sys.exit(0)

resolved, refused = [], []
for f in conflicted:
    if f in KEEP_MINE:
        rc2, _, e2 = run(['checkout', '--theirs', '--', f])
        run(['add', '--', f])
        resolved.append((f, 'KEEP-MINE(theirs)'))
        print('KEEP-MINE', f, rc2, e2.strip()[:80])
    elif f in UNION:
        rc3, o3, _ = run(['show', ':' + f])  # conflicted worktree copy? use raw file
        try:
            raw = io.open(f, encoding='utf-8', errors='replace').read()
        except Exception as ex:
            refused.append((f, 'union-read-fail ' + str(ex)))
            continue
        # strip conflict markers keeping both sides (append-only memory union)
        lines = raw.split('\n')
        outl, mode = [], None
        for ln in lines:
            if ln.startswith('<<<<<<<'):
                mode = 'ours'
                continue
            if ln.startswith('=======') and mode == 'ours':
                mode = 'theirs'
                continue
            if ln.startswith('>>>>>>>') and mode == 'theirs':
                mode = None
                continue
            outl.append(ln)
        io.open(f, 'w', encoding='utf-8', newline='').write('\n'.join(outl))
        run(['add', '--', f])
        resolved.append((f, 'UNION-both'))
        print('UNION', f)
    else:
        # shared derive family -> take origin side
        rc4, _, e4 = run(['checkout', '--ours', '--', f])
        run(['add', '--', f])
        resolved.append((f, 'TAKE-ORIGIN(ours)'))
        print('TAKE-ORIGIN', f, rc4, e4.strip()[:80])

print('RESOLVED', len(resolved), 'REFUSED', len(refused))
for f, why in refused:
    print('REFUSED:', f, why)
sys.exit(1 if refused else 0)
