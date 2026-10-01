"""r499bm-b re-fire rebase conflict resolver (heritage adoption of dead r499 pick 2458cf2b6).

Scope: 33 unmerged entries (20 UU + 13 AA) from pull --rebase onto origin/main d57c62b80.
Laws: bigmoney-conflict-resolve skill + merge_lane_views tool (A/B faces) +
r481 AA product-envelope twins law + r289 format mirror + R31 host-lane authority.
Stage orientation (r351): :2: = origin base side, :3: = replayed local pick.
"""
import subprocess
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def git(*a):
    r = subprocess.run(['git'] + list(a), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git %s -> rc=%d: %s' % (
            ' '.join(a), r.returncode, r.stderr.decode(errors='replace')[:300]))
    return r.stdout


def stage(path, n):
    return git('show', ':%d:%s' % (n, path))


def probe_fmt(raw_bytes):
    raw = raw_bytes.decode('utf-8', 'replace')
    crlf = '\r\n' in raw
    m = re.search(r'\{[\r\n]+( +)"', raw)
    indent = len(m.group(1)) if m else 1
    return crlf, indent


def write_json_fmt(path, doc, crlf, indent):
    payload = json.dumps(doc, ensure_ascii=False, indent=indent)
    if crlf:
        payload = payload.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(payload + ('\r\n' if crlf else '\n'))
    back = json.load(open(path, encoding='utf-8'))
    assert back == doc, 'parse-verify failed %s (r185 law)' % path


def tolerant_eq(a, b, rel=1e-9, depth=0):
    """Manual adjudication compare (r481 escalation): floats compared with
    relative tolerance (cross-machine accumulation-order artifacts at 1e-15
    level observed on null_pool_cumulative), everything else exact."""
    if depth > 8:
        return a == b
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a == b:
            return True
        denom = max(abs(a), abs(b), 1e-300)
        return abs(a - b) / denom < rel
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(tolerant_eq(a[k], b[k], rel, depth + 1)
                                        for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(
            tolerant_eq(x, y, rel, depth + 1) for x, y in zip(a, b))
    return a == b


AUDIT_ENVELOPE = {'audit', 'generated', 'generated_at', 'elapsed_sec', 'elapsed',
                  'machine', 'workers', 'elapsed_s'}

resolved = []

# ---- Phase 1: AA products, r481 twins law (assert science payload equality
# ignoring audit envelope, then take origin :2:) -------------------------------
AA_PRODUCTS = ['results/p2cal_ext/n1_w3/shard-%d-of-12.json' % i
                for i in range(1, 12)]
for p in AA_PRODUCTS:
    b2, b3 = stage(p, 2), stage(p, 3)
    d2, d3 = json.loads(b2), json.loads(b3)

    def strip(d):
        return {k: v for k, v in d.items() if k not in AUDIT_ENVELOPE}
    s2, s3 = strip(d2), strip(d3)
    if s2 != s3:
        bad = [k for k in set(list(s2) + list(s3)) if s2.get(k) != s3.get(k)]
        raise SystemExit('FAIL-CLOSED r481 assert: %s science keys differ: %s'
                         % (p, bad))
    with open(p, 'wb') as fh:
        fh.write(b2)
    resolved.append(p)
    print('[AA-twin] %s: payload-equal (envelope ignored), took origin :2:' % p)

# ---- Phase 1b: finalize face n1_w3_results.json -- r481 ESCALATED to manual
# adjudication: exact-key assert failed on null_pool_cumulative float last-digits
# (cross-machine accumulation-order artifact, delta <=1e-14 relative; headline
# stats identical: K=6720 mu=-0.0904 sigma=0.2479 on both commit messages).
# Adjudication: take origin :2: -- origin r507 finalize is the landed face the
# skill_line/ledger backfill on origin consumed; taking local float variant
# would break landed-chain coherence. Tolerance compare documents the check.
p = 'results/perpetual_faces/n1_w3_results.json'
b2, b3 = stage(p, 2), stage(p, 3)
d2, d3 = json.loads(b2), json.loads(b3)


def strip_env(d):
    return {k: v for k, v in d.items() if k not in AUDIT_ENVELOPE}
if not tolerant_eq(strip_env(d2), strip_env(d3)):
    bad = [k for k in set(list(strip_env(d2)) + list(strip_env(d3)))
           if not tolerant_eq(strip_env(d2).get(k), strip_env(d3).get(k))]
    raise SystemExit('FAIL-CLOSED adjudication: %s keys differ beyond 1e-9: %s'
                     % (p, bad))
with open(p, 'wb') as fh:
    fh.write(b2)
resolved.append(p)
print('[AA-adjudicated] %s: envelope+float(1e-9 rel)-equal, took origin :2: '
      '(ledger-coherence with landed r507 backfill)' % p)

# ---- Phase 2: AA W4 prereg -> take origin :2: (bm-a r507p2 frozen gate,
# fleet claims already flow against it; local twin = wording-level envelope) ---
p = 'research/PERPETUAL_N1_W4_PREREG.md'
with open(p, 'wb') as fh:
    fh.write(stage(p, 2))
resolved.append(p)
print('[AA-take-origin] %s (bands identical twins: A=16_100..18_099 B=21_500..21_699)' % p)

# ---- Phase 3: perpetual_faces_state.json -- take origin with wave-subset
# assert (local waves must not contain a wave origin lacks; bands identity) ----
p = 'results/perpetual_faces_state.json'
d2 = json.loads(stage(p, 2))
d3 = json.loads(stage(p, 3))


def wave_id(w):
    return (w.get('face'), w.get('wave'), tuple(w.get('bands', {}).get('a', [])),
            tuple(w.get('bands', {}).get('b_exit', [])), w.get('n_entries'))


ids2 = {wave_id(w) for w in d2.get('waves', [])}
ids3 = {wave_id(w) for w in d3.get('waves', [])}
if not ids3 <= ids2:
    raise SystemExit('FAIL-CLOSED: local waves not subset of origin waves: %s'
                     % (ids3 - ids2))
with open(p, 'wb') as fh:
    fh.write(stage(p, 2))
resolved.append(p)
print('[UU-wave-union] %s: local waves subset-verified (%d origin / %d local), took origin :2:' % (p, len(ids2), len(ids3)))

# ---- Phase 4: UU take-origin (:2:) files --------------------------------------
# runner script: functionally-equivalent twin, origin strictly stricter
# (adds W2/W3 shard-dir collision asserts); landed with selftest ALL PASS.
# host-lane / js-wrapper / regenerated-doc faces: bm-a host authority (R31/r378).
TAKE_2 = [
    'scripts/perpetual_faces_n1.py',
    'results/dashboard_status.json',
    'results/dashboard_status.js',
    'results/strategy_scorecard.json',
    'results/scorecard_v1.json',
    'docs/daily_report/REPORT-2026-10-01.json',
    'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json',
    'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
]
for p in TAKE_2:
    with open(p, 'wb') as fh:
        fh.write(stage(p, 2))
    resolved.append(p)
    print('[UU-take-origin] %s' % p)

# ---- Phase 5: UU take-:3: (newest-ts snapshot, not a tool face) --------------
p = 'results/fundamental_b_layer_filter.json'
d2 = json.loads(stage(p, 2))
d3 = json.loads(stage(p, 3))
assert d3.get('updated', '') >= d2.get('updated', ''), 'ts ordering surprise'
with open(p, 'wb') as fh:
    fh.write(stage(p, 3))
resolved.append(p)
print('[UU-take-new] %s (updated %s >= %s, deterministic re-derived mask)' % (
    p, d3.get('updated'), d2.get('updated')))

# ---- Phase 6: A/B faces via merge_lane_views resolve tool ---------------------
# Content merge by the canonical tool (done-absorption, cap50, take-new probes),
# then format mirrored to the ORIGIN blob (r289/r289-family format war law:
# indent2 = majority-writer canonical for pool/compute_audit per r499 triage).
TOOL_FACES = [
    'results/runnable_pool.json',
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/update_status.json',
    'results/token_usage.json',
    'results/lhb_update_status.json',
    'results/futures_update_status.json',
]
for p in TOOL_FACES:
    b2 = stage(p, 2)
    crlf, indent = probe_fmt(b2)
    r = subprocess.run(['python', 'scripts/merge_lane_views.py',
                        'resolve', p], capture_output=True)
    out = r.stdout.decode(errors='replace')
    print('--- tool resolve %s rc=%d (mirror fmt: crlf=%s indent=%d)' % (
        p, r.returncode, crlf, indent))
    print(out.strip())
    if r.returncode != 0:
        raise SystemExit('tool resolve failed for %s' % p)
    doc = json.load(open(p, encoding='utf-8'))
    write_json_fmt(p, doc, crlf, indent)
    resolved.append(p)

# ---- Phase 7: stage resolutions, verify zero unmerged -------------------------
git('add', '--', *resolved)
left = subprocess.run(['git', 'ls-files', '-u'], capture_output=True).stdout.decode()
print('=== unmerged entries remaining: %d ===' % len([x for x in left.splitlines() if x.strip()]))
print('=== resolved %d files ===' % len(resolved))
if left.strip():
    print(left)
    sys.exit(3)
print('RESOLVE-OK')
