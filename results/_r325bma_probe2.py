# -*- coding: utf-8 -*-
"""r325 bm-a rebase probe #2: 25-UU vs bm-c r82. Deep ts probe both stages."""
import json
import re
import subprocess
import io

FILES = [
    'docs/daily_report/REPORT-2026-09-27.json',
    'docs/daily_report/REPORT-2026-09-27.md',
    'results/autofill_state.json',
    'results/compute_audit.json',
    'results/daily_scorecard.json',
    'results/dashboard_status.js',
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json',
    'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json',
    'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json',
    'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json',
    'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json',
    'results/prospect_promotion/_summary.json',
    'results/regime_state.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/x2_watch_log.jsonl',
]

TS_KEYS = re.compile(r'(^|_|\.)(ts|generated|generated_at|updated|updated_at|time|'
                     r'asof|last_seen|cutoff|day|date)(_|$|\b)', re.I)


def stage(path, n):
    return subprocess.run(['git', 'show', ':%d:%s' % (n, path)], capture_output=True).stdout


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
        for i, v in enumerate(obj[:2]):
            out.extend(deep_ts(v, path + '[%d]' % i))
    return out


buf = []
for f in FILES:
    b2, b3 = stage(f, 2), stage(f, 3)
    buf.append('=== %s (S2=%dB S3=%dB)' % (f, len(b2), len(b3)))
    for tag, b in (('S2', b2), ('S3', b3)):
        if not b:
            buf.append('  %s EMPTY' % tag)
            continue
        if f.endswith('.jsonl'):
            lines = [ln for ln in b.decode('utf-8', 'replace').splitlines() if ln.strip()]
            buf.append('  %s jsonl lines=%d first=%s last=%s' % (
                tag, len(lines),
                lines[0][:60] if lines else '-',
                lines[-1][:60] if lines else '-'))
            continue
        if f.endswith('.md'):
            hits = re.findall(rb'(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)', b)
            buf.append('  %s md-ts: %s' % (tag, [h.decode() for h in hits[:3]]))
            continue
        txt = b
        if f.endswith('.js'):
            m = re.search(rb'window\.DASH_DATA\s*=\s*(\{.*\})\s*;', b, re.S)
            txt = m.group(1) if m else None
        if txt is None:
            buf.append('  %s no payload' % tag)
            continue
        try:
            d = json.loads(txt)
        except Exception as e:
            buf.append('  %s ERR %s' % (tag, e))
            continue
        buf.append('  %s %s' % (tag, [(p, v) for p, v in deep_ts(d)[:6]]))
    buf.append('')

io.open('results/_r325bma_probe2.txt', 'w', encoding='utf-8').write('\n'.join(buf))
print('\n'.join(buf))
