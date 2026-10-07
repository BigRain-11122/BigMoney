import subprocess
import sys
import io
import json
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run(args, env_extra=None):
    e = dict(os.environ)
    if env_extra:
        e.update(env_extra)
    p = subprocess.run(args, capture_output=True, env=e)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def blob(spec, path):
    rc, o, e = run(['git', 'show', spec + ':' + path])
    return json.loads(o) if rc == 0 else None

faces = ['results/saturation_engine/face_bm-c.json',
         'results/saturation_engine_state.bm-c.json']
for f in faces:
    s2 = blob(':2', f)   # rebase ours = round commit (2b46809ff, absorbed 04:13 churn)
    s3 = blob(':3', f)   # rebase theirs = tail commit (04:12 churn)
    t2 = (s2 or {}).get('ts') or (s2 or {}).get('updated') or str(s2)[:80]
    t3 = (s3 or {}).get('ts') or (s3 or {}).get('updated') or str(s3)[:80]
    print(f, '| stage2 ts:', t2, '| stage3 ts:', t3)
    pick = s2 if (str(t2) >= str(t3)) else s3   # newer-wins whole-face
    json.dumps(pick)                            # reparse gate
    open(f, 'w', encoding='utf-8', newline='').write(
        json.dumps(pick, indent=1, ensure_ascii=False) + '\n')
    print('  resolved ->', 'stage2' if pick is s2 else 'stage3')

rc, o, e = run(['git', 'add', '--'] + faces)
print('add rc', rc)
rc, o, e = run(['git', 'rebase', '--continue'], env_extra={'GIT_EDITOR': 'true'})
print('continue rc', rc)
print((o + e)[:400])
print('rebase-merge still exists:', os.path.exists('.git/rebase-merge'))
rc, o, e = run(['git', 'log', '--oneline', '-4'])
print(o)
