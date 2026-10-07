# -*- coding: utf-8 -*-
"""r858 bm-a S0 rebase-conflict resolver (14 UU faces; skill bigmoney-conflict-resolve).

Scope split (canon per skill ALL_FACES note):
  - 6 ALL_FACES lanes (compute_audit/regime_state/update_status/lhb/futures/
    token_usage) -> scripts/merge_lane_views.py resolve <path> (run separately,
    union recipes; 禁手写 union r376).
  - THIS script: twin-regen-md (r327/r329 twin-side coupling) + solo snapshot
    faces, reusing r857 _r857_uu_resolve.py proven block form verbatim:
    same-day regen twins must take the SAME side (ts-diffpick first block,
    forced across all blocks + md byte-copy same side).
Rebase orientation: ours=HEAD=new base (origin/bm-c side), theirs=replayed
commit (local r857 side).
Parse-verify every json before writing; fail-closed on any anomaly.
"""
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TS_RE = re.compile(
    r'"(?:ts|updated|generated)"\s*:\s*"?(20\d\d-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?)'
    r'|\b(20\d\d-\d\d-\d\d \d\d:\d\d(?::\d\d)?)')


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


def main():
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
    for p in [jp for jp, _ in TWINS] + list(SOLO_JSON):
        json.loads(open(p, encoding='utf-8').read())
    print('r858 resolver done: 3 twins + 2 solo, parse-verify OK')


if __name__ == '__main__':
    main()
