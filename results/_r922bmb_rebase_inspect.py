import subprocess, json, sys

GIT = r'C:\Program Files\Git\cmd\git.exe'


def run(args):
    r = subprocess.run([GIT] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout, r.stderr


rc, out, _ = run(['status', '--porcelain=v1'])
print('=== FULL STATUS ===')
print(out)
rc, out, _ = run(['ls-files', '-u'])
print('=== LS-FILES -U ===')
print(out)
unmerged = {}
for line in out.strip().splitlines():
    parts = line.split()
    mode, sha, stage, path = parts[0], parts[1], int(parts[2]), parts[2+1]
    unmerged.setdefault(path, {})[stage] = sha
print('=== UU FACE BLOBS ===')
for path, stages in unmerged.items():
    for stage, sha in sorted(stages.items()):
        rc, blob, _ = run(['cat-file', '-p', sha])
        try:
            j = json.loads(blob)
            keys = list(j.keys()) if isinstance(j, dict) else f'list[{len(j)}]'
            ts_hits = []
            def find_ts(o, depth=0):
                if depth > 3 or not isinstance(o, dict):
                    return
                for k, v in o.items():
                    kl = str(k).lower()
                    if isinstance(v, str) and ('ts' in kl or 'time' in kl or 'date' in kl or 'updated' in kl) and len(v) >= 8:
                        ts_hits.append(f'{k}={v}')
                    elif isinstance(v, dict):
                        find_ts(v, depth + 1)
            find_ts(j)
            hist_len = len(j.get('history', [])) if isinstance(j, dict) and isinstance(j.get('history'), list) else None
            print(f'{path} stage{stage} sha16={sha[:16]} keys={keys} hist={hist_len} ts={ts_hits[:6]}')
        except Exception as e:
            print(f'{path} stage{stage} sha16={sha[:16]} PARSE_FAIL {type(e).__name__} first120={blob[:120]!r}')
rc, out, _ = run(['check-ignore', 'logs/iteration-loop/round_20261014_013202.out'])
print('=== logs ignore check rc=', rc, '===')
rc, out, _ = run(['stash', 'list'])
print('=== STASH ===')
print(out or '(empty)')
rc, out, _ = run(['rev-parse', 'origin/main'])
print('=== origin/main ===', out.strip())
rc, out, _ = run(['log', '--oneline', '-1', 'origin/main'])
print(out.strip())
