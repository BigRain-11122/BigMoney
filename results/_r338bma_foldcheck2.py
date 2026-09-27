import subprocess

def run(*a):
    return subprocess.run(list(a), capture_output=True).stdout.decode('utf-8', errors='replace')

main = 'origin/main'
branches = ['machine/bm-c-r87', 'machine/bm-c-r88', 'machine/bm-c-r89',
            'machine/bm-a-r336', 'machine/bm-b-r278', 'machine/bm-b-r287',
            'machine/bm-b-r288', 'machine/bm-b-r290', 'machine/bm-b-r311',
            'machine/bm-b-r328', 'machine/bm-c-r72', 'machine/bm-c-r84']
for br in branches:
    ref = 'origin/' + br
    mb = run('git', 'merge-base', main, ref).strip()
    if not mb:
        print(br, ': NO MERGE BASE (?)')
        continue
    # files the branch itself changed vs its merge-base with main
    files = [l for l in run('git', 'diff', '--name-only', mb, ref).splitlines() if l.strip()]
    b_only = []
    for f in files:
        b = run('git', 'show', ref + ':' + f)
        m = run('git', 'show', main + ':' + f)
        if b != m:
            # check if branch content lines are subset of main content lines (journal files)
            bl = set(l.strip() for l in b.splitlines() if l.strip())
            ml = set(l.strip() for l in m.splitlines() if l.strip())
            missing = bl - ml
            b_only.append((f, len(missing)))
    uniq = [(f, n) for f, n in b_only if n > 0]
    print('%s : changed=%d, diff-from-main=%d, content-missing-in-main=%d %s' % (
        br, len(files), len(b_only), len(uniq), uniq[:5] if uniq else ''))
