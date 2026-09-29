import subprocess, re

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else None

for st, tag in ((1, 'base'), (2, 'origin'), (3, 'mine')):
    s = blob(st, 'CODELY.md')
    lines = s.splitlines()
    entries = [l for l in lines if l.startswith('- [')]
    print('== stage', st, tag, '| bytes', len(s.encode('utf-8')), '| lines',
          len(lines), '| entries', len(entries))
    for l in entries:
        head = l[:72]
        print('   ', head)
