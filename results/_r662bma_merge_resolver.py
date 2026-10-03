# -*- coding: utf-8 -*-
"""r662 bm-a merge resolver: 14 UU S6 regen faces -> deep ts compare per face, newer-wins.

Recipe: r640/r661 (twins: json deep-probe ts picks side; md follows same side byte-copy;
single-source faces: deep ts compare). Markers: strip ours-keep, post->>>>>>> tail (r630 surgery
law adapted); assert no marker residue after resolve (r644 content-check law).
"""
import json, re, subprocess, sys, os

UU = [
    'docs/daily_report/REPORT-2026-10-04.json',
    'docs/daily_report/REPORT-2026-10-04.md',
    'docs/live_usage/LIVE-2026-10-04.json',
    'docs/live_usage/LIVE-2026-10-04.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]

MARK_O = b'<<<<<<<'
MARK_S = b'======='
MARK_E = b'>>>>>>>'

def split_sides(blob):
    """Return (ours, theirs, had_conflict). ours = HEAD side, theirs = origin side.
    Normal (auto-merged shared) lines belong to BOTH sides."""
    if MARK_O not in blob:
        return blob, None, False
    ours_parts, theirs_parts = [], []
    state = 'normal'
    for ln in blob.split(b'\n'):
        if ln.startswith(MARK_O):
            state = 'ours'
            continue
        if ln.startswith(MARK_S):
            state = 'theirs'
            continue
        if ln.startswith(MARK_E):
            state = 'normal'
            continue
        if state == 'ours':
            ours_parts.append(ln)
        elif state == 'theirs':
            theirs_parts.append(ln)
        else:
            ours_parts.append(ln)
            theirs_parts.append(ln)
    return b'\n'.join(ours_parts), b'\n'.join(theirs_parts), True

TS_RE = re.compile(r'"(?:ts|timestamp|generated_at|asof)"\s*:\s*"([^"]+)"')

def probe_ts(blob):
    hits = TS_RE.findall(blob.decode('utf-8', 'replace'))
    return hits[0] if hits else ''

def resolve(face):
    blob = open(face, 'rb').read()
    ours, theirs, conflicted = split_sides(blob)
    if not conflicted:
        return ('clean-already', probe_ts(blob))
    to, tt = probe_ts(ours) or '1970', probe_ts(theirs) or '1970'
    if to >= tt:
        winner, side = ours, 'ours(%s>=%s)' % (to or '-', tt or '-')
    else:
        winner, side = theirs, 'theirs(%s>%s)' % (tt, to)
    open(face, 'wb').write(winner)
    # post-verify: no marker residue
    rb = open(face, 'rb').read()
    assert MARK_O not in rb and MARK_E not in rb, 'marker residue in %s' % face
    return (side, to)

results = {}
for f in UU:
    side, ts = resolve(f)
    results[f] = side
    print('%s -> %s' % (f, side))

# json faces must parse after resolve
for f in UU:
    if f.endswith('.json'):
        json.load(open(f, encoding='utf-8'))
print('ALL_JSON_PARSE_OK')
