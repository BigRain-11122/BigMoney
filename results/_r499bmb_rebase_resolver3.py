"""r499bm-b re-fire wave-2 resolver: pull --rebase onto 63e442439 (bm-a r508
N1-W4 finalize + bm-c r306). Self-detects unmerged set, applies class recipes.

Adjudications (manual, this session):
- PERPETUAL_N1_W3_PREREG.md: s7/s8 backfill twins, numbers identical
  (K=6720 mu=-0.0904 sigma=0.2479 K-lift +0.0082 p95-miss 0.0403>0.03 3/4);
  origin's provenance narrative matches the landed products this tree carries
  (wave-1 took origin shard products + finalize) -> take :2:.
- result JSONs: merge_lane_views tool recipes + origin-format mirror (r289).
"""
import subprocess
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s -> rc=%d: %s' % (
            ' '.join(a), r.returncode, r.stderr.decode(errors='replace')[:300]))
    return r.stdout


def stage(path, n):
    return git('show', ':%d:%s' % (n, path))


def probe_fmt(raw_bytes):
    raw = raw_bytes.decode('utf-8', 'replace')
    crlf = '\r\n' in raw
    m = re.search(r'\{[\r\n]+( +)"', raw)
    indent = len(m.group(1)) if m else 1
    return crlf, indent


def write_json_fmt(path, doc, crlf, indent):
    payload = json.dumps(doc, ensure_ascii=False, indent=indent)
    if crlf:
        payload = payload.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(payload + ('\r\n' if crlf else '\n'))
    back = json.load(open(path, encoding='utf-8'))
    assert back == doc, 'parse-verify failed %s (r185 law)' % path


unmerged = []
for line in git('ls-files', '-u').decode().splitlines():
    if line.strip():
        unmerged.append(line.split('\t')[1])
print('unmerged set (%d): %s' % (len(unmerged), sorted(set(unmerged))))

resolved = []
for p in sorted(set(unmerged)):
    if p == 'research/PERPETUAL_N1_W3_PREREG.md':
        with open(p, 'wb') as fh:
            fh.write(stage(p, 2))
        resolved.append(p)
        print('[take-origin] %s (s7/s8 twins, origin provenance matches tree)' % p)
    elif p == 'results/fundamental_b_layer_filter.json':
        d2 = json.loads(stage(p, 2))
        d3 = json.loads(stage(p, 3))
        if d3.get('updated', '') >= d2.get('updated', ''):
            take, side, why = stage(p, 3), ':3:', d3.get('updated')
        else:
            take, side, why = stage(p, 2), ':2:', d2.get('updated')
        with open(p, 'wb') as fh:
            fh.write(take)
        resolved.append(p)
        print('[take-new] %s (newest updated=%s from %s)' % (p, why, side))
    elif p.startswith('results/') and p.endswith('.json'):
        b2 = stage(p, 2)
        crlf, indent = probe_fmt(b2)
        r = subprocess.run(['python', 'scripts/merge_lane_views.py',
                            'resolve', p], capture_output=True)
        out = r.stdout.decode(errors='replace')
        tail = [l for l in out.splitlines() if l.strip().startswith('- ')][-4:]
        print('[tool-resolve] %s rc=%d fmt(crlf=%s indent=%d): %s' % (
            p, r.returncode, crlf, indent, ' | '.join(tail)))
        if r.returncode != 0:
            print(out)
            raise SystemExit('tool resolve failed for %s' % p)
        doc = json.load(open(p, encoding='utf-8'))
        write_json_fmt(p, doc, crlf, indent)
        resolved.append(p)
    else:
        raise SystemExit('unclassified unmerged entry: %s -- fail-closed' % p)

git('add', '--', *resolved)
left = subprocess.run(['git', 'ls-files', '-u'], capture_output=True).stdout.decode()
n_left = len([x for x in left.splitlines() if x.strip()])
print('=== unmerged remaining: %d | resolved this wave: %d ===' % (n_left, len(resolved)))
if n_left:
    sys.exit(3)
print('RESOLVE-OK wave2')
