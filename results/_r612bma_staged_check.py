import subprocess, json, sys

files = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True).stdout.decode('utf-8').split()
bad = []
for f in files:
    if f.endswith('.json'):
        r = subprocess.run(['git', 'show', ':' + f], capture_output=True)
        try:
            json.loads(r.stdout.decode('utf-8'))
        except Exception as e:
            bad.append((f, str(e)[:80]))
    elif f.endswith('.jsonl'):
        r = subprocess.run(['git', 'show', ':' + f], capture_output=True)
        n = 0
        for line in r.stdout.decode('utf-8', errors='replace').splitlines():
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                o = json.loads(line)
                if not isinstance(o, dict):
                    bad.append((f, 'non-dict row'))
                    break
            except Exception as e:
                bad.append((f, 'row %d: %s' % (n, str(e)[:60])))
                break
if bad:
    for f, e in bad:
        print('BAD:', f, e)
    sys.exit(1)
print('STAGED-BLOBS-OK (%d files validated)' % len(files))
