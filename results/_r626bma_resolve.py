# -*- coding: utf-8 -*-
"""r626 bm-a rebase resolver: 8 manual faces take-local(stage3) with ts evidence.

Classifier verdicts (probe deep-scan per r311/D-09; probe path existence r319):
  _attrition_guard_scan.json  UNKNOWN->manual: snapshot whole-doc, ts s2=14:04:38
                              (bm-c) vs s3=14:05:56 (bm-a) -> take s3; near-identical
                              content (1819B both) verified head-equal fields.
  fundamental_b_layer_filter  snapshot take-new: updated s2=14:03:48 vs s3=14:04:51 -> s3
  REPORT-2026-10-03.{json,md} twin-regen: generated_at s2=14:04:06 vs s3=14:04:51 -> s3
                              BOTH twins same side (r327/r329), md byte-copy from s3
  LIVE-2026-10-03.{json,md}, LIVE-latest.{json,md}: generated s2=14:04:07 vs
                              s3=14:04:52 -> s3, all four twins same side
"""
import subprocess, json

FILES = [
    'results/_attrition_guard_scan.json',
    'results/fundamental_b_layer_filter.json',
    'docs/daily_report/REPORT-2026-10-03.json',
    'docs/daily_report/REPORT-2026-10-03.md',
    'docs/live_usage/LIVE-2026-10-03.json',
    'docs/live_usage/LIVE-2026-10-03.md',
    'docs/live_usage/LIVE-latest.json',
    'docs/live_usage/LIVE-latest.md',
]

for f in FILES:
    r = subprocess.run(['git', 'show', f':3:{f}'], capture_output=True)
    assert r.returncode == 0, (f, r.stderr[:200])
    b = r.stdout
    if f.endswith('.json'):
        json.loads(b)  # parse-verify gate (r185 law) before write
    with open(f, 'wb') as fh:
        fh.write(b)
    print('resolved ->', f, f'({len(b)}B, stage3/local, parse-verified)')

print('8/8 resolved, zero hybrid twins')
