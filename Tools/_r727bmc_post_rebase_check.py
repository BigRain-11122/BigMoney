import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# r651 law: marker scan scope = THIS window's changed faces only
p = subprocess.run(['git', 'diff', '--name-only', '14e1326d3..HEAD'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
faces = [f for f in p.stdout.splitlines() if f]
print('changed faces in replayed window:', len(faces))
bad = []
for f in faces:
    try:
        t = open(f, 'rb').read()
    except OSError:
        continue
    if b'<<<<<<<' in t or b'>>>>>>>' in t or b'|||||||' in t:
        bad.append(f)
print('scoped marker scan bad:', bad if bad else 'ZERO')
