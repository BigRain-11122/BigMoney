# -*- coding: utf-8 -*-
"""r432 bm-c rebase pick-4 (S6 output absorb) resolver, 14 racing faces.
13 regenerated faces: take-THEIRS (own 22:11-22:15 S6 chain outputs -- newer
than bm-a r644's 22:10:44 chain end, newer-wins for same-day-idempotent faces;
the pick's semantic content = own chain products).
token_usage.json: per-hunk -- refusals hunk takes OURS (shared monotonic
counter, max-preserve 1225); all other hunks take THEIRS (own newer snapshot).
Marker-anchored, byte-exact, json-validated, key asserts."""
import json
import re

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
TAKE_THEIRS = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
TOKEN_USAGE = "results/token_usage.json"
MARK_START = re.compile(r'^<<<<<<< ')
MARK_MID = re.compile(r'^\|\|\|\|\|\|\| ')
MARK_SEP = re.compile(r'^=======$')
MARK_END = re.compile(r'^>>>>>>> ')


def hunks_of(lines):
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
            assert None not in (m, p, e), 'malformed hunk at %d' % (s + 1)
            out.append((lines[s + 1:m], lines[m + 1:p], lines[p + 1:e], s, e))
            i = e + 1
        else:
            i += 1
    return out


def resolve(rel, chooser):
    path = REPO + '\\' + rel.replace('/', '\\')
    text = open(path, 'rb').read().decode('utf-8')
    lines = text.split('\n')
    hh = hunks_of(lines)
    assert hh, 'no hunks in %s' % rel
    new_lines, cursor, notes = [], 0, []
    for ours, base, theirs, s, e in hh:
        keep = chooser(ours, base, theirs)
        notes.append('ours=%d base=%d theirs=%d -> %s' % (len(ours), len(base), len(theirs), keep))
        new_lines.extend(lines[cursor:s])
        new_lines.extend(ours if keep == 'ours' else theirs)
        cursor = e + 1
    new_lines.extend(lines[cursor:])
    final = '\n'.join(new_lines)
    resid = [l for l in new_lines
             if re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', l.rstrip('\r'))]
    assert not resid, (rel, resid[:2])
    if rel.endswith('.json'):
        json.loads(final)
    final.encode('utf-8')
    open(path, 'wb').write(final.encode('utf-8'))
    print('RESOLVED %s: %d hunk(s) [%s]' % (rel, len(hh), '; '.join(notes)))


for rel in TAKE_THEIRS:
    resolve(rel, lambda o, b, t: 'theirs')
resolve(TOKEN_USAGE, lambda o, b, t: 'ours' if any('"refusals"' in l for l in o) else 'theirs')

# token_usage final key asserts
final = json.loads(open(REPO + '\\results\\token_usage.json', 'rb').read().decode('utf-8'))
assert final['generated'] == '2026-10-03 22:15:54', final['generated']
assert final['per_round_context']['mandate_read_tokens_est'] == 12360
assert final['l2_local_llm']['crash_fuse']['refusals'] == 1225
assert final['delta_vs_prev']['mandate_growth'] == 203
print('TOKEN_USAGE asserts OK: generated=22:15:54 (own newer snapshot) + refusals=1225 (shared monotonic preserved)')
print('PICK-4 RESOLVED: 13 take-theirs + 1 per-hunk, 14/14 done')
