# r847 snapshot-family conflict resolver: take-new by deep ts probe from STAGED
# blobs (:2:=origin side, :3:=ours) per bigmoney-conflict-resolve skill laws
# (probe staged blob not working tree R350; deep-scan nested r311; path-exists
# first r319; ts value must match ^20\d{2}-; twins take the SAME side).
import json
import re
import subprocess
import sys

TS_RE = re.compile(r'^20\d{2}-')


def staged_blob(stage, path):
    out = subprocess.run(['git', 'show', ':%s:%s' % (stage, path)],
                        capture_output=True).stdout
    return out


def deep_ts(obj, path=''):
    """Deep-scan for ts-like string values; return latest ISO-ish ts or None."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = k.lower().replace('_', '').replace('-', '')
            if isinstance(v, str) and TS_RE.match(v) and ('ts' in kk or 'time' in kk or 'date' in kk or 'at' in kk or 'stamp' in kk):
                if best is None or v > best:
                    best = v
            sub = deep_ts(v, path + '/' + k)
            if sub and (best is None or sub > best):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            sub = deep_ts(v, path + '/%d' % i)
            if sub and (best is None or sub > best):
                best = sub
    return best


def resolve_snapshot(path):
    theirs = staged_blob(2, path)
    ours = staged_blob(3, path)
    try:
        tj = json.loads(theirs)
        oj = json.loads(ours)
    except Exception as e:
        print('JSON parse fail %s: %s' % (path, e))
        return None
    tt = deep_ts(tj)
    ot = deep_ts(oj)
    # R350 hardening: strip _/- in key names done in deep_ts; ts format gate done.
    side = None
    if tt and ot:
        side = 'theirs' if tt > ot else 'ours'  # tie -> ours (r140)
    elif ot:
        side = 'ours'
    elif tt:
        side = 'theirs'
    if side is None:
        print('NO ts on either side for %s -- FAIL-CLOSED' % path)
        return None
    blob = theirs if side == 'theirs' else ours
    # write back exactly the winning staged blob bytes (byte-level take-side)
    with open(path, 'wb') as f:
        f.write(blob)
    print('%s -> %s (ts theirs=%s ours=%s)' % (path, side, tt, ot))
    return side


if __name__ == '__main__':
    for p in sys.argv[1:]:
        resolve_snapshot(p)
