"""r504 bm-b rebase resolver (r503 recipe lineage + skill classify output):
  - results/pool_core_samples.jsonl : append-log -> line-level union zero loss (r503 verbatim)
  - results/compute_audit.json      : rolling-ledger -> history union (content-identity dedupe,
                                      ts-asc sort) + latest take-new via deep ts probe (r188/R208)
Write-back: indent/CRLF mirror of base blob (r223/r234 law); parse-verify before add (r185 law)."""
import subprocess, json, re, io

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'


def show(spec, path):
    return subprocess.check_output(['git', '-C', REPO, 'show', spec + path])


def detect_format(raw_bytes):
    crlf = raw_bytes.count(b'\r\n')
    lf = raw_bytes.count(b'\n') - crlf
    eol = '\r\n' if crlf > lf else '\n'
    txt = raw_bytes.decode('utf-8')
    m = re.search(r'^([ \t]*)"', txt, re.M)
    indent = len(m.group(1)) if m else 2
    return eol, indent


# ---------- 1. pool_core_samples.jsonl (append-log line union) ----------
p = REPO + r'\results\pool_core_samples.jsonl'
raw = open(p, 'rb').read().decode('utf-8')
blocks = re.findall(r'(?ms)^<<<<<<< HEAD\n(.*?)\n?=======\n(.*?)\n?>>>>>>> [^\n]*\n', raw)
print('samples: n_blocks', len(blocks))
out = []
for ours, theirs in blocks:
    lines = [l for l in (ours + '\n' + theirs).split('\n') if l.strip()]
    seen, kept = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l)
            kept.append(l)
    kept.sort(key=lambda l: re.search(r'"ts": "([^"]+)"', l).group(1))
    out.extend(kept)
res = re.sub(r'(?ms)^<<<<<<< HEAD\n.*?\n?>>>>>>> [^\n]*\n',
             lambda m: '\n'.join(out) + '\n', raw, count=0)
assert not re.findall(r'<<<<<<<|>>>>>>>', res), 'markers left in samples'
open(p, 'wb').write(res.encode('utf-8'))
print('samples: resolved_lines', len(out))

# ---------- 2. compute_audit.json (rolling-ledger) ----------
path = 'results/compute_audit.json'
ours = json.loads(show(':2:', path).decode('utf-8'))
theirs = json.loads(show(':3:', path).decode('utf-8'))

def rowkey(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

merged, seen = [], set()
for r in ours.get('history', []) + theirs.get('history', []):
    k = rowkey(r)
    if k not in seen:
        seen.add(k)
        merged.append(r)
merged.sort(key=lambda r: r['ts'])
print('ca: history ours=%d theirs=%d union=%d' % (len(ours['history']), len(theirs['history']), len(merged)))

lo, lt = ours.get('latest', {}), theirs.get('latest', {})
tso, tst = lo.get('ts', ''), lt.get('ts', '')
latest = lt if tst >= tso else lo  # deep probe: latest.ts lives one level down (r311 lesson)
print('ca: latest take-new: ours_ts=%s theirs_ts=%s -> %s' % (tso, tst, 'theirs' if tst >= tso else 'ours'))

final = {'history': merged, 'latest': latest}

base_raw = show(':2:', path)
eol, indent = detect_format(base_raw)
body = json.dumps(final, ensure_ascii=False, indent=indent)
if eol == '\r\n':
    body = body.replace('\n', '\r\n')
with open(REPO + '\\' + path.replace('/', '\\'), 'wb') as f:
    f.write(body.encode('utf-8'))
print('ca: wrote eol=%r indent=%d' % (eol, indent))

# ---------- parse-verify both (r185) ----------
json.loads(open(p, encoding='utf-8').read().splitlines()[0])  # first sample line parses
[json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]  # every line parses
d = json.loads(open(REPO + '\\' + path.replace('/', '\\'), encoding='utf-8').read())
assert len(d['history']) == len(merged) and d['latest']['ts'] == latest['ts']
print('PARSE_VERIFY_OK')
