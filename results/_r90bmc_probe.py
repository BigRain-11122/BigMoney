# -*- coding: utf-8 -*-
"""r90 bm-c probe: pick-1 (r87 642c3c41 replay onto origin/main+9) UU face classifier.
Sizes/areas in UTF-8 encode bytes (r89 canon). Read-only."""
import io, json, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout

def blobs(path):
    return git("show", f":1:{path}"), git("show", f":2:{path}"), git("show", f":3:{path}")

def deep_ts(obj):
    best = [""]
    KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof",
            "last_run", "written_at", "time", "datetime", "snapshot_at", "run_at")
    def scan(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in KEYS and isinstance(v, str) and len(v) >= 16:
                    nv = v.replace(" ", "T")[:19]
                    if nv > best[0]:
                        best[0] = nv
                scan(v)
        elif isinstance(x, list):
            for v in x:
                scan(v)
    scan(obj)
    return best[0]

uu = [l.decode().strip() for l in subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
     capture_output=True).stdout.splitlines() if l.strip()]
print(f"UU x{len(uu)} (encode-byte areas)")
for p in uu:
    b, o, t = blobs(p)
    print(f"\n== {p}")
    print(f"  bytes base={len(b)} origin={len(o)} mine={len(t)}")
    if p.endswith(".json"):
        try:
            jo, jt = json.loads(o), json.loads(t)
        except Exception as e:
            print(f"  !! json parse fail: {e}")
            continue
        ko = set(jo) if isinstance(jo, dict) else None
        kt = set(jt) if isinstance(jt, dict) else None
        print(f"  top-keys origin={sorted(ko) if ko else type(jo)} mine={sorted(kt) if kt else type(jt)}")
        print(f"  keyset {'identical' if ko == kt else 'DIVERGED'} ts_o={deep_ts(jo)} ts_t={deep_ts(jt)}")
        for src, j in (("o", jo), ("t", jt)):
            if isinstance(j, dict):
                arrs = {k: len(v) for k, v in j.items() if isinstance(v, list) and v}
                if arrs:
                    print(f"  {src} arrays: {arrs}")
    else:
        bl, ol, tl = b.decode("utf-8"), o.decode("utf-8"), t.decode("utf-8")
        print(f"  lines base={len(bl.splitlines())} origin={len(ol.splitlines())} mine={len(tl.splitlines())}")
        both_ext = ol.startswith(bl) and tl.startswith(bl)
        print(f"  both-extend-base={both_ext} origin-delta={len(ol)-len(bl)} mine-delta={len(tl)-len(bl)}")
print("PROBE-R90-OK")
