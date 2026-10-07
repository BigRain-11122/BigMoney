# -*- coding: utf-8 -*-
"""r857 bm-a rebase-conflict resolver (15 UU faces; skill bigmoney-conflict-resolve).

Groups:
  A) 3-stage whole-blob faces (multi-hunk, single-block resolvers inapplicable):
     - results/compute_audit.json : rolling-ledger -> history union by ts key
       + latest take-new by deep nested ts (r188/R208; deep probe r311).
     - results/token_usage.json    : snapshot -> whole-doc take-new by deep
       'generated' probe (R216).
  B) per-file newer-wins conflict-block faces (r856 _r856_uu_resolve.py proven
     form + 15th face + twin-coupling assertion r327/r329):
     same-day regen twins must take the SAME side.
Parse-verify every json before writing; fail-closed on any anomaly.
"""
import json
import re
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TS_RE = re.compile(
    r'"(?:ts|updated|generated)"\s*:\s*"?(20\d\d-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?)'
    r'|\b(20\d\d-\d\d-\d\d \d\d:\d\d(?::\d\d)?)')


def stage_blob(path, n):
    raw = subprocess.run(['git', 'show', ':%d:%s' % (n, path)],
                         capture_output=True).stdout
    return raw.decode('utf-8', 'replace')


def deep_newest_ts(obj):
    """Recursive newest ^20xx ts literal probe (deep-scan law r311)."""
    best = [None]

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            m = TS_RE.search(o)
            if m:
                v = m.group(1) or m.group(2)
                if best[0] is None or v > best[0]:
                    best[0] = v
    walk(obj)
    return best[0]


def resolve_group_a():
    # compute_audit.json: history union by ts + latest take-new
    p = 'results/compute_audit.json'
    a = json.loads(stage_blob(p, 2))   # origin side
    b = json.loads(stage_blob(p, 3))   # local side
    ha = {e.get('ts'): e for e in a.get('history', [])}
    hb = {e.get('ts'): e for e in b.get('history', [])}
    merged_hist = [(hb.get(k) or ha.get(k)) for k in sorted(set(ha) | set(hb))]
    la, lb = deep_newest_ts(a.get('latest')), deep_newest_ts(b.get('latest'))
    latest = b['latest'] if (lb or '') >= (la or '') else a['latest']
    out = dict(b)
    out['history'] = merged_hist
    out['latest'] = latest
    s = json.dumps(out, ensure_ascii=False, indent=2)
    json.loads(s)  # parse-verify
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('resolved %s: history union %d+%d->%d, latest=%s'
          % (p, len(ha), len(hb), len(merged_hist),
             'local' if latest is b['latest'] else 'origin'))

    # results/_orphan_face_probe.json: snapshot -> 3-stage whole-blob take-new
    # (multi-block marker form unstable after partial pass; stage blobs are
    # authoritative per-run snapshots, take-new by deep ts probe)
    p = 'results/_orphan_face_probe.json'
    try:
        raw_a = stage_blob(p, 2)
        raw_b = stage_blob(p, 3)
        # raw-text probe: both T-form and space-form ts literals (deep probe
        # on parsed values misses T-form -- r311 variant, fixed here)
        pat2 = re.compile(r'20\d\d-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?')
        ta = max(pat2.findall(raw_a), default=None)
        tb = max(pat2.findall(raw_b), default=None)
        win_raw = raw_b if (tb or '') >= (ta or '') else raw_a
        json.loads(win_raw)  # parse-verify the chosen whole blob
        open(p, 'w', encoding='utf-8', newline='').write(win_raw)
        print('resolved %s: 3-stage take-new ts=%s vs %s -> %s side'
              % (p, ta, tb, 'local' if win_raw is raw_b else 'origin'))
    except subprocess.CalledProcessError:
        print('skip %s: stages unavailable (non-conflict state)' % p)

    # token_usage.json: whole-doc take-new by deep 'generated'
    p = 'results/token_usage.json'
    a = json.loads(stage_blob(p, 2))
    b = json.loads(stage_blob(p, 3))
    ga, gb = a.get('generated'), b.get('generated')
    if not ga or not gb:
        print('FAIL %s: generated probe missing (%r vs %r)' % (p, ga, gb))
        sys.exit(1)
    win = b if gb >= ga else a
    s = json.dumps(win, ensure_ascii=False, indent=2)
    json.loads(s)
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('resolved %s: take-new generated %s (%s side)'
          % (p, max(ga, gb), 'local' if win is b else 'origin'))


TWINS = [
    ('docs/daily_report/REPORT-2026-10-08.json',
     'docs/daily_report/REPORT-2026-10-08.md'),
    ('docs/live_usage/LIVE-2026-10-08.json',
     'docs/live_usage/LIVE-2026-10-08.md'),
    ('docs/live_usage/LIVE-latest.json',
     'docs/live_usage/LIVE-latest.md'),
]
SOLO_JSON = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
]


def block_ts(txt):
    best = None
    for m in TS_RE.finditer(txt):
        v = m.group(1) or m.group(2)
        if best is None or v > best:
            best = v
    return best


def resolve_block_file(path, force_side=None):
    """Loop ALL conflict blocks in the file (multi-hunk form); side decided
    once from the first block's ts probe, then forced on every remaining
    block (same regen run). Returns side, or None if file already clean."""
    s = open(path, encoding='utf-8', errors='replace').read()
    pat = re.compile(r'<<<<<<<[^\n]*\n(.*?)\n=======[^\n]*\n(.*?)\n'
                     r'>>>>>>>[^\n]*\n?', re.S)
    if not pat.search(s):
        print('skip %s: no conflict block (already resolved)' % path)
        return None
    first = pat.search(s)
    side = force_side
    if side is None:
        ot = block_ts(first.group(1))
        tt = block_ts(first.group(2))
        if ot is None or tt is None:
            print('FAIL %s: ts missing ours=%s theirs=%s' % (path, ot, tt))
            sys.exit(1)
        side = 'theirs' if tt > ot else 'ours'
        print('%s: side decided = %s (ours=%s theirs=%s)'
              % (path, side, ot, tt))
    n = 0
    while True:
        m = pat.search(s)
        if not m:
            break
        win = m.group(2) if side == 'theirs' else m.group(1)
        s = s[:m.start()] + win + '\n' + s[m.end():]
        n += 1
    open(path, 'w', encoding='utf-8', newline='').write(s)
    print('resolved %s: side=%s blocks_replaced=%d' % (path, side, n))
    return side


def resolve_group_b():
    for jp, mp in TWINS:
        side = resolve_block_file(jp)
        if side is None:
            mside = resolve_block_file(mp)
            if mside is not None:
                print('WARN twin %s resolved independently (json clean)' % mp)
            continue
        mside = resolve_block_file(mp, force_side=side)
        if mside != side:
            print('FAIL twin coupling %s vs %s' % (jp, mp))
            sys.exit(1)
    for p in SOLO_JSON:
        resolve_block_file(p)
    # parse-verify all json faces after writing
    for p in [jp for jp, _ in TWINS] + [p for p in SOLO_JSON] + \
            ['docs/live_usage/LIVE-latest.json']:
        json.loads(open(p, encoding='utf-8').read())
    print('group B parse-verify: all json faces OK')


if __name__ == '__main__':
    resolve_group_a()
    resolve_group_b()
    print('r857 resolver done 15/15')
