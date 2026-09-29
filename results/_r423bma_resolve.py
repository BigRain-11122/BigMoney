import subprocess
import json
import sys


def stage_blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'stage {stage} read fail for {path}: {r.stderr[:200]}')
    return r.stdout


def deep_ts(obj, key_pref=('generated', 'updated', 'ts', 'written', 'asof')):
    """Deep-scan nested layers for the true ts (r311 law); return max wall-clock ts string."""
    found = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = str(k).lower().replace('_', '').replace('-', '')
                if any(nk.startswith(p.replace('_', '').replace('-', '')) for p in key_pref):
                    if isinstance(v, str) and v[:4] == '2026' and len(v) >= 10:
                        found.append((path + [k], v))
                walk(v, path + [k])
        elif isinstance(o, list):
            for i, v in enumerate(o[:200]):
                walk(v, path + [i])
    walk(obj, [])
    return found


def pick_newer_side(json_path, side_a=2, side_b=3):
    a = json.loads(stage_blob(side_a, json_path))
    b = json.loads(stage_blob(side_b, json_path))
    ta = deep_ts(a)
    tb = deep_ts(b)
    # probe compare-path existence first (r319); use the FIRST top-priority generated-ish ts
    def best(pairs):
        return max(p[1] for p in pairs) if pairs else None
    va, vb = best(ta), best(tb)
    print(f'  ts probes {json_path}: origin(:2:)={va} | replay(:3:)={vb}')
    if va is None and vb is None:
        raise RuntimeError('no ts on either side')
    if vb is None or (va is not None and va >= vb):
        return 2, va
    return 3, vb


def resolve_twin_pair(json_path, md_path):
    print(f'== twin pair {json_path}')
    side, ts = pick_newer_side(json_path)
    jbytes = stage_blob(side, json_path)
    mbytes = stage_blob(side, md_path)
    # parse-verify json before write (r185 law)
    json.loads(jbytes)
    open(json_path, 'wb').write(jbytes)
    open(md_path, 'wb').write(mbytes)
    print(f'  -> took side :{side}: (ts={ts}); {len(jbytes)}B json + {len(mbytes)}B md written (same-side coupling)')


def resolve_snapshot(path):
    print(f'== snapshot {path}')
    side, ts = pick_newer_side(path)
    b = stage_blob(side, path)
    json.loads(b)
    open(path, 'wb').write(b)
    print(f'  -> took side :{side}: (ts={ts}); {len(b)}B written')


resolve_snapshot('results/fundamental_b_layer_filter.json')
resolve_twin_pair('docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md')
resolve_twin_pair('docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md')
resolve_twin_pair('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')
print('ALL HAND-RESOLVES DONE')
