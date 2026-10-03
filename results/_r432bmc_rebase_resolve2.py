# -*- coding: utf-8 -*-
# r432 bm-c rebase pick-2 (c28af278f r431 S7 wrap) conflict resolver, 16 UU files.
# Law: r630 pick-verify-absorbed -> pick-2 payload (r431-era runtime/bookkeeping
# state) is absorbed-or-superseded upstream (bm-a r644 S6 regenerated faces ~22:0x;
# r431 wrap content already pushed). Resolution = TAKE OURS (origin authoritative).
# Bookkeeping faces (heartbeat/round-report) carry needle assertions: if the r431
# content needle is absent from ours, fall back to per-hunk UNION (ours+theirs).
# All .json resolutions validated by json.loads. Marker-line anchored, byte-exact.
import json
import re
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

FILES = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "fleet/machines/bm-c.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
    "round_reports-bm-c.md",
]

# needles that MUST survive in the final text of bookkeeping faces (r431 payload)
NEEDLES = {
    "fleet/machines/bm-c.json": ["O-20261003-2030-bm-c.md", "r431"],
    "round_reports-bm-c.md": ["r431"],
}

MARK_START = re.compile(r'^<<<<<<< ')
MARK_MID = re.compile(r'^\|\|\|\|\|\|\| ')
MARK_SEP = re.compile(r'^=======$')
MARK_END = re.compile(r'^>>>>>>> ')


def hunks(lines):
    """Yield (ours, base, theirs, start_idx, end_idx) per conflict hunk."""
    i, out = 0, []
    while i < len(lines):
        if MARK_START.match(lines[i].rstrip('\r')):
            s = i
            m = p = e = None
            j = i + 1
            while j < len(lines):
                if MARK_MID.match(lines[j].rstrip('\r')) and m is None:
                    m = j
                elif MARK_SEP.match(lines[j].rstrip('\r')) and m is not None and p is None:
                    p = j
                elif MARK_END.match(lines[j].rstrip('\r')) and p is not None:
                    e = j
                    break
                j += 1
            assert None not in (m, p, e), 'malformed hunk at line %d' % (s + 1)
            out.append((lines[s + 1:m], lines[m + 1:p], lines[p + 1:e], s, e))
            i = e + 1
        else:
            i += 1
    return out


def resolve(rel, union_fallback):
    path = REPO + '\\' + rel.replace('/', '\\')
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    lines = text.split('\n')
    hh = hunks(lines)
    assert hh, 'no conflict hunks found in %s' % rel
    new_lines, cursor, strategy = [], 0, 'take-ours'
    for ours, base, theirs, s, e in hh:
        new_lines.extend(lines[cursor:s])
        if union_fallback:
            new_lines.extend(ours)
            new_lines.extend(theirs)
        else:
            new_lines.extend(ours)
        cursor = e + 1
    new_lines.extend(lines[cursor:])
    final = '\n'.join(new_lines)
    # needle gate (bookkeeping faces): take-ours first, union retry if lost
    for nd in NEEDLES.get(rel, []):
        if nd not in final and not union_fallback:
            print('NEEDLE %r absent in take-ours for %s -> union retry' % (nd, rel))
            return resolve(rel, True)
    resid = [l for l in new_lines
             if re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', l.rstrip('\r'))]
    assert not resid, (rel, 'residual markers: %r' % resid[:2])
    if rel.endswith('.json'):
        json.loads(final)
    final.encode('utf-8')
    open(path, 'wb').write(final.encode('utf-8'))
    return len(hh), strategy


for rel in FILES:
    n, strat = resolve(rel, False)
    print('RESOLVED %s: hunks=%d strategy=%s' % (rel, n, strat))

# final needle sweep on both bookkeeping faces
for rel, needs in NEEDLES.items():
    path = REPO + '\\' + rel.replace('/', '\\')
    final = open(path, 'rb').read().decode('utf-8')
    for nd in needs:
        assert nd in final, (rel, 'needle %r lost after resolution' % nd)
print('ALL 16 FILES RESOLVED: take-ours (origin authoritative), needles 3/3 held, json valid')
