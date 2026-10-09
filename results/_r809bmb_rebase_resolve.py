# r809 bm-b rebase conflict resolver (canon: bigmoney-conflict-resolve / r773 direction law / r789 lineage)
# Stage2=ours (bm-b r809 absorb), Stage3=theirs (origin 371cc72d7 face).
import json, subprocess, sys

def git(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout, r.stderr

rc, out, _ = git('log', '--format=%h|%an|%s', 'e71a76092..371cc72d7')
print('=== origin advances ===')
print(out.strip())
committers = set(l.split('|')[1] for l in out.strip().splitlines() if '|' in l)
print('committers:', committers)

rc, out, _ = git('diff', '--name-only', '--diff-filter=U')
files = [f for f in out.strip().splitlines() if f]
print('conflicted_n=', len(files))

APPEND_ONLY_PREFIX = ('data/daily/',)  # per-stock daily CSV, append-only, union domain
JSONL_APPEND = ('results/x2_watch_log.jsonl', 'results/post_review.jsonl')
UNION_HISTORY = ('results/compute_audit.json', 'results/regime_state.json', 'results/token_usage.json')
SINGLE_WRITER_BMA = ('results/dashboard_status.json', 'results/dashboard_status.js',
                     'results/daily_scorecard.json', 'results/daily_scorecard.html')

resolved_ours, resolved_theirs, unioned = [], [], []
for f in files:
    rc, ours, _ = git('show', ':2:' + f)
    rc2, theirs, _ = git('show', ':3:' + f)
    if rc != 0 and rc2 != 0:
        resolved_ours.append(f); continue  # both stages missing (delete/delete style) -> keep worktree
    if f.startswith(APPEND_ONLY_PREFIX) or f in JSONL_APPEND:
        # append-only: ours must be a superset (same tree lineage, later snapshot); else union unique rows
        ol, tl = ours.splitlines(), theirs.splitlines()
        if set(tl) <= set(ol):
            open(f, 'w', encoding='utf-8', newline='').write('\n'.join(ol) + ('\n' if ol else ''))
            resolved_ours.append(f)
        else:
            seen, merged = set(), []
            for line in tl + ol:
                if line not in seen:
                    seen.add(line); merged.append(line)
            # restore chronological order for date-sorted CSVs: sort by first column when it looks like a date
            if f.startswith(APPEND_ONLY_PREFIX):
                try:
                    merged.sort(key=lambda x: (x.split(',')[0],))
                except Exception:
                    pass
            open(f, 'w', encoding='utf-8', newline='').write('\n'.join(merged) + ('\n' if merged else ''))
            unioned.append(f)
    elif f in SINGLE_WRITER_BMA and committers - {'bm-b'}:
        # host=bm-a single-writer faces (r378 law): bm-a side wins regardless of ts
        open(f, 'w', encoding='utf-8', newline='').write(theirs)
        resolved_theirs.append(f)
    else:
        # regen snapshot faces: ours = the verified on-disk estate products (same-day idempotent regen,
        # cosmetic ts deltas only); bm-b lane continuity + our QA evidence chain -> ours
        open(f, 'w', encoding='utf-8', newline='').write(ours if rc == 0 else theirs)
        resolved_ours.append(f)

print('ours:', len(resolved_ours), 'theirs:', len(resolved_theirs), 'unioned:', len(unioned))
if unioned: print('UNIONED FILES:', unioned)
if resolved_theirs: print('THEIRS (single-writer law):', resolved_theirs)

# marker sweep + JSON parse verify on resolved faces
bad = []
for f in files:
    try:
        body = open(f, encoding='utf-8', errors='replace').read()
    except Exception:
        continue
    if '<<<<<<<' in body or '>>>>>>>' in body or '=======' in body and f.endswith(('.json', '.md', '.csv', '.js')):
        if '<<<<<<<' in body or '>>>>>>>' in body:
            bad.append(f)
    if f.endswith('.json'):
        try:
            json.loads(body)
        except Exception:
            bad.append(f + ' (json-parse)')
print('verify bad faces:', bad if bad else 'NONE')
if bad:
    sys.exit(2)
print('RESOLVE-OK')
