#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r813 bm-b rebase-conflict resolver (canonical recipes, bigmoney-conflict-resolve SKILL).

Context: r812 session (bm-b) died mid `git pull --rebase` push-rejection collision with
bm-c tip 6ab22b1a9 (bm-c claimed T-180 at 03:04:04; bm-b work commit ac495a6fb at 03:08:06
= later => bm-b yields claim per fleet/README.md SS4 commit-time law; artifacts kept in-tree
per r394 anti-double-burn purpose, yield documented in round report + inbox MSG).
Rebase state: stopped at `pick ac495a6fb`, conflict set = 15 files (both-sides touched).
Ours (stage-2 / HEAD during rebase) = 6ab22b1a9 (bm-c tip). Theirs = ac495a6fb (r812 bm-b).

Recipes (classify_conflicts.py + SKILL.md manual classification for UNKNOWN entries):
  rolling-ledger  compute_audit.json    union history by ts, take-new latest (r188/R208)
  rolling-ledger  regime_state.json     union transitions/history by asof, take-new state (R208)
  snapshot x7      *_status/attrition/token/fundamental      take-new by ts (R208/R216)
  twin-pair x4+2   docs/daily_report + docs/live_usage     atomic take-side by generated ts
  ticket x1        fleet/tasks/T-2026-10-10-180-P1.json    take ours whole (bm-b yields claim, SS4)
Laws kept: r185 parse-verify before write-back+add; r140 same-second tie -> HEAD(ours);
zero-loss union assertion; write-back mirrors blob bytes (take-side) / producer format (union).
"""
import json, subprocess, sys, os, re

OURS = "6ab22b1a9"
THEIRS = "ac495a6fb"

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"blob fail {rev}:{path}: {r.stderr[:200]}")
    return r.stdout

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

def ts_of(d, *keys):
    for k in keys:
        if k in d:
            return d[k]
    return ""

SNAP_TS_KEY = {
    "results/futures_update_status.json": "ts",
    "results/lhb_update_status.json": "updated",
    "results/fundamental_b_layer_filter.json": "updated",
    "results/token_usage.json": "generated",
    "results/update_status.json": "updated",
    "results/_attrition_guard_scan.json": "ts",
}

TAKE_SIDE_PAIRS = {  # json probe file -> (ts key, twin .md mirrors)
    "docs/daily_report/REPORT-2026-10-10.json": ("generated_at", ["docs/daily_report/REPORT-2026-10-10.md"]),
    "docs/live_usage/LIVE-2026-10-10.json": ("generated", ["docs/live_usage/LIVE-2026-10-10.md"]),
    "docs/live_usage/LIVE-latest.json": ("generated", ["docs/live_usage/LIVE-latest.md"]),
}

TAKE_OURS = ["fleet/tasks/T-2026-10-10-180-P1.json"]  # bm-b yields claim (SS4 commit-time law)

def main():
    receipt = {"resolver": "results/_r813bmb_resolve.py", "ours": OURS, "theirs": THEIRS,
               "rebased_commit": "ac495a6fb (r812 bm-b, author 03:08:06)",
               "resolved": [], "asserts": []}
    # 1) snapshots: take-new by ts
    for p, k in SNAP_TS_KEY.items():
        o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
        side = "theirs" if str(ts_of(t, k)) >= str(ts_of(o, k)) else "ours"
        win = t if side == "theirs" else o
        b = blob(THEIRS if side == "theirs" else OURS, p)
        open(p, "wb").write(b)
        json.loads(open(p, "rb").read())  # r185 parse-verify
        receipt["resolved"].append({"path": p, "recipe": "snapshot-take-new", "ts_key": k,
                                    "side": side, "ts_win": ts_of(win, k)})
    # 2) twin pairs: atomic side choice by generated ts, mirror .md twin
    for p, (k, twins) in TAKE_SIDE_PAIRS.items():
        o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
        side = "theirs" if str(ts_of(t, k)) >= str(ts_of(o, k)) else "ours"
        src = THEIRS if side == "theirs" else OURS
        open(p, "wb").write(blob(src, p))
        json.loads(open(p, "rb").read())
        receipt["resolved"].append({"path": p, "recipe": "twin-atomic-take-side", "side": side})
        for tw in twins:
            open(tw, "wb").write(blob(src, tw))
            receipt["resolved"].append({"path": tw, "recipe": "twin-mirror", "side": side})
    # 3) ticket: bm-b yields claim -> take ours whole (SS4)
    for p in TAKE_OURS:
        b = blob(OURS, p)
        open(p, "wb").write(b)
        d = json.loads(open(p, "rb").read())
        receipt["resolved"].append({"path": p, "recipe": "yield-claim-take-ours",
                                    "status_now": d.get("status"), "claimed_by": d.get("claimed_by")})
        receipt["asserts"].append("%s: bm-b yielded claim to %s (commit-time SS4: bm-c 03:04:04 < bm-b 03:08:06)" % (p, d.get("claimed_by")))
    # 4) compute_audit.json: rolling-ledger union history by ts + take-new latest
    p = "results/compute_audit.json"
    o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
    merged = {}
    for e in o["history"] + t["history"]:
        if e["ts"] not in merged:          # r140 same-ts tie -> HEAD/ours (ours iterated first)
            merged[e["ts"]] = e
    hist = sorted(merged.values(), key=lambda e: e["ts"])
    latest = t["latest"] if str(ts_of(t["latest"], "ts")) >= str(ts_of(o["latest"], "ts")) else o["latest"]
    out = {"latest": latest, "history": hist}
    open(p, "wb").write(dump_like(out, fmt_probe(blob(OURS, p))))
    v = json.loads(open(p, "rb").read())
    exp = len({e["ts"] for e in o["history"]} | {e["ts"] for e in t["history"]})
    assert len(v["history"]) == exp, "union loss: %d != %d" % (len(v["history"]), exp)
    receipt["resolved"].append({"path": p, "recipe": "rolling-ledger-union", "ours_hist": len(o["history"]),
                                "theirs_hist": len(t["history"]), "union": exp,
                                "latest_side": "theirs" if latest == t["latest"] else "ours"})
    receipt["asserts"].append("compute_audit union zero-loss: |A U B| = %d rows asserted" % exp)
    # 5) regime_state.json: union transitions/history by asof + take-new state fields
    p = "results/regime_state.json"
    o, t = json.loads(blob(OURS, p)), json.loads(blob(THEIRS, p))
    out = dict(o)
    if str(t.get("updated", "")) >= str(o.get("updated", "")):
        for k, val in t.items():
            if not isinstance(val, list):
                out[k] = val
    hmap = {}
    for e in o.get("history", []) + t.get("history", []):
        if e.get("asof") not in hmap:      # r140 same-key tie -> ours first
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
    exp_h = len({e.get("asof") for e in o.get("history", [])} | {e.get("asof") for e in t.get("history", [])})
    assert len(v["history"]) == exp_h, "regime history union loss %d != %d" % (len(v["history"]), exp_h)
    receipt["resolved"].append({"path": p, "recipe": "rolling-ledger-union+take-new-state",
                                "history_union": exp_h, "transitions_union": len(out["transitions"]),
                                "state_side": "theirs" if out.get("updated") == t.get("updated") else "ours"})
    receipt["asserts"].append("regime_state union zero-loss: history |A U B| = %d" % exp_h)
    # 6) git add resolved set
    add = [r["path"] for r in receipt["resolved"]]
    subprocess.run(["git", "add", "--"] + add, check=True)
    # final sweep: no conflict markers anywhere in resolved set
    marker = re.compile(rb"^(<<<<<<< |>>>>>>> |=======$)", re.M)
    bad = []
    for r in receipt["resolved"]:
        b = open(r["path"], "rb").read()
        if marker.search(b):
            bad.append(r["path"])
    assert not bad, "markers remain: %s" % bad
    receipt["asserts"].append("marker sweep: 0 conflict markers in resolved set")
    json.dump(receipt, open("results/_r813bmb_resolve.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    print("RESOLVE OK")

if __name__ == "__main__":
    main()
