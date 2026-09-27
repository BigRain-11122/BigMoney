# r99 bm-c resolve patch-2: 3 non-JSON faces (x2 jsonl line-union / REPORT md M-fresher / dashboard_status.js M-fresher sync with .json twin)
import subprocess, io, re, os

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)

def blob(rev, path):
    r = subprocess.run(['git', 'show', rev + path], capture_output=True)
    assert r.returncode == 0, (rev, path, r.stderr[:200])
    return r.stdout

def md_ts(b):
    m = re.search(rb'(generated|ts|updated)["\':\s]+(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)', b)
    return m.group(2).decode() if m else None

def w(p, b):
    with io.open(p, 'wb') as f:
        f.write(b)

# 1) x2_watch_log.jsonl: line-level union (append-only ledger, dedup on full-line identity per R345 894|894->900 precedent)
p = 'results/x2_watch_log.jsonl'
o, t = blob(':2:', p), blob(':3:', p)
lo = [l for l in o.decode('utf-8').splitlines() if l.strip()]
lt = [l for l in t.decode('utf-8').splitlines() if l.strip()]
seen, merged = set(), []
for l in lo + lt:
    if l not in seen:
        seen.add(l); merged.append(l)
w(p, ('\n'.join(merged) + '\n').encode('utf-8'))
print('%s union %d+%d -> %d lines' % (p, len(lo), len(lt), len(merged)))

# 2) REPORT md: same-day idempotent regen face -> M-fresher take-new
p = 'docs/daily_report/REPORT-2026-09-27.md'
o, t = blob(':2:', p), blob(':3:', p)
so, st = md_ts(o), md_ts(t)
pick = t if (st and (so is None or st >= so)) else o
w(p, pick)
print('%s take-%s (ours=%s theirs=%s)' % (p, 'theirs' if pick is t else 'ours', so, st))

# 3) dashboard_status.js: twin of dashboard_status.json (already take-theirs at 19:23:50 vs 19:13:18) -> sync take-theirs
p = 'results/dashboard_status.js'
o, t = blob(':2:', p), blob(':3:', p)
so, st = md_ts(o), md_ts(t)
pick = t if (st and (so is None or st >= so)) else o
w(p, pick)
print('%s take-%s (ours=%s theirs=%s)' % (p, 'theirs' if pick is t else 'ours', so, st))

# marker sweep over all 28 (staged-worktree parity with precommit claw)
uu = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True).stdout.split()
bad = []
for p in uu:
    try:
        txt = io.open(p, 'rb').read()
        if b'<<<<<<<' in txt or b'>>>>>>>' in txt or b'=======' in txt[:0] :  # ======= alone is too generic; use full markers
            bad.append(p)
    except FileNotFoundError:
        bad.append(p + ' (missing)')
bad = [p for p in bad if True]
# strict re-check with distinct conflict markers only
bad = []
for p in uu:
    txt = io.open(p, 'rb').read()
    if b'<<<<<<< ' in txt or b'>>>>>>> ' in txt:
        bad.append(p)
print('UU remaining:', len(uu), '| MARKER SWEEP:', 'CLEAN' if not bad else bad)
print('PATCH2 DONE; next: git add -A + rebase --continue')
