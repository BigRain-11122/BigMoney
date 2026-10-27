import io
import subprocess
import sys

PAIRS = [("<<<<<<< ", 0), ("||||||| ", 1), ("=======", 2), (">>>>>>> ", 3)]


def resolve_union(path):
    s = io.open(path, encoding='utf-8', newline='').read()
    lines = s.split('\n')
    out, i = [], 0
    hunks = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('<<<<<<< '):
            hunks += 1
            base, theirs = [], []
            mode = 'ours'
            i += 1
            while i < len(lines) and not lines[i].startswith('>>>>>>> '):
                l = lines[i]
                if l.startswith('||||||| '):
                    mode = 'base'
                elif l == '=======':
                    mode = 'theirs'
                elif mode == 'ours':
                    out.append(l)
                elif mode == 'theirs':
                    theirs.append(l)
                i += 1
            out.extend(theirs)
            i += 1
            continue
        out.append(ln)
        i += 1
    io.open(path, 'w', encoding='utf-8', newline='').write('\n'.join(out))
    left = sum(1 for l in out if l.startswith(('<<<<<<<', '>>>>>>>', '|||||||')))
    print("%s: hunks=%d markers_left=%d lines=%d" % (path, hunks, left, len(out)))
    return hunks


for p in sys.argv[1:]:
    resolve_union(p)