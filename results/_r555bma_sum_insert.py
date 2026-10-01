"""r555 helper: insert W47 leg description into the static PASS summary (valid literals)."""
PATH = 'scripts/perpetual_faces_n1.py'
data = open(PATH, 'rb').read().decode('utf-8')
nl = '\r\n' if data.count('\r\n') > 0 else '\n'

anchor = 'r348 bm-c] "' + nl + '          "+ T-141 s2 "'
i = data.find(anchor)
assert i > 0, 'summary tail anchor not found: %r' % anchor[:80]
print('anchor at', i)

W47 = (
    'r348 bm-c] "' + nl +
    '          "+ W47 materializer face "' + nl +
    '          "[same guard set, dep=W17..W46 ALL present (the chain FULLY '
    'caught up W1..W46 at this freeze -- net ledger head 465,748, zero '
    'in-flight upstream face, static dep asserts legal for the full set), '
    'A=arithmetic continuation clean per law sec.4 W47 row 137_004..139_003 '
    '(W46 row W47+ WARNING projection verified machine-side, zero skip), '
    'B=FORCED SKIP-OVER past SEED_REGISTRY[\'pc_l2_ic\']=45_000 (arithmetic '
    'tail 44_801..45_000 machine-REFUSED, r307 scan-forward first clean '
    'window 45_001..45_200, W39-B/W43-B family, ADMIT receipt '
    'results/_r555bma_w47_band_gate.py), THIRTY-SEVENTH ENGINE-OWNED WAVE '
    'engine_owner=bm-a per engine de-throttle law O-20261001-2355 sec.2 '
    'own-continuous-series (zero-gap relay after the W46 full closeout '
    'bm-c r348, wave 47 = first free number after W46\'s claim; bm-a tick '
    'architecture per r535 law -- no resident instance, ignition proof = '
    'product growth within 2 ticks per r325 law), r555 bm-a] "' + nl +
    '          "+ T-141 s2 "'
)
new = data[:i] + W47 + data[i + len(anchor):]
open(PATH, 'wb').write(new.encode('utf-8'))
print('W47 summary description inserted')
