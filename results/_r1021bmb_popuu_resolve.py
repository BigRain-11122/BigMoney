"""r1021 bm-b: stash-pop UU resolver for watermark_red.json (newer-wins)."""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = 'results/watermark_red.json'


def sh(args):
    p = subprocess.run(['git'] + args, cwd=ROOT, capture_output=True,
                       creationflags=0x08000000)
    return (p.stdout or b'').decode('utf-8', 'replace')


def ts_of(text):
    best = ''
    for key in ('"ts"', '"checked_at"'):
        for m in re.finditer(re.escape(key) + r'\s*:\s*"([^"]+)"', text):
            if m.group(1) > best:
                best = m.group(1)
    return best


def main():
    st = sh(['status', '--porcelain'])
    uu = [l[3:].strip() for l in st.splitlines() if l.startswith('UU')]
    print('UU faces: %s' % uu)
    for FACE in uu:
        ours = sh(['show', ':2:' + FACE])
        theirs = sh(['show', ':3:' + FACE])
        o_ts, t_ts = ts_of(ours), ts_of(theirs)
        body = ours if (o_ts and (not t_ts or o_ts > t_ts)) else theirs
        with open(os.path.join(ROOT, FACE), 'w', encoding='utf-8', newline='') as f:
            f.write(body)
        subprocess.run(['git', 'add', '--', FACE], cwd=ROOT, capture_output=True,
                       creationflags=0x08000000)
        print('resolved %s :: origin=%s stash=%s -> %s' % (
            FACE, o_ts[:19] or '-', t_ts[:19] or '-',
            'origin-newer' if body == ours else 'stash-newer'))
    st2 = sh(['status', '--porcelain'])
    left = [l for l in st2.splitlines() if l.startswith('UU')]
    print('UU remaining: %d' % len(left))


if __name__ == '__main__':
    main()
