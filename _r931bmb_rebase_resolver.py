# -*- coding: utf-8 -*-
# _r931bmb_rebase_resolver.py -- r931 bm-b rebase UU resolver: 3 shared regen
# faces, per-file newer-wins by embedded ts (r844 canon: facts-driven per-file
# ts read, zero literal constants; r995 bm-c precedent: shared rolling faces
# live-wins). ours (:2) = origin side (bm-c r995 S6 faces), theirs (:3) =
# this machine's r931 replayed S6 faces (10:58-11:07 run).
import json
import re
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/token_usage.json",
]
TS_KEYS = ("ts", "updated", "generated", "generated_at", "updated_at",
           "last_attempt", "time", "now", "asof")
ISO_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_bytes(spec):
    r = subprocess.run(["git", "-C", ROOT, "show", spec],
                       capture_output=True, timeout=30)
    return r.stdout if r.returncode == 0 else None


def extract_ts(data):
    try:
        d = json.loads(data.decode("utf-8", "replace"))
        if isinstance(d, dict):
            for k in TS_KEYS:
                v = d.get(k)
                if isinstance(v, str) and ISO_RE.search(v):
                    return v
            for v in d.values():
                if isinstance(v, dict):
                    for k in TS_KEYS:
                        vv = v.get(k)
                        if isinstance(vv, str) and ISO_RE.search(vv):
                            return vv
    except Exception:
        pass
    m = ISO_RE.search(data.decode("utf-8", "replace"))
    return m.group(0) if m else None


def main():
    decisions = []
    for f in UU:
        ours = stage_bytes(":2:%s" % f)
        theirs = stage_bytes(":3:%s" % f)
        if ours is None or theirs is None:
            pick = "theirs" if theirs is not None else ("ours" if ours is not None else "abort")
            decisions.append((f, pick, "stage-missing", None, None))
            continue
        to, tt = extract_ts(ours), extract_ts(theirs)
        if to and tt:
            pick = "theirs" if tt >= to else "ours"
            why = "ts newer-wins"
        else:
            pick = "theirs"
            why = "fallback theirs (unparseable ts)"
        decisions.append((f, pick, why, to, tt))
    for f, pick, why, to, tt in decisions:
        print("%-42s -> %-6s (%s) ours_ts=%s theirs_ts=%s" % (f, pick, why, to, tt))
    bad = [d for d in decisions if d[1] == "abort"]
    if bad:
        print("ABORT: stage missing on %d files" % len(bad))
        return 1
    for f, pick, _, _, _ in decisions:
        side = "theirs" if pick == "theirs" else "ours"
        r = subprocess.run(["git", "-C", ROOT, "checkout", "--%s" % side, f],
                           capture_output=True, timeout=30)
        if r.returncode != 0:
            print("CHECKOUT FAIL %s: %s" % (f, r.stderr.decode("utf-8", "replace")))
            return 1
        r = subprocess.run(["git", "-C", ROOT, "add", f],
                           capture_output=True, timeout=30)
        if r.returncode != 0:
            print("ADD FAIL %s: %s" % (f, r.stderr.decode("utf-8", "replace")))
            return 1
    print("resolved+staged %d/%d" % (len(decisions), len(UU)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
