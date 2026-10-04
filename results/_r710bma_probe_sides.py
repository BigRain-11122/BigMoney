# r710 bm-a rebase-mode side probe (r709 bloodline, REBASE stage: 2=origin tip side, 3=local replay side, r351 law)
# Deep-ts probe both stages for the 11 non-ALL_FACES UU faces; twins must land same side (r708 twin law);
# ts compare normalized to 'T'-joined form (r709 format-asymmetry false-tie law).
import json, subprocess, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stage(stage_n, path):
    b = subprocess.run(['git', 'show', ':%d:%s' % (stage_n, path)], capture_output=True, cwd=ROOT).stdout
    return b

def norm_ts(v):
    if not isinstance(v, str):
        return ''
    v = v.strip()
    if re.match(r'^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}', v):
        return v.replace(' ', 'T')
    return ''

def deep_ts(obj, best=''):
    # wall-clock values only (R350 law: time-of-day required, date-only never feeds max)
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = k.replace('_', '').replace('-', '').lower()
            if (nk.startswith('generated') or nk.startswith('updated') or nk.startswith('asof')
                    or nk.startswith('asof') or nk.startswith('state')) and norm_ts(v):
                t = norm_ts(v)
                if t > best:
                    best = t
            r = deep_ts(v, best)
            if r > best:
                best = r
    elif isinstance(obj, list):
        for x in obj:
            r = deep_ts(x, best)
            if r > best:
                best = r
    return best

FACES = [
    'docs/daily_report/REPORT-2026-10-05.json',
    'docs/daily_report/REPORT-2026-10-05.md',
    'docs/live_usage/LIVE-2026-10-05.json',
    'docs/live_usage/LIVE-2026-10-05.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]

report = {}
for p in FACES:
    o2, o3 = stage(2, p), stage(3, p)
    # json faces: parse probe; md/js faces: regex scan for generated/updated stamps
    def probe(b):
        try:
            d = json.loads(b.decode('utf-8'))
            return deep_ts(d)
        except Exception:
            hits = [norm_ts(m.group(1)) for m in re.finditer(
                rb"(?:generated_at|updated|as_of)[\"':= ]+([0-9T:\- ]{10,25})", b)]
            hits = [h for h in hits if h]
            return max(hits) if hits else ''
    t2, t3 = probe(o2), probe(o3)
    report[p] = {'origin_s2': t2, 'local_s3': t3, 'b2': len(o2), 'b3': len(o3)}
    print('%-52s s2(origin)=%s  s3(local)=%s  bytes %d/%d' % (p, t2 or '-', t3 or '-', len(o2), len(o3)))

open(os.path.join(ROOT, 'results', '_r710bma_probe_sides.json'), 'w', encoding='utf-8', newline='\n').write(
    json.dumps(report, ensure_ascii=False, indent=1) + '\n')
print('WROTE results/_r710bma_probe_sides.json')
