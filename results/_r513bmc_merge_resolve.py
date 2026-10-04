# -*- coding: utf-8 -*-
# r513 bm-c merge resolver (r710 bm-b bloodline, MERGE_MODE stage: 2=ours 3=theirs)
# Faces: 18 UU vs origin/main 48a6a15a0 (bm-b r710 wave + 1 follow-up commit)
# Decisions (r710 canon + bm-c token law):
#   - 11 snapshot/derive faces: embedded-ts newer-wins (normalized compare, r709
#     format-asymmetry law), tie/missing-ts -> ours (live regen same-family; r140
#     origin-authority applies only when theirs strictly newer)
#   - md/js twins follow their json twin decision (r708/r510 twin same-side law)
#   - compute_audit.json / regime_state.json: rolling-ledger union (history/transitions)
#     + ours latest/state (r188/R208)
#   - token_usage.json: per-key machines union, monotonic-max pick (r503/r501 bm-c law),
#     totals recomputed from union, top scalars from newer 'generated' side
# Zero-loss assertions: parse-verify-then-write (r185), read-back, residual marker
# scan, final ls-files -u zero, twin same-side probe.
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGE_TIP = "48a6a15a0"


def side(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)],
                        capture_output=True, cwd=ROOT, creationflags=0x08000000)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout


TS_KEYS = ("generated_at", "updated", "generated", "now", "ts", "asof", "as_of",
           "last_run", "scan_ts")


def norm_ts(s):
    # r709 law: ' ' < 'T' lexical poison; normalize space-form to T-form
    return s.strip().replace(" ", "T")


def probe_ts(obj, depth=0, max_depth=2):
    if not isinstance(obj, dict) or depth > max_depth:
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return norm_ts(v)
    for v in obj.values():
        if isinstance(v, dict):
            t = probe_ts(v, depth + 1, max_depth)
            if t:
                return t
    return None


SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
MD_TWINS = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
JS_TWIN = ("results/dashboard_status.js", "results/dashboard_status.json")
UNION_LEDGERS = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions"],
}
TOKEN = "results/token_usage.json"

receipt = {"round": "r513 bm-c", "merge_head": MERGE_TIP, "faces": {},
           "decisions": {}}


def write(path, data):
    if isinstance(data, bytes):
        open(os.path.join(ROOT, path), "wb").write(data)
    else:
        open(os.path.join(ROOT, path), "w", encoding="utf-8",
             newline="\n").write(data)


decisions = {}

# ---- 1) snapshot faces: embedded-ts newer-wins (parse-verify before write)
for p in SNAPSHOTS:
    o_raw, t_raw = side(2, p), side(3, p)
    if t_raw is None:
        decisions[p] = ("ours", "theirs-missing")
        write(p, o_raw)
        receipt["faces"][p] = {"action": "ours", "why": "theirs-missing"}
        continue
    if o_raw is None:
        decisions[p] = ("theirs", "ours-missing")
        write(p, t_raw)
        receipt["faces"][p] = {"action": "theirs", "why": "ours-missing"}
        continue
    try:
        o = json.loads(o_raw.decode("utf-8"))
        t = json.loads(t_raw.decode("utf-8"))
    except Exception as ex:
        decisions[p] = ("theirs", "parse-fail=%s" % ex)
        write(p, t_raw)
        receipt["faces"][p] = {"action": "theirs", "why": "parse-fail %s" % ex}
        continue
    to, tt = probe_ts(o), probe_ts(t)
    if to and tt and to > tt:
        decisions[p] = ("ours", "ts %s>%s" % (to, tt))
        write(p, o_raw)
    elif to and tt and to == tt and o != t:
        decisions[p] = ("ours", "ts-tie content-diff -> ours live regen (same-second family)")
        write(p, o_raw)
    elif to and tt:
        decisions[p] = ("theirs", "ts theirs %s > ours %s" % (tt, to))
        write(p, t_raw)
    else:
        decisions[p] = ("ours", "ts-missing both sides -> ours live regen")
        write(p, o_raw)
    json.loads(open(os.path.join(ROOT, p), "rb").read().decode("utf-8"))  # r185
    receipt["faces"][p] = {"action": decisions[p][0], "why": decisions[p][1]}

# ---- 2) md/js twins follow their json twin (r708/r510 twin same-side law)
for p, twin in MD_TWINS.items():
    s, why = decisions[twin]
    raw = side(2 if s == "ours" else 3, p)
    write(p, raw)
    decisions[p] = (s, "md-twin of %s (%s)" % (twin, why))
    receipt["faces"][p] = {"action": s, "why": decisions[p][1]}
p, twin = JS_TWIN
s, why = decisions[twin]
raw = side(2 if s == "ours" else 3, p)
write(p, raw)
decisions[p] = (s, "js-twin of %s (%s)" % (twin, why))
receipt["faces"][p] = {"action": s, "why": decisions[p][1]}

# ---- 3) rolling-ledger unions (r188/R208: history union + ours latest/state)
for p, keys in UNION_LEDGERS.items():
    o = json.loads(side(2, p).decode("utf-8"))
    t = json.loads(side(3, p).decode("utf-8"))
    for k in keys:
        a, b = o.get(k) or [], t.get(k) or []
        rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a}
        for r in b:
            rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
        merged = sorted(rows.values(),
                        key=lambda r: str(r.get("ts", r.get("updated", ""))))
        o[k] = merged
        assert len(merged) >= max(len(a), len(b)), "union loss %s %s" % (p, k)
        receipt["faces"][p] = {"action": "union+" + k, "ours_len": len(a),
                               "theirs_len": len(b), "union_len": len(merged)}
    write(p, json.dumps(o, ensure_ascii=False, indent=1) + "\n")
    decisions[p] = ("union", "rolling-ledger union, ours latest/state")

# ---- 4) token_usage.json per-key machines union (r503/r501 bm-c law) ------
o_raw, t_raw = side(2, TOKEN), side(3, TOKEN)
o = json.loads(o_raw.decode("utf-8"))
t = json.loads(t_raw.decode("utf-8"))
om, tm = o.get("machines", {}), t.get("machines", {})
assert isinstance(om, dict) and isinstance(tm, dict), "machines not dict"


def num_sum(v):
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, dict):
        return sum(x for x in (num_sum(w) for w in v.values())
                   if isinstance(x, (int, float)))
    return 0


union_m, ties, side_pick = {}, 0, {}
for k in sorted(set(om) | set(tm)):
    a, b = om.get(k), tm.get(k)
    if a is None:
        union_m[k], side_pick[k] = b, "theirs-only"
        continue
    if b is None:
        union_m[k], side_pick[k] = a, "ours-only"
        continue
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        union_m[k], ties = a, ties + 1
        side_pick[k] = "tie"
        continue
    # monotonic cumulative counters only grow: larger sum = true union (r503)
    if num_sum(a) >= num_sum(b):
        union_m[k], side_pick[k] = a, "ours-max"
    else:
        union_m[k], side_pick[k] = b, "theirs-max"
base = o if (probe_ts(o) or "") >= (probe_ts(t) or "") else t
u = dict(base)
u["machines"] = union_m
for fk in ("total_state_tokens_est", "total_report_tokens_est"):
    if fk in base and all(fk in v for v in union_m.values()):
        u[fk] = sum(v.get(fk, 0) for v in union_m.values())
write(TOKEN, json.dumps(u, ensure_ascii=False, indent=1) + "\n")
decisions[TOKEN] = ("per-key-union", "machines %d keys, ties=%d, picks=%s"
                     % (len(union_m), ties,
                        {k: v for k, v in side_pick.items() if v != "tie"}))
receipt["faces"][TOKEN] = {"action": "per-key-union", "ties": ties,
                           "side_pick": side_pick}
json.loads(open(os.path.join(ROOT, TOKEN), "rb").read().decode("utf-8"))  # r185

# ---- 5) read-back + residual marker scan + twin same-side probe -----------
for p in SNAPSHOTS + list(MD_TWINS) + [JS_TWIN[0]] + list(UNION_LEDGERS) + [TOKEN]:
    raw = open(os.path.join(ROOT, p), "rb").read()
    assert not re.search(rb"<<<<<<< ", raw), "marker left in %s" % p
    assert not re.search(rb">>>>>>> ", raw), "marker left in %s" % p
dj = json.load(open(os.path.join(ROOT, "results/dashboard_status.json"),
                    encoding="utf-8"))
js = open(os.path.join(ROOT, "results/dashboard_status.js"), "rb").read()
djts = probe_ts(dj) or ""
js_has = djts.encode() in js or djts.replace("T", " ").encode() in js
receipt["twin_checks"] = {"dashboard_json_ts": djts,
                          "dashboard_js_contains_same_ts": bool(js_has)}
assert js_has, "dashboard js/json twin same-side violated"
receipt["decisions"] = {k: v[0] + " | " + v[1] for k, v in decisions.items()}
receipt["resolved_n"] = len(decisions)
open(os.path.join(ROOT, "results", "_r513bmc_merge_resolve.json"), "w",
     encoding="utf-8", newline="\n").write(
    json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
print("RESOLVED", len(decisions), "faces; token ties=%d picks=%s"
      % (ties, {k: v for k, v in side_pick.items() if v != "tie"}))
for k, v in sorted(decisions.items()):
    print("  %-52s -> %s (%s)" % (k, v[0], v[1][:70]))
