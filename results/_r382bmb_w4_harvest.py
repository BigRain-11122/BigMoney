"""r382 bm-b: W4-GENERATE harvest flip (r244 landed-marker law) + byte-style law (r381 kenglu)."""
import json, subprocess, sys

POOL = 'results/runnable_pool.json'
raw = open(POOL, 'rb').read()
crlf = raw.count(b'\r\n'); lf = raw.count(b'\n'); trailing = raw[-1:]
print('probe: crlf=%d lf=%d trailing=%r' % (crlf, lf, trailing))
assert b'\r\n' in raw and trailing != b'\n', 'unexpected byte style'

d = json.loads(raw.decode('utf-8'))
e = next(x for x in d['entries'] if x['id'] == 'TRIAL-LABOR-W4-GENERATE')
sh = e['shards'][0]
assert e['status'] == 'ready' and sh['status'] == 'ready' and sh['owner'] == 'bm-b'

now = '2026-09-28 12:27:41'
e['status'] = 'done'
e['done_at'] = now
e['result_ref'] = 'results/trial_labor_w4/w4_candidates.json'
e['done_note'] = ('r382 bm-b harvest (r244 landed-marker law): relaunch 12:13:47 on fixed runner sha '
                  '(r381 raw-face law) clean burn 831.3s -> landed 12:27:41; raw 5000 (A500/B4500) -> '
                  'exclusion hits 0 -> dedup distinct 3810 (fp-collapses 3844 + corr-collapses 35), '
                  'zero engine cells burned, single-shot marker intact; G-VOL frozen anchors '
                  '{first_valid 519, calm 1523, wild 1441, n_bars 3483} reproduced live on the raw '
                  'full-history face = r381 face-fix production-validated; seven-source exclusion '
                  'consumed (w1 149 + w2 404 + w3 513 + MASS 166 [translated-exact 2, 164 '
                  'non-translatable disclosed] + grammar_stop_gate_vol_none 42); judged products 4 '
                  'sources declared-unavailable zero rows honest; vol faces {calm 1226, none 1311, '
                  'wild 1273}; grammar sha16 d498e9343ee57460 anchored; TRIAL_GRAMMAR_LEDGER wave-4 '
                  'row runner-written at consume 12:27:41; next slice = W4 screen-prep + '
                  'TRIAL-LABOR-W4-SCREEN pool entry (CPU pool face lawful per prereg sec.0 r369 '
                  'disposition)')
sh['status'] = 'done'
sh['done_at'] = now
sh['note'] = ('DONE r382 bm-b harvest (r244 landed-marker law): tick 12:13:42 relaunch on changed '
              'runner sha (r379 fuse auto-clear law, S16c cleared 12:13:37) -> landed 12:27:41; '
              'products w4_candidates.json n=3810 distinct grammar d498e9343ee57460 '
              'evidence_cutoff 2026-09-22; G-VOL refusal 11:46 root-cause face law (r381 61f81785) '
              'production-validated through exact real-data anchors')

out = json.dumps(d, ensure_ascii=False, indent=2)
out = out.replace('\n', '\r\n')
if trailing != b'\n':
    out = out.rstrip('\r\n')
open(POOL, 'wb').write(out.encode('utf-8'))

v = open(POOL, 'rb').read()
assert v.count(b'\r\n') >= crlf, 'crlf lost'
d2 = json.loads(v.decode('utf-8'))
e2 = next(x for x in d2['entries'] if x['id'] == 'TRIAL-LABOR-W4-GENERATE')
assert e2['status'] == 'done' and e2['shards'][0]['status'] == 'done'
print('harvest flip OK; byte-style preserved')
r = subprocess.run(['git', 'diff', '--stat', '--', POOL], capture_output=True, text=True)
print(r.stdout.strip())
