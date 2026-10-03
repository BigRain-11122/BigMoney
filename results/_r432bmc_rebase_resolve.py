# -*- coding: utf-8 -*-
# r432 bm-c pull--rebase pick-1 conflict resolver (CODELY.md + research/pit-ps.md).
# Origin side (ours) = post-integration state: my r431 sweep surgery already absorbed
# upstream (bm-a push-storm integration), bm-b r635 receipts appended on top. My pick
# side (theirs) deltas in both hunks = EMPTY (deletion intent already realized in
# origin). Per r423 union law + r630 pick-verify-absorbed law: keep ours block, drop
# base, mine empty -> take-ours == union here. Byte-exact, marker-line anchored.
import re

def resolve(path, ours_needles, base_needles, uniq_needles):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    lines = text.split('\n')
    starts = [i for i, l in enumerate(lines) if l.startswith('<<<<<<< ')]
    mids = [i for i, l in enumerate(lines) if l.startswith('||||||| ')]
    seps = [i for i, l in enumerate(lines) if l.rstrip('\r') == '=======']
    ends = [i for i, l in enumerate(lines) if l.startswith('>>>>>>> ')]
    assert len(starts) == 1 and len(mids) == 1 and len(seps) == 1 and len(ends) == 1, \
        (path, len(starts), len(mids), len(seps), len(ends))
    s, m, p, e = starts[0], mids[0], seps[0], ends[0]
    ours = lines[s + 1:m]
    base = lines[m + 1:p]
    mine = lines[p + 1:e]
    assert not mine, (path, 'mine side not empty: %r' % mine[:1])
    for nd in ours_needles:
        assert any(nd in l for l in ours), (path, 'ours missing needle %r' % nd)
    for nd in base_needles:
        assert any(nd in l for l in base), (path, 'base missing needle %r' % nd)
    new_lines = lines[:s] + ours + lines[e + 1:]
    resid = [l for l in new_lines
             if re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', l.rstrip('\r'))]
    assert not resid, (path, 'residual markers: %r' % resid[:2])
    new_text = '\n'.join(new_lines)
    for nd, cnt in uniq_needles:
        assert new_text.count(nd) == cnt, (path, 'needle %r count=%d != %d' % (nd, new_text.count(nd), cnt))
    new_text.encode('utf-8')
    open(path, 'wb').write(new_text.encode('utf-8'))
    print('RESOLVED %s: kept ours=%d lines, dropped base=%d, mine=0' % (path, len(ours), len(base)))

resolve(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md',
        ours_needles=['r635 bm-b'],
        base_needles=['r426 bm-c'],
        uniq_needles=[('O-20261003-2030 CEO 宝藏保护令执行回执', 1)])
resolve(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-ps.md',
        ours_needles=['r635 bm-b'],
        base_needles=[],
        uniq_needles=[('包装器多行输出=单一 PS 字符串项坑', 1)])
print('BOTH FILES RESOLVED: take-ours (r635 receipts kept, sweep deltas already in origin)')
