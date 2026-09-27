# -*- coding: utf-8 -*-
"""R81 bm-c rebase S6-mirror batch resolver (canon: r317/r319/R208/R209/r311 deep-scan probe-direction).

Batch = 28 UU vs bm-a r323 same-window S6 mirror (mine 12:58 vs origin ~13:0x).
Snapshots: per-file deep-scan ts probe BOTH stages, newer side wins verbatim
(no blind take-new, r311/r319 probe-first law); ts-less deterministic faces take :2:.
Ledgers: union zero-loss (compute_audit history by ts / regime history asof +
transitions ts / autofill launches 5-tuple key + cap50 oldest-dropped assert /
x2_watch_log line union). js-wrapper = whole bytes (R209).
After: git add marks resolution; rebase --continue externally.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
TS_KEYS = ("ts", "updated", "generated", "asof", "updated_at", "last_write", "written_at")
AUTOFFILL_KEY = ("ts", "machine", "entry", "shard", "pid")
MARKER = re.compile(rb"^(<<<<<<<|=======$|>>>>>>>)", re.M)


def stage_bytes(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def has_stages(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path], capture_output=True, text=True)
    return bool(r.stdout.strip())


def deep_ts(obj, best=""):
    """r311 deep-scan: recursively collect ts-like values; return max string."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TS_KEYS and len(v) >= 8:
                if v > best:
                    best = v
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for e in obj:
            best = deep_ts(e, best)
    return best


def side_ts(raw):
    try:
        return deep_ts(json.loads(raw.decode("utf-8-sig")))
    except Exception:
        return ""


def resolve_snapshot(path):
    a, b = stage_bytes(path, 2), stage_bytes(path, 3)
    ta, tb = side_ts(a), side_ts(b)
    if ta or tb:
        win = 2 if ta >= tb else 3          # tie -> :2: (origin/HEAD, r140)
        why = "ts %s>=%s" % (ta or "none", tb or "none")
    else:
        win, why = 2, "ts-less deterministic face -> :2:"
    raw = a if win == 2 else b
    if not path.endswith((".md", ".js")):
        json.loads(raw.decode("utf-8-sig"))  # parse-verify before write (r185)
    assert not MARKER.search(raw), "marker leak in %s" % path
    (ROOT / path).write_bytes(raw)
    return why, len(raw)


def union_by_key(a, b, key):
    ka = {str(e.get(key, "")) for e in a}
    kb = {str(e.get(key, "")) for e in b}
    expect = len(ka | kb)
    seen = {}
    for src in (a, b):
        for e in src:
            seen.setdefault(str(e.get(key, "")), e)
    result = sorted(seen.values(), key=lambda e: str(e.get(key, "")))
    assert len(result) == expect, "union collapse %d+%d->%d (expect %d)" % (len(a), len(b), len(result), expect)
    return result, expect


def fmt_write(path, out, base_n=2):
    raw = stage_bytes(path, base_n)
    crlf = b"\r\n" in raw
    nl = b"\r\n" if crlf else b"\n"
    indent = " "
    for line in raw.decode("utf-8-sig").splitlines():
        s = line.lstrip(" ")
        if s and line != s:
            indent = " " * (len(line) - len(s))
            break
    (ROOT / path).write_bytes(
        (json.dumps(out, ensure_ascii=False, indent=indent) + "\n").encode("utf-8").replace(b"\n", nl))
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def resolve_audit():
    path = "results/compute_audit.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    merged, expect = union_by_key(ours["history"], mine["history"], "ts")
    out = dict(ours)
    out["history"] = merged
    # r319: probe compare path exists before use
    ta = str(((ours.get("latest") or {}).get("ts")) or "")
    tb = str(((mine.get("latest") or {}).get("ts")) or "")
    out["latest"] = (ours if ta >= tb else mine)["latest"]
    back = fmt_write(path, out)
    assert len(back["history"]) == expect
    print("  %s: history union -> %d (expect %d), latest.ts=%s" % (path, len(merged), expect, back["latest"]["ts"]))


def resolve_regime():
    path = "results/regime_state.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    out = dict(ours if str(ours.get("updated", "")) >= str(mine.get("updated", "")) else mine)
    hist, hexp = union_by_key(ours.get("history") or [], mine.get("history") or [], "asof")
    trans, texp = union_by_key(ours.get("transitions") or [], mine.get("transitions") or [], "ts")
    out["history"], out["transitions"] = hist, trans
    back = fmt_write(path, out)
    assert len(back["history"]) == hexp and len(back["transitions"]) == texp
    print("  %s: history union -> %d, transitions -> %d, updated=%s" % (path, hexp, texp, back.get("updated")))


def resolve_autofill():
    path = "results/autofill_state.json"
    ours = json.loads(stage_bytes(path, 2).decode("utf-8-sig"))
    mine = json.loads(stage_bytes(path, 3).decode("utf-8-sig"))
    for label, d in (("ours", ours), ("mine", mine)):        # r319 key-exist probe
        for e in d.get("launches", []):
            for f in AUTOFFILL_KEY:
                if f not in e:
                    sys.exit("VIOLATION: key %r missing in %s entry" % (f, label))
    seen = {}
    for src in (mine, ours):                                  # :2: wins collisions (r140 HEAD-side)
        for e in src.get("launches", []):
            seen.setdefault(tuple(e.get(f) for f in AUTOFFILL_KEY), e)
    merged = sorted(seen.values(), key=lambda e: str(e.get("ts", "")), reverse=True)
    kept, dropped = merged[:50], merged[50:]                  # R215 rolling cap
    if dropped:
        assert min(e["ts"] for e in kept) >= max(e["ts"] for e in dropped), "cap dropped non-oldest"
    kept.sort(key=lambda e: str(e.get("ts", "")))             # r245 ascending write-back
    out = dict(ours)
    out["launches"] = kept
    lt_o, lt_m = ours.get("last_tick"), mine.get("last_tick")
    out["last_tick"] = (lt_o if str((lt_o or {}).get("ts", "")) >= str((lt_m or {}).get("ts", "")) else lt_m)
    back = fmt_write(path, out)
    assert isinstance(back["last_tick"], dict)
    ka = {tuple(e.get(f) for f in AUTOFFILL_KEY) for e in ours.get("launches", [])}
    kb = {tuple(e.get(f) for f in AUTOFFILL_KEY) for e in mine.get("launches", [])}
    assert len(ka | kb) == len(merged), "pre-cap union zero-loss"
    print("  %s: union %d -> cap50 kept %d dropped %d, last_tick.ts=%s" % (
        path, len(merged), len(kept), len(dropped), back["last_tick"]["ts"]))


def resolve_x2log():
    path = "results/x2_watch_log.jsonl"
    a = stage_bytes(path, 2).decode("utf-8-sig").splitlines()
    b = stage_bytes(path, 3).decode("utf-8-sig").splitlines()
    lines = sorted(set(a) | set(b))
    assert len(lines) == len(set(a) | set(b)), "line union zero-loss"
    raw = stage_bytes(path, 2)
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    (ROOT / path).write_bytes(nl.join(l.encode("utf-8") for l in lines) + nl)
    print("  %s: line union -> %d (|A|=%d |B|=%d)" % (path, len(lines), len(a), len(b)))


def main():
    n = 0
    for path in SNAPSHOTS:
        if not has_stages(path):
            continue
        why, size = resolve_snapshot(path)
        print("  %s: take-side %s (%dB)" % (path, why, size))
        n += 1
    for fn in (resolve_audit, resolve_regime, resolve_autofill, resolve_x2log):
        p = {resolve_audit: "results/compute_audit.json", resolve_regime: "results/regime_state.json",
             resolve_autofill: "results/autofill_state.json", resolve_x2log: "results/x2_watch_log.jsonl"}[fn]
        if has_stages(p):
            fn()
            n += 1
    left = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True).stdout.strip()
    if left:
        print("UNRESOLVED LEFT:", left)
        return 1
    for path in SNAPSHOTS + ["results/compute_audit.json", "results/regime_state.json",
                             "results/autofill_state.json", "results/x2_watch_log.jsonl"]:
        if (ROOT / path).exists():
            subprocess.run(["git", "add", "--", path])
    print("resolved=%d, all staged" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
