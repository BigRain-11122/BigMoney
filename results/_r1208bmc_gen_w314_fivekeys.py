# -*- coding: utf-8 -*-
"""r1208 bm-c: generate the W314 five-keys assertion from the W313 lineage
(results/_r1206bmc_w313_fivekeys.py) as a count-asserted canon-clone.

Face classes handled in order (r1168/r1171/r1184 pitfall family):
  1. K-index numerics parked behind letter-only sentinels (@PK@ / @SK@) so the
     W-sentinel cascade can never touch them,
  2. exact key literals / anchor constants replaced one by one (count-asserted),
  3. ONE single-pass wave-token cascade (W313->W314, W312->W313, w313->w314,
     w312->w313, r1206->r1208) LAST,
  4. sentinels resolved AFTER the cascade.
"""
import io
import re

SRC = 'results/_r1206bmc_w313_fivekeys.py'
DST = 'results/_r1208bmc_w314_fivekeys.py'
t = io.open(SRC, encoding='utf-8').read()

# ---- 1. park K-index numerics behind letter-only sentinels -------------------
NUM = [
    (4, '684320', '@PK@'),   # prior merged K (key-name suffixes + identity lines)
    (4, '686520', '@SK@'),   # W313 merged K (key names + identity)
]
print('== K-index park table ==')
for want, old, new in NUM:
    c = t.count(old)
    print('%3d/%3d  %s' % (c, want, old))
    assert c == want, 'numeric count %d != %d for %r' % (c, want, old)
    t = t.replace(old, new)

SPECIAL = [
    (1, 'KEY_MU_MERGED_W312 = -0.09280899886018237',
        'KEY_MU_MERGED_W312 = -0.09282770917089087'),
    (1, 'KEY_SIGMA_W312 = 0.2451674001421358',
        'KEY_SIGMA_W312 = 0.24516098633452796'),
    (1, 'KEY_A_P95_W312 = 0.3338', 'KEY_A_P95_W312 = 0.3071'),
    (1, 'KEY_LINE_W312_MERGED = 1.2007', 'KEY_LINE_W312_MERGED = 1.2008'),
    (1, '("key1_merged_mu_w312", "-0.09280900", k_mu_merged, 1e-8)',
        '("key1_merged_mu_w313", "-0.09282771", k_mu_merged, 1e-8)'),
    (1, '("key1b_w312_only_mu", "-0.08867268", k_prior_mu, 1e-8)',
        '("key1b_w313_only_mu", "-0.09864764", k_prior_mu, 1e-8)'),
    (1, '("key2_sigma_w312", "0.24516740", k_sigma, 1e-8)',
        '("key2_sigma_w313", "0.24516099", k_sigma, 1e-8)'),
    (1, '("key3_a_p95_w312", "0.3338", k_a_p95, 1e-9)',
        '("key3_a_p95_w313", "0.3071", k_a_p95, 1e-9)'),
    (1, '("key4_k_lift_w312", "+0.0001", klift, 1e-9)',
        '("key4_k_lift_w313", "+0.0000", klift, 1e-9)'),
    (1, '("key5_w312_se_mu", "0.000296", k_se_mu, 1e-9)',
        '("key5_w313_se_mu", "0.000296", k_se_mu, 1e-9)'),
    (1, 'assert "1,108,541" in t', 'assert "1,112,941" in t'),
    (1, '"wave": 313,', '"wave": 314,'),
    (1, 'Clone lineage: _r1203bmc_w312_fivekeys.py (canon).',
        'Clone lineage: @LIN@ (canon).'),
]
print('== special count table ==')
for want, old, new in SPECIAL:
    c = t.count(old)
    print('%3d/%3d  %s' % (c, want, old[:80]))
    assert c == want, 'special count %d != %d for %r' % (c, want, old)
    t = t.replace(old, new)

TOK = {'W313': 'W314', 'W312': 'W313', 'w313': 'w314', 'w312': 'w313',
       'r1206': 'r1208'}
pat = re.compile('|'.join(sorted(TOK, key=len, reverse=True)))
print('== wave-token pass ==')
print({k: t.count(k) for k in TOK})
out = pat.sub(lambda m: TOK[m.group(0)], t)

for sent, val in (('@PK@', '686520'), ('@SK@', '688720'),
                  ('@LIN@', '_r1206bmc_w313_fivekeys.py')):
    print('sentinel', sent, out.count(sent))
    assert out.count(sent) >= 1, (sent, out.count(sent))
    out = out.replace(sent, val)

CHECKS = [
    ('KEY_MU_MERGED_W313 = -0.09282770917089087', 1),
    ('KEY_SIGMA_W313 = 0.24516098633452796', 1),
    ('KEY_A_P95_W313 = 0.3071', 1),
    ('KEY_LINE_W313_MERGED = 1.2008', 1),
    ('se_mu_at_k688720', 1),
    ('line_merged_688720', 2),
    ('w314_only', 4),
    ('"w314_only"', 3),
    ('n1_w313_results.json', 4),
    ('n1_w314_results.json', 2),
    ('PERPETUAL_N1_W314_PREREG.md', 1),
    ('_r1208bmc_w314_fivekeys.json', 2),
    ('"wave": 314', 1),
    ('prev_k": 686520', 1),
    ('(686520 + 2200)', 1),
    ('"1,112,941" in t', 1),
    ('Clone lineage: _r1206bmc_w313_fivekeys.py (canon).', 1),
]
print('== post-generation count table ==')
bad = []
for lit, want in CHECKS:
    got = out.count(lit)
    flag = '' if got == want else '  <-- MISMATCH'
    print('%3d/%3d  %s%s' % (got, want, lit[:70], flag))
    if got != want:
        bad.append((lit, got, want))
BANNED = ['684320', 'w312', 'W312', '@PK@', '@SK@', '-0.08867268',
          '1.2007', '0.3338,']
for b in BANNED:
    if b in out:
        bad.append(('BANNED present: ' + b, out.count(b), 0))
if bad:
    print('GENERATOR FAIL', bad)
    raise SystemExit(1)
io.open(DST, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE', DST, len(out), 'bytes')