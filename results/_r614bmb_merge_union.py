# r614 bm-b MERGE-context CODELY union: origin/main full blob (incl. bm-c r410
# repairs/appends) + my append-only additions since merge-base. Byte-exact.
import subprocess, sys

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('show failed: %s -> %s' % (ref, r.stderr.decode('utf-8', 'replace')[:200]))
    return r.stdout

mb = subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'],
                    capture_output=True, text=True).stdout.strip()
if not mb:
    raise SystemExit('no merge-base found')
base = show(mb + ':CODELY.md')
mine = show('HEAD:CODELY.md')
theirs = show('origin/main:CODELY.md')
assert mine.startswith(base), 'my CODELY delta is NOT append-only -- manual review needed'
added = mine[len(base):].strip(b'\n')
assert added, 'no local additions found'
assert added not in theirs, 'my additions already on origin -- plain take-theirs is enough'
out = theirs if theirs.endswith(b'\n') else theirs + b'\n'
out += added + b'\n'
with open('CODELY.md', 'wb') as f:
    f.write(out)
print('CODELY MERGE union OK: base=%s theirs=%d bytes + my additions %d bytes'
      % (mb[:9], len(theirs), len(added)))
