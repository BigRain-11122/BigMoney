#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r815 bm-b rebase-conflict resolver (canonical recipes, bigmoney-conflict-resolve SKILL).

Context: r815 S7 push-window collision. bm-b r815 commit ac67faec3 (04:31) replayed
onto origin tip d4d3a0aa7 (6 incoming commits, bm-c W17 ignition keepalives + churn
absorbs + bm-a r938 T-181 prereg freeze). Rebase stopped at pick ac67faec3 with 31 UU
files (same-day S6-regenerated artifact storm, both-machines-wrote AA class).
Ours (stage-2 / HEAD during rebase) = d4d3a0aa7. Theirs = ac67faec3 (r815 bm-b).

Recipes (classify_conflicts.py 30 classified + 1 UNKNOWN manual per r813 precedent):
  rolling-ledger  compute_audit.json / regime_state.json   union history/transitions, take-new state (r188/R208)
  append-log      x2_watch_log.jsonl                        line-level union zero loss (r188/r217)
  snapshot x24     *_status/scorecard/paper/export/summaries take-new via hardened deep-ts probe (r100/R350)
  twin-pairs       docs/daily_report + docs/live_usage      atomic take-side, .md twins mirror (r98/r99/r100/r439bmb)
  js-wrapper      dashboard_status.js                       take-side WHOLE BYTES (R209), side follows .json twin probe
  UNKNOWN manual  results/_attrition_guard_scan.json        snapshot take-new by ts (r813 SNAP_TS_KEY precedent)
Laws kept: r185 parse-verify before write-back+add; r140 same-second tie -> HEAD(ours);
R350 value-shape gate (ts values must carry time-of-day to feed max; key-EXCLUDE lists
forbidden); zero-loss union assertions; r813 resolver lineage reused per anti-dup law.
"""
import json
import re
import subprocess

OURS = "d4d3a0aa7"
THEIRS = "ac67faec3"

TS_FAMS = ("generated", "generatedat", "updated", "stateupdated", "asof", "ts")
VAL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %s:%s: %s" % (rev, path, r.stderr[:200]))
    return r.stdout


def deep_ts(d, best=""):
    """Hardened wall-clock probe (r100/R350): normalize key (strip _/-), family
    prefix match, value must be timestamp-shaped WITH time-of-day before it may
    feed the max. Recurse nested layers (r311). No key-EXCLUDE lists (R350)."""
    if isinstance(d, dict):
        for k, v in d.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and VAL_RE.match(v) and v > best:
                if any(nk.startswith(f) for f in TS_FAMS):
                    best = v
            best = deep_ts(v, best)
    elif isinstance(d, list):
        for e in d:
            best = deep_ts(e, best)
    return best


def fmt_probe(b):
    crlf = b"\r\n" in b[:400]
    trail_nl = b.endswith(b"\n")
    second = b.split(b"\n", 2)[1] if b.count(b"\n") >= 2 else b""
    indent = len(second) - len(second.lstrip())
    return crlf, trail_nl, (indent if 0 < indent < 9 else 2)


def dump_like(obj, probe):
    crlf, trail_nl, ind = probe
    s = json.dumps(obj, ensure_ascii=False, indent=ind)
    if crlf:
        s = s.replace("\n", "\r\n")
    if trail_nl:
        s += "\r\n" if crlf else "\n"
    return s.encode("utf-8")


SNAP_FILES = [
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/_attrition_guard_scan.json",   # UNKNOWN->manual: r813 snapshot precedent
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-10-09.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]

TAKE_SIDE_PAIRS = {  # json probe file -> .md twins mirrored atomically
    "docs/daily_report/REPORT-2026-10-10.json": ["docs/daily_report/REPORT-2026-10-10.md"],
    "docs/live_usage/LIVE-2026-10-10.json": ["docs/live_usage/LIVE-2026-10-10.md"],
    "docs/live_usage/LIVE-latest.json": ["docs/live_usage/LIVE-latest.md"],
}

JS_WRAPPER = "results/dashboard_status.js"   # side follows dashboard_status.json probe


def main():
    receipt = {"resolver": "results/_r815bmb_resolve.py", "ours": OURS,
               "theirs": THEIRS, "resolved": [], "asserts": []}
    resolved_paths = []

    # 1) snapshots: take-new via hardened deep-ts probe (tie -> ours/HEAD, r140)
    for p in SNAP_FILES:
        o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
        to_, tt = deep_ts(o), deep_ts(t)
        side = "theirs" if tt > to_ else "ours"
        src = THEIRS if side == "theirs" else OURS
        open(p, "wb").write(blob(src, p))
        json.loads(open(p, "rb").read())  # r185 parse-verify
        resolved_paths.append(p)
        receipt["resolved"].append({"path": p, "recipe": "snapshot-take-new",
                                    "side": side, "ts_ours": to_, "ts_theirs": tt})

    # 2) twin pairs: atomic side choice, .md twins mirror the SAME side
    for p, twins in TAKE_SIDE_PAIRS.items():
        o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
        to_, tt = deep_ts(o), deep_ts(t)
        side = "theirs" if tt > to_ else "ours"
        src = THEIRS if side == "theirs" else OURS
        open(p, "wb").write(blob(src, p))
        json.loads(open(p, "rb").read())
        resolved_paths.append(p)
        receipt["resolved"].append({"path": p, "recipe": "twin-atomic-take-side",
                                    "side": side, "ts_ours": to_, "ts_theirs": tt})
        for tw in twins:
            open(tw, "wb").write(blob(src, tw))
            resolved_paths.append(tw)
            receipt["resolved"].append({"path": tw, "recipe": "twin-mirror", "side": side})

    # 3) js-wrapper snapshot: side follows the .json twin probe, whole bytes (R209)
    js_side = next(r for r in receipt["resolved"]
                   if r["path"] == "results/dashboard_status.json")["side"]
    src = THEIRS if js_side == "theirs" else OURS
    open(JS_WRAPPER, "wb").write(blob(src, JS_WRAPPER))
    resolved_paths.append(JS_WRAPPER)
    receipt["resolved"].append({"path": JS_WRAPPER, "recipe": "js-wrapper-take-side-bytes",
                                "side": js_side})
    receipt["asserts"].append(
        "dashboard_status.js wrapper preserved: %s" %
        (blob(src, JS_WRAPPER).lstrip()[:16].decode("utf-8", "replace"), ))

    # 4) compute_audit.json: rolling-ledger union history by ts + take-new latest
    p = "results/compute_audit.json"
    o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
    merged = {}
    for e in o["history"] + t["history"]:
        if e["ts"] not in merged:          # r140 same-ts tie -> ours (iterated first)
            merged[e["ts"]] = e
    hist = sorted(merged.values(), key=lambda e: e["ts"])
    latest = t["latest"] if deep_ts(t["latest"]) > deep_ts(o["latest"]) else o["latest"]
    out = {"latest": latest, "history": hist}
    open(p, "wb").write(dump_like(out, fmt_probe(blob(OURS, p))))
    v = json.loads(open(p, "rb").read())
    exp = len({e["ts"] for e in o["history"]} | {e["ts"] for e in t["history"]})
    assert len(v["history"]) == exp, "union loss: %d != %d" % (len(v["history"]), exp)
    resolved_paths.append(p)
    receipt["resolved"].append({"path": p, "recipe": "rolling-ledger-union",
                                "ours_hist": len(o["history"]),
                                "theirs_hist": len(t["history"]), "union": exp,
                                "latest_side": "theirs" if latest == t["latest"] else "ours"})
    receipt["asserts"].append("compute_audit union zero-loss: |A U B| = %d rows asserted" % exp)

    # 5) regime_state.json: union transitions/history by asof + take-new state fields
    p = "results/regime_state.json"
    o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
    out = dict(o)
    if deep_ts(t) > deep_ts(o):
        for k, val in t.items():
            if not isinstance(val, list):
                out[k] = val
    hmap = {}
    for e in o.get("history", []) + t.get("history", []):
        if e.get("asof") not in hmap:       # r140 same-key tie -> ours first
            hmap[e["asof"]] = e
    out["history"] = sorted(hmap.values(), key=lambda e: e.get("asof", ""))
    tmap = {}
    for e in o.get("transitions", []) + t.get("transitions", []):
        key = (e.get("from"), e.get("to"), e.get("asof", e.get("ts", "")))
        if key not in tmap:
            tmap[key] = e
    out["transitions"] = sorted(tmap.values(), key=lambda e: str(e.get("asof", e.get("ts", ""))))
    open(p, "wb").write(dump_like(out, fmt_probe(blob(OURS, p))))
    v = json.loads(open(p, "rb").read())
    exp_h = len({e.get("asof") for e in o.get("history", [])}
                | {e.get("asof") for e in t.get("history", [])})
    assert len(v["history"]) == exp_h, "regime history union loss %d != %d" % (
        len(v["history"]), exp_h)
    resolved_paths.append(p)
    receipt["resolved"].append({"path": p, "recipe": "rolling-ledger-union+take-new-state",
                                "history_union": exp_h,
                                "transitions_union": len(out["transitions"])})
    receipt["asserts"].append("regime_state union zero-loss: history |A U B| = %d" % exp_h)

    # 6) x2_watch_log.jsonl: append-log line-level union zero loss
    p = "results/x2_watch_log.jsonl"
    lo = [ln for ln in blob(OURS, p).decode("utf-8").splitlines() if ln.strip()]
    lt = [ln for ln in blob(THEIRS, p).decode("utf-8").splitlines() if ln.strip()]
    seen, union = set(), []
    for ln in lo + lt:
        if ln not in seen:
            seen.add(ln)
            union.append(ln)
    assert len(union) == len(set(lo) | set(lt)), "jsonl union loss"
    nl = "\r\n" if b"\r\n" in blob(OURS, p)[:400] else "\n"
    open(p, "wb").write((nl.join(union) + nl).encode("utf-8"))
    resolved_paths.append(p)
    receipt["resolved"].append({"path": p, "recipe": "append-log-union",
                                "ours_lines": len(lo), "theirs_lines": len(lt),
                                "union": len(union)})
    receipt["asserts"].append("x2_watch_log union zero-loss: %d = |A U B|" % len(union))

    # 7) git add resolved set + marker sweep
    subprocess.run(["git", "add", "--"] + resolved_paths, check=True)
    marker = re.compile(rb"^(<<<<<<< |>>>>>>> |=======$)", re.M)
    bad = []
    for r in receipt["resolved"]:
        b = open(r["path"], "rb").read()
        if marker.search(b):
            bad.append(r["path"])
    assert not bad, "markers remain: %s" % bad
    receipt["asserts"].append("marker sweep: 0 conflict markers in resolved set (%d files)"
                              % len(receipt["resolved"]))
    json.dump(receipt, open("results/_r815bmb_resolve.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"resolved": len(receipt["resolved"]),
                      "sides": {s: sum(1 for r in receipt["resolved"]
                                       if r.get("side") == s)
                                for s in ("ours", "theirs")},
                      "asserts": receipt["asserts"]},
                     ensure_ascii=False, indent=1))
    print("RESOLVE OK")


if __name__ == "__main__":
    main()
