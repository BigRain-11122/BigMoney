"""r661 merge-conflict manual resolver (fail-closed faces beyond ALL_FACES).

Faces:
  snapshot: fundamental_b_layer_filter.json, _attrition_guard_scan.json (deep-ts probe take-new)
  twins:    REPORT-2026-10-04.json/.md, LIVE-2026-10-04.json/.md, LIVE-latest.json/.md
            (json face probes generated/updated ts to pick a SIDE; .md faces copied
             byte-for-byte from the SAME side blob -- r327/r329 twin law)
"""
import json
import re
import subprocess
import sys

TS_KEYS = ('generated', 'generated_at', 'updated', 'updated_at', 'ts', 'scanned_at', 'now')


def stages(path):
    """Return {stage: blob_sha} for a conflicted path."""
    out = subprocess.run(['git', 'ls-files', '-u', path], capture_output=True, text=True).stdout
    st = {}
    for ln in out.strip().splitlines():
        parts = ln.split()
        if len(parts) >= 3:
            st[int(parts[2])] = parts[1]  # stage -> blob sha
    return st


def blob(path, stage):
    st = stages(path)
    if stage not in st:
        return None
    return subprocess.run(['git', 'cat-file', 'blob', st[stage]], capture_output=True).stdout


def deep_ts(obj, depth=0):
    """Recursively locate newest wall-clock ts value; return ISO string or None."""
    best = None
    if depth > 8 or obj is None:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = str(k).lower().replace('-', '_')
            if isinstance(v, str) and re.match(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}', v):
                if any(t in kk for t in ('generated', 'updated', 'ts', 'scanned', 'now')):
                    if best is None or v > best:
                        best = v
            sub = deep_ts(v, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for it in obj:
            sub = deep_ts(it, depth + 1)
            if sub and (best is None or sub > best):
                best = sub
    return best


def resolve_snapshot(path, prefer=None):
    """take-new by deep ts probe across stage2(local)/stage3(origin)."""
    a = blob(path, 2)
    b = blob(path, 3)
    assert a is not None and b is not None, path + ': missing stages'
    ta, tb = None, None
    for side, raw in ((2, a), (3, b)):
        try:
            d = json.loads(raw.decode('utf-8'))
            t = deep_ts(d)
            if side == 2:
                ta = t
            else:
                tb = t
        except Exception:
            pass
    print(f'  {path}: local(:2:) ts={ta} origin(:3:) ts={tb}')
    if ta is None and tb is None:
        pick = 2 if prefer != 3 else 3
        print(f'  -> both probes None, prefer side {pick} ({prefer})')
    elif tb is None or (ta is not None and ta >= tb):
        pick = 2
    else:
        pick = 3
    raw = blob(path, pick)
    d = json.loads(raw.decode('utf-8'))
    open(path, 'wb').write(raw)
    print(f'  -> wrote side {pick} ({len(raw)}B), parse-verified')


def resolve_twin(json_path, md_path):
    """json face: deep-ts probe picks side; md face: same-side blob byte copy."""
    a = blob(json_path, 2)
    b = blob(json_path, 3)
    ta, tb = None, None
    for side, raw in ((2, a), (3, b)):
        try:
            ta_tb = deep_ts(json.loads(raw.decode('utf-8')))
            if side == 2:
                ta = ta_tb
            else:
                tb = ta_tb
        except Exception:
            pass
    print(f'  {json_path}: local ts={ta} origin ts={tb}')
    if ta is None and tb is None:
        pick = 2  # tie / probe-miss -> HEAD per r140
    elif tb is None or (ta is not None and ta >= tb):
        pick = 2
    else:
        pick = 3
    jraw = blob(json_path, pick)
    json.loads(jraw.decode('utf-8'))  # parse-verify before write
    open(json_path, 'wb').write(jraw)
    for mp in (md_path if isinstance(md_path, (list, tuple)) else [md_path]):
        mraw = blob(mp, pick)
        assert mraw is not None, mp + f': stage {pick} missing'
        open(mp, 'wb').write(mraw)
        print(f'  -> twin side {pick}: json {len(jraw)}B + md {mp} {len(mraw)}B same-side byte copy')
    print(f'  -> side {pick} wins (parse-verified json + same-side md)')


print('== snapshots ==')
resolve_snapshot(r'results/fundamental_b_layer_filter.json')
resolve_snapshot(r'results/_attrition_guard_scan.json')

print('== twins ==')
resolve_twin('docs/daily_report/REPORT-2026-10-04.json', 'docs/daily_report/REPORT-2026-10-04.md')
resolve_twin('docs/live_usage/LIVE-2026-10-04.json', 'docs/live_usage/LIVE-2026-10-04.md')
resolve_twin('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')
print('resolver done')
