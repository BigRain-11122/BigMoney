# r614 bm-b rebase CODELY.md union resolver: origin/main full blob + my appended
# line (append-only proof via startswith), byte-exact, no PS-redirect anywhere.
import subprocess

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('show failed: %s -> %s' % (ref, r.stderr.decode('utf-8', 'replace')[:200]))
    return r.stdout

origin = show('origin/main:CODELY.md')
base = show('7657d9d8e^:CODELY.md')
mine = show('7657d9d8e:CODELY.md')
assert mine.startswith(base), 'my CODELY change is NOT append-only -- abort'
added = mine[len(base):].strip(b'\n')          # my appended line(s), newline-trimmed
assert added, 'no appended content found'
assert added not in origin, 'my line already present on origin -- nothing to union'
# NOTE: origin CODELY.md may legitimately contain marker STRINGS inside pit-law
# documentation text (bm-a r619 quotes claw markers); only validate structure of
# the append point, not global marker absence.

out = origin if origin.endswith(b'\n') else origin + b'\n'
out += added + b'\n'
with open('CODELY.md', 'wb') as f:
    f.write(out)
print('CODELY union OK: origin %d bytes + my line %d bytes' % (len(origin), len(added)))
