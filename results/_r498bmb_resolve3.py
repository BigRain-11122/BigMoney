# r498 cherry-pick conflict resolver (15 UU): append-ledger union by ts / take-newer snapshot (R208/R209/r498-bm-a AA)
import subprocess, json, sys

def stage(path, n):
    r = subprocess.run(['git', 'show', ':%d:%s' % (n, path)], capture_output=True)
    if r.returncode != 0:
        print('STAGE_FAIL', n, path, r.stderr.decode()[:150]); sys.exit(2)
    return r.stdout

def w(path, data_bytes):
    with open(path, 'wb') as f:
        f.write(data_bytes)

UU = [l.strip() for l in subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
     capture_output=True).stdout.decode().splitlines() if l.strip()]

report = 'logs/iteration-loop/round_reports.md'
log = []

def parse_ts(line):
    # lines start with ISO ts "2026-10-01T08:20:53+08:00 | ..."
    return line[:1] >= '0' and line[:2] >= '20' and 'T' in line[:11]

for path in UU:
    s2, s3 = stage(path, 2), stage(path, 3)
    if path == report:
        # append-ledger union: merge-sort tail lines by ts, dedupe identical
        a = s2.decode('utf-8').splitlines()
        b = s3.decode('utf-8').splitlines()
        # common prefix (both share the base history)
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        tail_a, tail_b = a[i:], b[i:]
        seen, merged = set(), []
        import re
        def tskey(l):
            m = re.match(r'(2026-\d\d-\d\dT[\d:]+)', l)
            return m.group(1) if m else '9999'
        for l in sorted(tail_a + tail_b, key=tskey):
            if l in seen or not l.strip():
                continue
            seen.add(l); merged.append(l)
        out = a[:i] + merged
        log.append('%s UNION tail_a=%d tail_b=%d merged=%d' % (path, len(tail_a), len(tail_b), len(merged)))
        w(path, ('\r\n'.join(out) + '\r\n').encode('utf-8'))
        continue
    if path.endswith('.json'):
        try:
            j2, j3 = json.loads(s2), json.loads(s3)
        except Exception as e:
            log.append('%s JSON_PARSE_FAIL %s -> take stage2' % (path, e)); w(path, s2); continue
        keys2 = set(j2) if isinstance(j2, dict) else None
        if isinstance(j2, dict) and isinstance(j3, dict):
            # take-newer by ts-ish key, union per-machine sub-dicts when present
            t2 = j2.get('ts') or j2.get('updated') or j2.get('updated_at') or ''
            t3 = j3.get('ts') or j3.get('updated') or j3.get('updated_at') or ''
            if isinstance(j2.get('machines'), dict) and isinstance(j3.get('machines'), dict):
                mm = dict(j2['machines']); mm.update(j3['machines'])
                out = dict(j3 if t3 >= t2 else j2); out['machines'] = mm
                log.append('%s machines-union %d -> %d' % (path, len(j2['machines']), len(mm)))
            elif all(isinstance(j2.get(k), dict) and isinstance(j3.get(k), dict)
                      for k in keys2 & set(j3) if k not in ('ts', 'updated', 'updated_at', 'generated')) and len(keys2 & set(j3)) >= 3 and 'bm-a' in j3 and 'bm-b' in j3:
                # per-machine keyed ledger (token_usage style): union machine keys, newer top-level ts wins
                out = dict(j3 if t3 >= t2 else j2)
                for k in set(j2) | set(j3):
                    if k in ('ts', 'updated', 'updated_at', 'generated'): continue
                    if isinstance(j2.get(k), dict) and isinstance(j3.get(k), dict):
                        out[k] = {**j2.get(k, {}), **j3.get(k, {})}
                log.append('%s per-machine-union' % path)
            else:
                out = j3 if (t3 and t2 and t3 >= t2) else j2  # take-newer, tie/unknown -> stage2 (origin base)
                log.append('%s snapshot take-%s (t2=%s t3=%s)' % (path, '3' if out is j3 else '2', t2, t3))
        else:
            out = j2; log.append('%s non-dict take2' % path)
        txt = json.dumps(out, ensure_ascii=False, indent=1)
        crlf = b'\r\n' in s2[:400]
        if crlf: txt = txt.replace('\n', '\r\n')
        w(path, (txt + ('\r\n' if crlf else '\n')).encode('utf-8'))
        continue
    # .md regenerated faces (REPORT/LIVE): take stage2 (origin, deterministic same-cutoff derive)
    w(path, s2); log.append('%s md take2 (regen face, same cutoff derive)' % path)

# validation pass: every resolved json parses; report tail sanity
for path in UU:
    if path.endswith('.json'):
        json.loads(open(path, encoding='utf-8').read())
print('RESOLVED %d files' % len(UU))
for l in log: print(' |', l)
