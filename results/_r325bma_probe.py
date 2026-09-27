# -*- coding: utf-8 -*-
"""r325 bm-a rebase probe: deep-scan ts-like fields in both stages of UU files."""
import json
import re
import subprocess
import io

FILES = [
    'results/compute_audit.json',
    'results/regime_state.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/update_status.json',
    'results/token_usage.json',
    'docs/daily_report/REPORT-2026-09-27.json',
    'docs/daily_report/REPORT-2026-09-27.md',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
]

TS_KEYS = re.compile(r'(^|_|\.)(ts|generated|generated_at|updated|updated_at|time|'
                     r'asof|last_seen|cutoff)(_|$|\b)', re.I)


def stage(path, n):
    b = subprocess.run(['git', 'show', ':%d:%s' % (n, path)], capture_output=True).stdout
    return b


def deep_ts(obj, path=''):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + '.' + str(k)
            if isinstance(v, str) and TS_KEYS.search(str(k)) and len(v) <= 40:
                out.append((p, v))
            elif isinstance(v, (int, float)) and TS_KEYS.search(str(k)):
                out.append((p, v))
            else:
                out.extend(deep_ts(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            out.extend(deep_ts(v, path + '[%d]' % i))
    return out


buf = []
for f in FILES:
    b2, b3 = stage(f, 2), stage(f, 3)
    buf.append('=== %s  (stage2=%dB stage3=%dB)' % (f, len(b2), len(b3)))
    for tag, b in (('S2-ours(bm-b)', b2), ('S3-theirs(bm-a-r325)', b3)):
        if not b:
            buf.append('  %s: EMPTY' % tag)
            continue
        txt = None
        if f.endswith('.js'):
            m = re.search(rb'window\.DASH_DATA\s*=\s*(\{.*\})\s*;', b, re.S)
            if m:
                txt = m.group(1)
        elif f.endswith('.md'):
            txt = None
            hits = re.findall(rb'(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d[^\s\)\]]*)', b)
            buf.append('  %s md-timestamps: %s' % (tag, [h.decode('utf-8', 'replace') for h in hits[:4]]))
            continue
        else:
            txt = b
        if txt is None:
            buf.append('  %s: no DASH_DATA payload' % tag)
            continue
        try:
            d = json.loads(txt)
        except Exception as e:
            buf.append('  %s: JSON ERR %s' % (tag, e))
            continue
        hits = deep_ts(d)
        buf.append('  %s: %s' % (tag, [(p, v) for p, v in hits[:6]]))
    buf.append('')

io.open('results/_r325bma_probe.txt', 'w', encoding='utf-8').write('\n'.join(buf))
print('\n'.join(buf))
