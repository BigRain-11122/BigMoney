# -*- coding: utf-8 -*-
"""r782 S0 rebase resolver: 31-UU shared regen faces.
Per-face ts evidence (r756 normalize law / r773 per-face law / r758 union law for x2_watch_log).
Host-guarded faces (r378: dashboard/daily_scorecard/strategy_scorecard/daily_report host=bm-a)
-> ours authoritative; everything else -> ts-newer-wins; x2_watch_log.jsonl -> union+stable ts sort.
"""
import json, re, subprocess, sys
from datetime import datetime

def git(*args):
    return subprocess.run(['git'] + list(args), capture_output=True).stdout

def blob(stage, path):
    out = git('show', '%s:%s' % (stage, path))
    return out.decode('utf-8', 'surrogateescape') if out is not None else None

TS_KEYS = ['generated', 'ts', 'updated', 'updated_at', 'asof', 'as_of', 'generated_at', 'written_at', 'scan_time', 'heartbeat_epoch_utc', 'cutoff', 'date']

def norm_ts(v):
    """Normalize mixed-separator timestamps to epoch seconds (r756 law)."""
    if v is None:
        return None
    s = str(v).strip()
    # pure epoch seconds
    if re.fullmatch(r'\d{9,12}', s):
        return float(s)
    # ISO-ish with space or T separator, optional +08:00 offset
    s2 = s.replace(' ', 'T', 1) if 'T' not in s[:11] else s
    m = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:([+-])(\d{2}):?(\d{2}))?', s2)
    if m:
        dt = datetime.strptime(m.group(1) + 'T' + m.group(2), '%Y-%m-%dT%H:%M:%S')
        if m.group(3):
            off = int(m.group(4)) * 3600 + int(m.group(5)) * 60
            if m.group(3) == '+':
                pass
            # convert to naive-beijing baseline: treat all as +08:00 wallclock -> compare directly
        return dt.timestamp() + (8 * 3600)  # naive -> beijing epoch
    # date only
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    if m:
        return datetime.strptime(m.group(1), '%Y-%m-%d').timestamp()
    return None

def deep_max_ts(obj, depth=0):
    """Max timestamp anywhere in the doc (r756 deep-ts probe) - normalized compare."""
    best = None
    if depth > 6:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if any(t in kl for t in ('generated', 'ts', 'updated', 'asof', 'cutoff', 'time', 'date', 'epoch')):
                t = norm_ts(v)
                if t and (best is None or t > best):
                    best = t
            t = deep_max_ts(v, depth + 1)
            if t and (best is None or t > best):
                best = t
    elif isinstance(obj, list):
        for v in obj:
            t = deep_max_ts(v, depth + 1)
            if t and (best is None or t > best):
                best = t
    return best

HOST_OURS = {
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/daily_scorecard.json', 'results/strategy_scorecard.json',
}

def resolve(path):
    ours = blob(':2', path)
    theirs = blob(':3', path)
    if path == 'results/x2_watch_log.jsonl':
        # r758 union law: union dedupe + stable ts sort
        a = [l for l in ours.splitlines() if l.strip()]
        b = [l for l in theirs.splitlines() if l.strip()]
        seen, merged = set(), []
        for l in a + b:  # stable, ours first
            if l not in seen:
                seen.add(l); merged.append(l)
        def line_ts(l):
            m = re.search(r'"ts":\s*"([^"]+)"', l)
            return norm_ts(m.group(1)) if m else 0.0
        # verify pre-sort order roughly ts-ascending; stable sort by ts
        merged.sort(key=line_ts)
        return 'union', '\n'.join(merged) + '\n'
    if path in HOST_OURS:
        return 'host-ours', ours
    # ts-newer-wins via deep probe on JSON; md files -> strip twin? md has no ts easily; use twin json decision
    to, tt = None, None
    try:
        jo, jt = json.loads(ours), json.loads(theirs)
        to, tt = deep_max_ts(jo), deep_max_ts(jt)
    except Exception:
        pass
    if to is None or tt is None:
        # md twins: decide by sibling json
        sibling = path[:-3] + '.json' if path.endswith('.md') else None
        if sibling:
            try:
                jo = json.loads(blob(':2', sibling)); jt = json.loads(blob(':3', sibling))
                to, tt = deep_max_ts(jo), deep_max_ts(jt)
            except Exception:
                pass
    if to is None and tt is None:
        return 'theirs-fallback', theirs
    if tt is None or (to is not None and to >= tt):
        return 'ours-newer(ts %s>=%s)' % (to, tt), ours
    return 'theirs-newer(ts %s>%s)' % (tt, to), theirs

def main():
    out = git('status', '--porcelain').decode('utf-8', 'surrogateescape')
    paths = [l[3:].strip() for l in out.splitlines() if l.startswith('UU')]
    verdicts = {}
    for p in paths:
        mode, content = resolve(p)
        # write resolved content via hash-object -> update-index (no worktree churn needed? worktree has markers; write file directly)
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        subprocess.run(['git', 'add', '--', p], capture_output=True)
        verdicts[p] = mode
    for p, m in sorted(verdicts.items()):
        print('%s -> %s' % (m, p))
    print('TOTAL', len(verdicts))

if __name__ == '__main__':
    main()
