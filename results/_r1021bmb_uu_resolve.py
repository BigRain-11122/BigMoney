"""r1021 bm-b rebase UU resolver (r1015 versioned-resolver family law).

Faces: shared regen faces (18). Resolution law:
- results/paper/marks/marks-20261019.jsonl -> append-only line-union (ts order, dedup).
- all others -> newer-wins by embedded ts-ish field (ts/checked_at/updated_at/
  generated/now); incomparable -> ours-must-be-origin check not needed: default
  = theirs (this commit's regen faces are the payload being delivered).
ours (:2:) = origin tip side; theirs (:3:) = my r1021 commit side.
Prints per-face verdict lines; exits 0. Adds each resolved face to the index.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WINDOW = 0x08000000
UNION_FACES = {'results/paper/marks/marks-20261019.jsonl'}
TS_KEYS = ('"ts"', '"checked_at"', '"updated_at"', '"generated_at"', '"now"')


def sh(args, timeout=90):
    p = subprocess.run(['git'] + args, cwd=ROOT, capture_output=True, timeout=timeout,
                       creationflags=NO_WINDOW)
    return p.returncode, (p.stdout or b'').decode('utf-8', 'replace'), \
        (p.stderr or b'').decode('utf-8', 'replace')


def ts_of(text):
    best = ''
    for key in TS_KEYS:
        for m in re.finditer(re.escape(key) + r'\s*:\s*"([^"]+)"', text):
            v = m.group(1)
            if v > best:
                best = v
    return best


def main():
    rc, out, err = sh(['status', '--porcelain'])
    uu = [l[3:].strip() for l in out.splitlines() if l.startswith('UU')]
    print('UU faces: %d' % len(uu))
    for face in uu:
        rc2, ours, _ = sh(['show', ':2:%s' % face])
        rc3, theirs, _ = sh(['show', ':3:%s' % face])
        if rc2 != 0 or rc3 != 0:
            print('SKIP (side-missing) %s' % face)
            continue
        if face in UNION_FACES:
            seen, rows = set(), []
            for chunk in (ours, theirs):
                for line in chunk.splitlines():
                    line = line.strip()
                    if not line or line in seen:
                        continue
                    seen.add(line)
                    rows.append(line)

            def key(line):
                m = re.search(r'"ts"\s*:\s*"([^"]+)"', line)
                return m.group(1) if m else line[:19]
            rows.sort(key=key)
            body = '\n'.join(rows) + '\n'
            pick = 'union(%d rows)' % len(rows)
        else:
            o_ts, t_ts = ts_of(ours), ts_of(theirs)
            if o_ts and (not t_ts or o_ts > t_ts):
                body, pick = ours, 'origin-newer(%s>%s)' % (o_ts, t_ts or '-')
            else:
                body, pick = theirs, 'mine(%s vs %s)' % (t_ts or '-', o_ts or '-')
        with open(os.path.join(ROOT, face), 'w', encoding='utf-8', newline='') as f:
            f.write(body)
        sh(['add', '--', face])
        print('resolved %s :: %s' % (face, pick))
    rc4, out4, _ = sh(['status', '--porcelain'])
    left = [l for l in out4.splitlines() if l.startswith('UU')]
    print('UU remaining: %d' % len(left))
    return 0 if not left else 1


if __name__ == '__main__':
    sys.exit(main())
