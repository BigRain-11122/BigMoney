# -*- coding: utf-8 -*-
"""r870 bm-a rebase-conflict resolver (hand recipes per bigmoney-conflict-resolve skill):
- snapshot class: deep-ts probe both rebase stage blobs, take-newer whole doc (bytes verbatim)
- twin-regen-md class: probe the .json side for newest generated ts, copy BOTH json+md
  byte-verbatim from the SAME side (twin-side coupling law r327/r329 -- md is not JSON,
  never json.loads an md twin; no hybrid twins)
Stage law: :2: = base_side (origin/main = bm-c r745), :3: = replay_side (bm-a closeout).
Zero working-tree reads; stage blobs via `git show :N:path` raw bytes (subprocess, zero PS pipe)."""
import subprocess, json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def stage_bytes(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_RE = re.compile(r'^20\d{2}-')

def deep_ts(obj, best=None):
    """deep-scan nested layers for the newest wall-clock ts value (r311/D-20260927-09)."""
    if best is None:
        best = ''
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = str(k).lower().replace('_', '').replace('-', '')
            if isinstance(v, str) and TS_RE.match(v) and ('ts' in kn or 'generated' in kn or 'updated' in kn or 'time' in kn) and ('T' in v or ':' in v):
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def resolve_snapshot(path, probe_hint=None):
    b2, b3 = stage_bytes(2, path), stage_bytes(3, path)
    j2, j3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if t3 >= t2 else 2   # tie -> HEAD/replay side (r140)
    win = open(os.path.join(ROOT, path), 'wb')
    win.write(b3 if side == 3 else b2)
    win.close()
    json.loads(open(os.path.join(ROOT, path), 'rb').read().decode('utf-8'))  # parse-verify
    print(f'[snapshot] {path}: base={t2 or "none"} replay={t3 or "none"} -> side:{side} ({"replay/bm-a" if side==3 else "base/bm-c"})')

def resolve_twin(json_path, md_path):
    b2, b3 = stage_bytes(2, json_path), stage_bytes(3, json_path)
    j2, j3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    t2, t3 = deep_ts(j2), deep_ts(j3)
    side = 3 if t3 >= t2 else 2
    for path in (json_path, md_path):
        b = stage_bytes(side, path)
        assert b, f'stage {side} empty for {path}'
        open(os.path.join(ROOT, path), 'wb').write(b)
    # verify twins: json parses; md carries no conflict markers and is same-side
    json.loads(open(os.path.join(ROOT, json_path), 'rb').read().decode('utf-8'))
    md_txt = open(os.path.join(ROOT, md_path), 'rb').read().decode('utf-8', errors='replace')
    assert '<<<<<<<' not in md_txt and '>>>>>>>' not in md_txt, f'{md_path} has conflict markers'
    print(f'[twin] {json_path}+{os.path.basename(md_path)}: base={t2 or "none"} replay={t3 or "none"} -> side:{side} BOTH faces same-side')

# --- snapshot class ---
resolve_snapshot('results/fundamental_b_layer_filter.json')
resolve_snapshot('results/_attrition_guard_scan.json')

# --- twin-regen-md class (json side decides, both faces byte-copied same side) ---
resolve_twin('docs/daily_report/REPORT-2026-10-08.json', 'docs/daily_report/REPORT-2026-10-08.md')
resolve_twin('docs/live_usage/LIVE-2026-10-08.json', 'docs/live_usage/LIVE-2026-10-08.md')
resolve_twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')

# --- final UU sweep: zero unresolved conflict paths left in the porcelain ---
r = subprocess.run(['git', 'status', '--short'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
uu = [l for l in r.stdout.splitlines() if l.startswith('UU') or l.startswith('AA') or l.startswith('DD')]
print('remaining UU/AA/DD:', uu if uu else 'NONE')
sys.exit(0 if not uu else 2)
