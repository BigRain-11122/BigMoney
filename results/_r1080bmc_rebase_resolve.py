# -*- coding: utf-8 -*-
# r1080 bm-c: rebase conflict resolver for pick 9758fd875 (50th-gen absorb window)
# Policies: r1028 ts-newer-wins (watermark_red) / r1034 newer-regenerable (S6 product faces) /
# append-only line-union (jsonl logs + REPORT md) / per-machine probe evidence take local-mine.
# Single-pass order-preserving rebuild (plain segments stay in place).
import re

TS_RE = re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')

def first_ts(lines):
    for ln in lines:
        m = TS_RE.search(ln)
        if m:
            return m.group(0).replace('T', ' ')
    return ''

def policy_newer(ours, base, theirs):
    a, b = first_ts(ours), first_ts(theirs)
    return ours if a >= b else theirs

def policy_union(ours, base, theirs):
    seen, merged = set(), []
    for ln in ours + theirs:
        k = ln.strip()
        if k in seen:
            continue
        seen.add(k); merged.append(ln)
    return merged

def policy_mine(ours, base, theirs):
    return theirs if theirs else ours

def resolve_file(path, pol):
    text = open(path, encoding='utf-8', errors='replace').read()
    if '<<<<<<<' not in text:
        print('SKIP(no-markers):', path)
        return
    lines = text.split('\n')
    out, state = [], None
    ours, base, theirs = [], [], []
    nblocks = 0
    for ln in lines:
        if ln.startswith('<<<<<<<'):
            state = 'ours'; continue
        if ln.startswith('|||||||'):
            state = 'base'; continue
        if ln.startswith('=======') and state in ('ours', 'base'):
            state = 'theirs'; continue
        if ln.startswith('>>>>>>>'):
            out.extend(pol(ours, base, theirs))
            ours, base, theirs = [], [], []
            state = None
            nblocks += 1
            continue
        if state == 'ours':
            ours.append(ln)
        elif state == 'base':
            base.append(ln)
        elif state == 'theirs':
            theirs.append(ln)
        else:
            out.append(ln)
    open(path, 'w', encoding='utf-8', newline='').write('\n'.join(out))
    print('RESOLVED:', path, 'blocks=%d' % nblocks)

FILES = {
    'results/watermark_red.json': policy_newer,
    'docs/live_usage/LIVE-latest.md': policy_newer,
    'results/daily_scorecard.json': policy_newer,
    'results/paper_export/latest.json': policy_newer,
    'results/paper_export/export-2026-10-16.json': policy_newer,
    'results/_r686bmb_d19_check.json': policy_mine,
    'results/_r686bmb_orders_fresh.md': policy_mine,
    'results/post_review.jsonl': policy_union,
    'results/x2_watch_log.jsonl': policy_union,
    'results/post_review/REPORT-20261018.md': policy_union,
}

for path, pol in FILES.items():
    resolve_file(path, pol)
print('DONE')
