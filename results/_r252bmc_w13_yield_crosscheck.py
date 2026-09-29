# -*- coding: utf-8 -*-
"""r252 bm-c W13 yield cross-validation: bm-a r456 probe facts vs bm-c r251/r252 probe facts
shared-anchor face comparison (receipt evidence, read-only)."""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import json

a = json.load(open('results/_r456bma_sumnsump_w13_probe_facts.json', encoding='utf-8'))
b = json.load(open('results/_r251bmc_sumn_w13_probe_facts.json', encoding='utf-8'))
print('bm-a facts top keys:', len(a), '| bm-c facts top keys:', len(b))


def g(d, *names):
    for n in names:
        if n in d:
            return d[n]
    return None


checks = [
    ('rows', g(a, 'rows'), g(b, 'rows')),
    ('sumn10_decidable', g(a, 'sumn10_decidable_days'), g(b, 'sumn10_decidable_days')),
    ('sumn10_open', g(a, 'sumn10_open_days'), g(b, 'sumn10_open_days')),
    ('sumn10_rate', g(a, 'sumn10_open_rate_on_decidable'), g(b, 'sumn10_open_rate_on_decidable')),
    ('sumn20_decidable', g(a, 'sumn20_decidable_days'), g(b, 'sumn20_decidable_days')),
    ('sumn20_open', g(a, 'sumn20_open_days'), g(b, 'sumn20_open_days')),
    ('sumn20_rate', g(a, 'sumn20_open_rate_on_decidable'), g(b, 'sumn20_open_rate_on_decidable')),
    ('first_decidable_120', g(a, 'first_decidable_bar_idx', 'sumn_first_decidable_bar_idx'), g(b, 'sumn10_first_decidable_bar_idx', 'first_decidable_bar_idx')),
    ('512_nonzero', g(a, 'nine_gate_512_cells_nonzero_count', 'cells_512_nonzero'), g(b, 'nine_gate_512_cells_nonzero_count')),
    ('512_empty', g(a, 'nine_gate_512_cells_empty_count', 'cells_512_empty'), g(b, 'nine_gate_512_cells_empty_count')),
    ('cutoff', g(a, 'cutoff'), g(b, 'cutoff')),
]
n_match = n_diff = n_miss = 0
for name, va, vb in checks:
    if va is None or vb is None:
        print('%-26s bm-a=%s bm-c=%s MISSING-FACE' % (name, va, vb))
        n_miss += 1
        continue
    tag = 'MATCH' if va == vb else 'DIFF'
    if tag == 'MATCH':
        n_match += 1
    else:
        n_diff += 1
    print('%-26s bm-a=%s bm-c=%s %s' % (name, va, vb, tag))
print('shared numeric anchors: %d match / %d diff / %d missing' % (n_match, n_diff, n_miss))

for d, tag in ((a, 'bm-a'), (b, 'bm-c')):
    adj = d.get('adjacency', {})
    for k in sorted(adj):
        if 'sumn' in k and ('sumn10' in k or 'sumn20_vs' in k):
            v = adj[k]
            print(tag, k, '->', {kk: v[kk] for kk in ('a_open', 'b_open', 'both_open', 'a_only_days') if kk in v})

# forward faces
for d, tag in ((a, 'bm-a'), (b, 'bm-c')):
    for k in ('forward_20d', 'forward_5d'):
        if k in d:
            v = d[k]
            print(tag, k, '-> open', v.get('mean_fwd_open'), 'closed', v.get('mean_fwd_closed'), 'n_open', v.get('n_open'))
# key structural faces bm-a primary=sumn20 vs bm-c primary=sumn10 (window difference, disclosed)
print('---primary-window disclosure---')
print('bm-a axis order:', 'SUMN in {none, sumn20_lo, sumn10_lo} (sumn20 primary)')
print('bm-c probe primary face: sumn10 (complementary window)')
