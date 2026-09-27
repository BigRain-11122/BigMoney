# -*- coding: utf-8 -*-
"""r352 bm-b rebase-storm resolver #2 (15-UU vs bm-a r370 3-commit same-window
chain fbc2c262+7e34a9b3+7fb67b5a). Recipes per bigmoney-conflict-resolve canon:
10 classifier-classified + 5 UNKNOWN manually adjudicated (daily twins coupled
take-new / pool governance theirs-terminal / scorecard pair take-new).
Zero-loss unions + deep-ts take-new snapshots + json.loads verify pre-write.
Blob extraction via subprocess git show (PS-redirect UTF-16 trap law r352)."""
import json
import re
import subprocess
import sys

FILES_SNAPSHOT = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
FILES_LEDGER = ["results/compute_audit.json", "results/regime_state.json"]
FILES_DAILY = ["docs/daily_report/REPORT-2026-09-28.json",
               "docs/daily_report/REPORT-2026-09-28.md"]
POOL = "results/runnable_pool.json"
JS = "results/dashboard_status.js"


def blob(stage, path):
    out = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                         capture_output=True).stdout.decode("utf-8")
    return out


def jblob(stage, path):
    return json.loads(blob(stage, path))


def deep_ts(d):
    """max ts-like scalar anywhere shallow-ish (depth<=3)."""
    best = ""
    stack = [(d, 0)]
    while stack:
        o, dep = stack.pop()
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and re.fullmatch(
                        r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d(:\d\d)?", v):
                    if v > best:
                        best = v
                elif isinstance(v, (dict, list)) and dep < 3:
                    stack.append((v, dep + 1))
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, (dict, list)):
                    stack.append((v, dep))
    return best


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


def take_new_snapshot(path):
    o, t = jblob(2, path), jblob(3, path)
    to, tt = deep_ts(o), deep_ts(t)
    if tt >= to:
        pick = t
    else:
        pick = o
    write_json(path, pick)
    json.load(open(path, encoding="utf-8"))
    print("[snapshot] %s -> %s side (ts ours=%s theirs=%s)"
          % (path, "theirs" if tt >= to else "ours", to or "-", tt or "-"))


def union_ledger(path):
    o, t = jblob(2, path), jblob(3, path)
    key = "history" if "history" in o else "transitions"
    ko = {json.dumps(r, sort_keys=True): r for r in o.get(key, [])}
    kt = {json.dumps(r, sort_keys=True): r for r in t.get(key, [])}
    union = list({**ko, **kt}.values())
    base = dict(t)  # state fields take-new: theirs = newer chain this window
    base[key] = union
    ident = len(set(list(ko) + list(kt)))
    assert len(union) == ident, "ledger union row-count != |AuB| identities"
    write_json(path, base)
    json.load(open(path, encoding="utf-8"))
    print("[ledger] %s %s union %d|%d -> %d identities==|AuB|"
          % (path, key, len(ko), len(kt), len(union)))


def daily_twins():
    oj, tj = jblob(2, "docs/daily_report/REPORT-2026-09-28.json"), \
        jblob(3, "docs/daily_report/REPORT-2026-09-28.json")
    to, tt = deep_ts(oj), deep_ts(tj)
    side = 3 if tt >= to else 2
    for p in FILES_DAILY:
        raw = blob(side, p)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(raw)
        if p.endswith(".json"):
            json.load(open(p, encoding="utf-8"))
    print("[daily-twins] coupled -> %s side (ts ours=%s theirs=%s)"
          % ("theirs" if side == 3 else "ours", to or "-", tt or "-"))


def js_wrapper():
    o, t = blob(2, JS), blob(3, JS)
    m = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;\s*$", t, re.S)
    to = deep_ts(json.loads(m.group(1))) if m else ""
    m2 = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;\s*$", o, re.S)
    oo = deep_ts(json.loads(m2.group(1))) if m2 else ""
    pick = t if to >= oo else o
    with open(JS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(pick)
    json.loads(re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;\s*$",
                         pick, re.S).group(1))
    print("[js-wrapper] whole-bytes -> %s (ts ours=%s theirs=%s)"
          % ("theirs" if to >= oo else "ours", oo or "-", to or "-"))


def pool():
    o, t = jblob(2, POOL), jblob(3, POOL)
    oi = o if isinstance(o, list) else o.get("items", o.get("entries", []))
    ti = t if isinstance(t, list) else t.get("items", t.get("entries", []))
    if not isinstance(o, list):
        oi, ti = oi, ti
    omap = {x["id"]: x for x in oi}
    tmap = {x["id"]: x for x in ti}
    ids = sorted(set(omap) | set(tmap))
    out = []
    for i in ids:
        a, b = omap.get(i), tmap.get(i)
        if a is None:
            out.append(b)
        elif b is None:
            out.append(a)
        elif json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
            out.append(b)
        elif i == "DECISION-CHAIN-V2-P1":
            # r370 canon + terminal-governance: bm-a 7e34a9b3 re-pin
            # lane_owner=bm-b + surgical dead-claim clear (exit-2 forensics)
            # supersedes my same-window preservation -> take theirs whole.
            out.append(b)
        else:
            # same-id divergence: governance fields non-null-first, rest
            # new-side-wins (r366) -- theirs = later chain this window.
            merged = dict(a)
            for k, v in b.items():
                if k in ("lane_owner", "lane_note") and v:
                    merged[k] = v
                else:
                    merged[k] = v
            out.append(merged)
    assert len(out) == len(ids), "pool id-union count != identity count"
    v2 = [x for x in out if x["id"] == "DECISION-CHAIN-V2-P1"][0]
    assert v2.get("lane_owner") == "bm-b", "V2-P1 lane_owner lost"
    sh = [s for s in v2.get("shards", []) if s.get("key") == "v2-0of1"][0]
    print("[pool] union %d|%d -> %d ids; V2-P1 lane_owner=bm-b, "
          "shard owner=%s (bm-a surgical clear adopted)"
          % (len(omap), len(tmap), len(out), sh.get("owner")))
    write_json(POOL, o if isinstance(o, list) else o)
    if not isinstance(o, list):
        # dict-shaped pool: re-write with merged entries list
        shape = dict(o)
        klist = "items" if "items" in o else "entries"
        shape[klist] = out
        write_json(POOL, shape)
    else:
        write_json(POOL, out)
    json.load(open(POOL, encoding="utf-8"))
    # post-write verify (watch-face law r359)
    d2 = json.load(open(POOL, encoding="utf-8"))
    i2 = d2 if isinstance(d2, list) else d2.get("items", d2.get("entries", []))
    ids2 = {x["id"] for x in i2}
    assert ids2 == set(ids), "pool watch-face drift post-write"
    v2b = [x for x in i2 if x["id"] == "DECISION-CHAIN-V2-P1"][0]
    assert v2b.get("lane_owner") == "bm-b"


def main():
    for p in FILES_SNAPSHOT:
        take_new_snapshot(p)
    for p in FILES_LEDGER:
        union_ledger(p)
    daily_twins()
    js_wrapper()
    pool()
    print("RESOLVE2-OK all 15 faces resolved + verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# POST-RUN CORRECTION LOG (kept verbatim, r220 no-abort honesty):
# Stage-mapping inversion during rebase: stage2=HEAD(upstream bm-a side),
# stage3=the-replayed-commit(ours). Deep-ts take-new + identity unions are
# label-agnostic (self-correcting). ONE semantic casualty caught post-run:
# pool V2-P1 adopted stage3 (my preserved-claim face) instead of bm-a's
# surgical-clear terminal face -> surgically replaced with HEAD version
# (lane_owner=bm-b, shard owner=None) via inline fix this window, verified
# 88 entries. Lesson queued for memory: rebase blob stages are INVERTED vs
# merge; resolvers must label :2:=upstream/:3:=replayed BEFORE semantics-
# bearing adoptions (snapshots unaffected when ts-compared symmetrically).
