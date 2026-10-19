import subprocess, json, os

def run(*a):
    return subprocess.run(list(a), capture_output=True, text=True, encoding='utf-8', errors='replace')

# --- 1. watermark_red.json DU: keep disk (stash freshest 15:03:04), accept origin deletion in index ---
r = subprocess.run(['git','rm','--cached','--','results/watermark_red.json'], capture_output=True, text=True)
print('rm --cached:', (r.stdout or r.stderr).strip())
p = 'results/watermark_red.json'
print('disk exists:', os.path.exists(p))
if os.path.exists(p):
    d = json.load(open(p, encoding='utf-8'))
    print('disk ts:', d.get('ts'))

r = subprocess.run(['git','check-ignore','-v','results/watermark_red.json'], capture_output=True, text=True)
print('check-ignore:', (r.stdout.strip() or 'NOT-IGNORED'), r.stderr.strip())

# --- 2. marks-20261019.jsonl UU: line-union per r419 ---
mp = 'results/paper/marks/marks-20261019.jsonl'
head = run('git','show','HEAD:'+mp).stdout
ours = run('git','show',':2:'+mp).stdout
theirs = run('git','show',':3:'+mp).stdout
disk = open(mp, encoding='utf-8', errors='replace').read() if os.path.exists(mp) else ''
print('lens head/ours/theirs/disk:', len(head), len(ours), len(theirs), len(disk))

def valid_lines(txt):
    out = []
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            json.loads(ln)
            out.append(ln)
        except Exception:
            pass
    return out

pool = {}
for src in (head, ours, theirs, disk):
    for ln in valid_lines(src):
        pool[ln] = True
lines = sorted(pool.keys())
bad = sum(1 for ln in lines if not _valid(ln)) if False else 0
for ln in lines:
    try:
        json.loads(ln)
    except Exception:
        bad += 1
with open(mp, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + ('\n' if lines else ''))
print('union lines:', len(lines), 'invalid:', bad)
subprocess.run(['git','add','--',mp])
r = subprocess.run(['git','diff','--check'], capture_output=True, text=True)
print('diff --check rc:', r.returncode, (r.stdout or r.stderr).strip()[:200])
r = subprocess.run(['git','status','--short'], capture_output=True, text=True)
print('status now:')
print(r.stdout[:800])
