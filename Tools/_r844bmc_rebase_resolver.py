"""r844 bm-c rebase UU resolver: 14 regen/runtime faces, per-file newer-wins
by embedded ts (r843 canon: facts-driven per-file ts read, zero literal
constants). ours (:2) = origin side (bm-b r852/853 S6 faces), theirs (:3) =
this machine's r844 S6 faces (01:32-33 run). Prints decision table, applies
git checkout --ours/--theirs per file. ts keys tried: ts, updated, generated,
generated_at, updated_at, last_attempt, time, now, asof (first parseable
ISO-looking string wins). Files with no parseable ts on either side ->
fallback theirs (replayed side = newest S6 run by wall clock)."""
import json
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "docs/daily_report/REPORT-2026-10-11.json",
    "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_r686bmb_d19_check.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_KEYS = ("ts", "updated", "generated", "generated_at", "updated_at",
           "last_attempt", "time", "now", "asof")
ISO_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def stage_bytes(spec):
    r = subprocess.run(["git", "-C", ROOT, "show", spec],
                       capture_output=True, timeout=30)
    return r.stdout if r.returncode == 0 else None


def extract_ts(data):
    """First parseable ISO-ish ts from known keys, then any line match."""
    try:
        d = json.loads(data.decode("utf-8", "replace"))
        if isinstance(d, dict):
            for k in TS_KEYS:
                v = d.get(k)
                if isinstance(v, str) and ISO_RE.search(v):
                    return v
            # nested one level
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
        ours = stage_bytes(":%s" % f)  # :2 = ours
        theirs = stage_bytes(":%s" % f)  # :3 = theirs
        # stage syntax needs :2:path / :3:path
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
        print("%-46s -> %-6s (%s) ours_ts=%s theirs_ts=%s" % (f, pick, why, to, tt))
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
