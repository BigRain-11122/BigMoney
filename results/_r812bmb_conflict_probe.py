import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FILES = [r"results\token_usage.json", r"results\update_status.json"]
TS_KEYS = ["generated", "updated", "now", "prev_generated"]

for f in FILES:
    t = open(f, encoding="utf-8", errors="replace").read()
    # split on conflict markers
    parts = re.split(r"^(<<<<<<< HEAD|=======|>>>>>>> )", t, flags=re.M)
    # walk: find HEAD blocks and MINE blocks pairwise
    head_side = []
    mine_side = []
    mode = None
    for p in parts:
        if p == "<<<<<<< HEAD":
            mode = "head"
            continue
        if p == "=======":
            mode = "mine"
            continue
        if p and p.startswith(">>>>>>> "):
            mode = None
            continue
        if mode == "head":
            head_side.append(p)
        elif mode == "mine":
            mine_side.append(p)
    print("==", f)
    for label, chunks in (("HEAD(origin-base)", head_side), ("MINE(ac495a6fb)", mine_side)):
        ts = []
        for c in chunks:
            for k in TS_KEYS:
                ts += re.findall(r'"%s": "([^"]+)"' % k, c)
        print("  %s ts=%s bytes=%d" % (label, ts[:3], sum(len(c) for c in chunks)))
    # try full-side json parse to preview take-newer viability
    if len(head_side) == 1 and len(mine_side) == 1:
        # whole-file conflict: single block each
        try:
            h = json.loads(head_side[0])
            m = json.loads(mine_side[0])
            hk = [k for k in ("generated", "updated") if k in h]
            mk = [k for k in ("generated", "updated") if k in m]
            print("  HEAD json OK keys %s=%s | MINE json OK keys %s=%s" % (
                hk, [h.get(k) for k in hk], mk, [m.get(k) for k in mk]))
        except Exception as e:
            print("  whole-side json parse fail:", e)
    else:
        print("  multi-block: head_blocks=%d mine_blocks=%d (whole-file conflict with preamble/postamble)" % (
            len(head_side), len(mine_side)))
