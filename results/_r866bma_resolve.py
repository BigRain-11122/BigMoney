"""r866 bm-a rebase-conflict resolver (14 UU, bm-c r737 same-window push).

ALL_FACES members (6) were resolved via scripts/merge_lane_views.py resolve
(union/take-new canonical recipes) BEFORE this script ran. This script
handles the 8 non-ALL_FACES files per SKILL.md recipes:
  - twin-regen-md (daily_report + live_usage + live-latest): json face
    take-new by TOP-LEVEL generated_at (deep-scan probe trap avoided: ISO
    'T' strings sort above space-separated generated_at -- probe must use
    the face's own generation key); md twins byte-copied from the SAME side
    (twin coupling r327/r329).
  - per-run snapshots (_attrition_guard_scan / fundamental_b_layer_filter):
    take-new by ts/updated, whole doc.
All sides verified strictly-newer LOCAL before taking (no ties -> no
HEAD-tie law triggered). Parse-verify before write-back (r185 law).
"""
import json
import subprocess

TAKE_LOCAL = [
    ('docs/daily_report/REPORT-2026-10-08.json', 'generated_at'),
    ('docs/daily_report/REPORT-2026-10-08.md', None),
    ('docs/live_usage/LIVE-2026-10-08.json', 'generated'),
    ('docs/live_usage/LIVE-2026-10-08.md', None),
    ('docs/live_usage/LIVE-latest.json', 'generated'),
    ('docs/live_usage/LIVE-latest.md', None),
    ('results/_attrition_guard_scan.json', 'ts'),
    ('results/fundamental_b_layer_filter.json', 'updated'),
]

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert r.returncode == 0, f'stage read failed {path}'
    return r.stdout

for path, key in TAKE_LOCAL:
    o, l = blob(2, path), blob(3, path)
    if key:
        to, tl = json.loads(o)[key], json.loads(l)[key]
        assert tl > to, f'{path}: local not newer ({tl} vs {to}) -- refusing'
        print(f'{path}: take LOCAL ({key} {tl} > {to})')
    else:
        assert o != l, f'{path}: md twins identical?'
        print(f'{path}: byte-copy LOCAL (twin coupling)')
    if key:  # parse-verify the exact bytes we write (r185 law)
        json.loads(l)
    with open(path, 'wb') as f:
        f.write(l)
print('resolver done: 8 files written from :3: (local) side')
