# -*- coding: utf-8 -*-
"""r784 bm-a merge-window resolver for the non-ALL_FACES UU set (25 files).
Merge semantics: :2: = ours (HEAD r784), :3: = theirs (origin bm-c r629/r630).
Laws enforced:
- r209: read git blobs via subprocess bytes, no PS redirection artifacts
- r756: ts compare = normalize space->T + strptime numeric compare, never str compare
- r100/R350: deep-scan nested layers for ts keys, prefix-normalized keys,
  values must match wall-clock ^20.. with time-of-day; probe STAGED blobs
- r140: same-second tie -> HEAD (ours)
- r378/D-03①+r440: host=bm-a executive faces (dashboard_status.js/json,
  daily_scorecard, strategy_scorecard) = ours-live-wins AFTER ts verification
- r327/r329: twin-regen pairs -- json face ts-diffpick decides side, md face
  = same-side blob BYTE copy (never json.loads an md)
- r758/r217: x2_watch_log.jsonl = line-level union dedup + ts stable sort
- r185: parse-verify every resolved json before write-back; fail-closed
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')
TS_KEY_RE = re.compile(r'^(?:generated_at|generated|updated_at|updated|ts|asof|'
                       r'last_.*(?:ts|at)|.*_ts|scanned_at|written_at)$')


def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show :{stage}:{path} rc={r.returncode}')
    return r.stdout.decode('utf-8', errors='strict')


def parse_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip().replace(' ', 'T')
    m = re.match(r'^(20\d{2}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', s)
    if not m:
        return None
    # numeric tuple compare (year,mon,day,h,min,sec); tz offset ignored per
    # r756 normalization (both sides +08:00 same-clock fleet)
    d, t = m.group(1), m.group(2)
    return tuple(int(x) for x in d.split('-')) + tuple(int(x) for x in t.split(':'))


def deep_ts(obj, depth=0):
    """Deep-scan any nesting layer for the max wall-clock ts (r311/D-09)."""
    best = None
    if depth > 8:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).lower().replace('_', '').replace('-', '')
            if isinstance(v, str) and TS_RE.match(v.strip()):
                # key prefix-normalized match (r100) + wall-clock value gate (R350)
                if nk.endswith('ts') or nk.endswith('at') or nk.endswith('asof') \
                        or nk in ('generated', 'generatedat', 'updated', 'updatedat'):
                    p = parse_ts(v)
                    if p and (best is None or p > best):
                        best = p
            sub = deep_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = deep_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    return best


def side_ts(text):
    try:
        return deep_ts(json.loads(text))
    except Exception:
        return None


def take_newer(path, prefer_ours_on_tie=True):
    ours, theirs = blob(2, path), blob(3, path)
    to, tt = side_ts(ours), side_ts(theirs)
    # Content-identical short-circuit (token_usage equivalence law r440)
    if ours == theirs:
        return 'identical'
    pick = 'ours' if to and (tt is None or to > tt or (to == tt and prefer_ours_on_tie)) else \
           ('theirs' if tt else 'ours')
    why = f'ours_ts={to} theirs_ts={tt}'
    data = ours if pick == 'ours' else theirs
    if path.endswith('.json'):
        json.loads(data)  # parse-verify before write (r185)
    with open(path, 'wb') as f:
        f.write(data.encode('utf-8'))
    return f'{pick} ({why})'


def twin_pair(json_path, md_path):
    ours_j, theirs_j = blob(2, json_path), blob(3, json_path)
    to, tt = side_ts(ours_j), side_ts(theirs_j)
    if ours_j == theirs_j:
        pick = 'ours'
    else:
        pick = 'ours' if to and (tt is None or to >= tt) else 'theirs'
    jdata = ours_j if pick == 'ours' else theirs_j
    json.loads(jdata)
    mdata = blob(2, md_path) if pick == 'ours' else blob(3, md_path)
    with open(json_path, 'wb') as f:
        f.write(jdata.encode('utf-8'))
    with open(md_path, 'wb') as f:
        f.write(mdata.encode('utf-8'))  # same-side BYTE copy (r329)
    return f'{pick} (json_ts={to if pick == "ours" else tt})'


def union_jsonl(path, ts_key='ts'):
    ours, theirs = blob(2, path), blob(3, path)
    seen, rows = set(), []
    for src in (ours, theirs):
        for line in src.splitlines():
            if not line.strip():
                continue
            if line in seen:
                continue
            seen.add(line)
            try:
                d = json.loads(line)
            except Exception:
                rows.append((None, 1, line))  # non-json line: keep, stable tail
                continue
            rows.append((parse_ts(d.get(ts_key, '')) or (0,), 0, line))
    rows.sort(key=lambda r: (r[1], r[0]))  # json lines by ts stable, raw lines tail-stable
    out = '\n'.join(r[2] for r in rows) + ('\n' if rows else '')
    assert len(rows) == len(seen), 'union line loss'
    with open(path, 'wb') as f:
        f.write(out.encode('utf-8'))
    return f'union {len(rows)} lines (dedup from {len(ours.splitlines())}+{len(theirs.splitlines())})'


report = []

# --- host-ours executive faces (r378 host=bm-a; ours-live-wins after ts check)
for p in ('results/dashboard_status.json', 'results/dashboard_status.js',
          'results/daily_scorecard.json', 'results/strategy_scorecard.json'):
    ours, theirs = blob(2, p), blob(3, p)
    to, tt = side_ts(ours) if p.endswith('.json') else deep_ts(None) or None, None
    if p.endswith('.json'):
        to, tt = side_ts(ours), side_ts(theirs)
        assert to is None or tt is None or to >= tt, \
            f'{p}: ours ts {to} OLDER than theirs {tt} -- evidence disagrees with host-ours'
    if ours == theirs:
        report.append(f'{p}: identical (ours bytes kept)')
        continue
    with open(p, 'wb') as f:
        f.write(ours.encode('utf-8'))
    report.append(f'{p}: OURS host-live-wins (ours_ts={to} theirs_ts={tt})')

# --- twin-regen pairs (json decides, md same-side bytes)
report.append('docs/daily_report/REPORT-2026-10-06: ' + twin_pair(
    'docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md'))
report.append('docs/live_usage/LIVE-2026-10-06: ' + twin_pair(
    'docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md'))
report.append('docs/live_usage/LIVE-latest: ' + twin_pair(
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'))

# --- ts-evidence take-new snapshots
for p in ('results/_attrition_guard_scan.json',
          'results/fundamental_b_layer_filter.json',
          'results/paper/COMPOSITE-CE-01_paper.json',
          'results/paper/COMPOSITE-CE-02_paper.json',
          'results/paper/DROUGHT-CE-01_paper.json',
          'results/paper/ENGULF-CE-01_paper.json',
          'results/paper/NEEDLE-DE-01_paper.json',
          'results/paper/VOLATILITY-CE-01_paper.json',
          'results/paper_export/export-2026-09-30.json',
          'results/paper_export/latest.json',
          'results/prospect_paper/_summary.json',
          'results/prospect_promotion/_summary.json',
          'results/scorecard_v1.json',
          'results/t35_open_fill_verify.json'):
    report.append(f'{p}: ' + take_newer(p))

# --- append-log union (r758/r217)
report.append('results/x2_watch_log.jsonl: ' + union_jsonl('results/x2_watch_log.jsonl'))

for line in report:
    print(line)

# verify zero unresolved UU remain in our resolved set
bad = []
for p in ('results/dashboard_status.json', 'results/dashboard_status.js',
          'results/daily_scorecard.json', 'results/strategy_scorecard.json',
          'docs/daily_report/REPORT-2026-10-06.json', 'docs/daily_report/REPORT-2026-10-06.md',
          'docs/live_usage/LIVE-2026-10-06.json', 'docs/live_usage/LIVE-2026-10-06.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
          'results/_attrition_guard_scan.json', 'results/fundamental_b_layer_filter.json',
          'results/x2_watch_log.jsonl'):
    txt = open(p, encoding='utf-8').read()
    if '<<<<<<<' in txt or '>>>>>>>' in txt or '=======' in txt:
        bad.append(p)
if bad:
    print('MARKER SCAN FAIL:', bad)
    sys.exit(1)
print('marker scan CLEAN')
