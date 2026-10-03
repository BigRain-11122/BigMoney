# -*- coding: utf-8 -*-
"""_r427bmc_resolve.py v2 -- DYNAMIC conflict resolver for treadmill push windows.
Discovers UU/AA set from git status; per file: ts-compare stage :2: (origin/ours)
vs :3: (mine/theirs); take-new by ts, tie/unknown -> origin (public tip side);
refuse to stage marker-bearing side. Rebase semantics documented in v1 header.
"""
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000


def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    return p.returncode, p.stdout, p.stderr


def blob(rev):
    return sg(["show", rev])[1]


def ts_of(b):
    m = re.search(rb'"(ts|timestamp|updated|updated_at|asof|generated_at|'
                  rb'scan_ts|probe_ts|clock)"\s*:\s*"([^"]+)"', b)
    if m:
        return m.group(2).decode("utf-8", "replace")[:19]
    m = re.search(rb'"(epoch|heartbeat_epoch_utc)"\s*:\s*([0-9]{9,})', b)
    if m:
        return m.group(2).decode()
    return "?"


def markers(b):
    return len(re.findall(rb"^(<<<<<<< |=======$|>>>>>>> )", b, re.M))


rc, out, _ = sg(["status", "--porcelain"])
files = []
for ln in out.decode("utf-8", "replace").splitlines():
    if ln[:2] in ("UU", "AA", "AU", "UA", "DU", "UD"):
        files.append(ln[3:].strip())
if not files:
    print("NO_UNMERGED -- nothing to resolve")
    sys.exit(0)
n_mine = n_origin = 0
for f in files:
    o, t = blob(":2:" + f), blob(":3:" + f)
    if not o and t:
        side = "mine"
    elif o and not t:
        side = "origin"
    else:
        to, tt = ts_of(o), ts_of(t)
        if to == "?" and tt == "?":
            side = "origin"  # tie/unknown -> public-tip side
        else:
            side = "origin" if to >= tt else "mine"
    pick = {"origin": o, "mine": t}[side]
    assert markers(pick) == 0, "marker-bearing side for " + f
    with open(f, "wb") as fh:
        fh.write(pick)
    r = sg(["add", "--", f])
    assert r[0] == 0, (f, r[2])
    n_mine += side == "mine"
    n_origin += side == "origin"
    print("%-46s -> take=%s" % (f, side))
print("RESOLVE_DONE files=%d mine=%d origin=%d" % (len(files), n_mine, n_origin))
