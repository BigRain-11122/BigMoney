# -*- coding: utf-8 -*-
"""r790 bm-a merge-resolver CONTINUATION (r611-3 mid-crash recovery: run-1
completed all adds, stages collapsed; this leg re-derives nothing, verifies
the staged :0: faces -- per-face ts readback vs HEAD/MERGE_HEAD sides,
real-marker line-start scan, union integrity assertions -- and writes the
receipt. Zero replay of the resolution writes themselves."""
import subprocess, json, io, re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def rev_blob(rev, p):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, p)], capture_output=True)
    return r.stdout if r.returncode == 0 else b""

def pick_ts(d):
    for k in ("ts", "generated", "generated_at", "asof", "updated"):
        v = d.get(k)
        if isinstance(v, str): return v
    for path in (("latest", "generated"), ("latest", "ts"), ("meta", "generated")):
        cur = d
        try:
            for k in path: cur = cur[k]
            if isinstance(cur, str): return cur
        except Exception: pass
    return ""

def norm(s): return s.replace(" ", "T") if s else ""

SNAP = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
TWINS = {
    "docs/daily_report/REPORT-2026-10-06.md": "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md": "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
receipt = {"window": "r790 bm-a close merge 24-UU (continuation leg r611-3)", "faces": {}, "verdict": None}
ok = 0

# 1. snapshot faces: staged :0: == one of the two sides, and it is the NEWER side
for p in SNAP:
    z = rev_blob(":0", p)
    assert len(z) > 30, "empty index blob " + p
    j = json.loads(z.decode("utf-8"))            # reparse gate
    tz = norm(pick_ts(j))
    oh = rev_blob("HEAD", p); mh = rev_blob("MERGE_HEAD", p)
    to = norm(pick_ts(json.loads(oh.decode("utf-8")))) if oh else ""
    tt = norm(pick_ts(json.loads(mh.decode("utf-8")))) if mh else ""
    expected = "ours" if to >= tt else "theirs"
    same_ours = (z == oh); same_theirs = (z == mh)
    assert same_ours or same_theirs, "staged %s matches neither side" % p
    side = "ours" if same_ours else "theirs"
    assert side == expected, "%s side=%s but ts-law expects %s (ours=%s theirs=%s)" % (p, side, expected, to, tt)
    receipt["faces"][p] = {"mode": "take-newer", "side": side, "staged_ts": tz,
                           "ours_ts": to, "theirs_ts": tt, "readback": "ok"}
    ok += 1

# 2. md twins: staged bytes == same-side twin's source side
for p, twin in TWINS.items():
    z = rev_blob(":0", p); oh = rev_blob("HEAD", p); mh = rev_blob("MERGE_HEAD", p)
    side = "ours" if z == oh else ("theirs" if z == mh else "MISMATCH")
    twin_side = receipt["faces"][twin]["side"]
    assert side == twin_side, "%s twin side %s != json side %s" % (p, side, twin_side)
    receipt["faces"][p] = {"mode": "twin-lock", "side": side, "twin": twin}
    ok += 1

# 3. token_usage.json: per-key union integrity -- every key from both sides present,
#    each staged key equals the newer-generated side
p = "results/token_usage.json"
z = json.loads(rev_blob(":0", p).decode("utf-8"))
o = json.loads(rev_blob("HEAD", p).decode("utf-8"))
t = json.loads(rev_blob("MERGE_HEAD", p).decode("utf-8"))
assert set(z.keys()) == set(list(o.keys()) + list(t.keys())), "token union key loss"
for k in z:
    ov, tv = o.get(k), t.get(k)
    if isinstance(ov, dict) and isinstance(tv, dict):
        expect = ov if str(ov.get("generated", "")) >= str(tv.get("generated", "")) else tv
        assert z[k] == expect, "token key %s not newer-side" % k
receipt["faces"][p] = {"mode": "per-key-union", "keys": len(z),
                       "ours_keys": len(o), "theirs_keys": len(t)}
ok += 1

# 4. x2_watch_log: union integrity -- merged = dedup(ours+theirs), ts-sorted
p = "results/x2_watch_log.jsonl"
z_lines = [l for l in rev_blob(":0", p).decode("utf-8").splitlines() if l.strip()]
o_lines = [l for l in rev_blob("HEAD", p).decode("utf-8").splitlines() if l.strip()]
t_lines = [l for l in rev_blob("MERGE_HEAD", p).decode("utf-8").splitlines() if l.strip()]
expect_set = set(o_lines) | set(t_lines)
assert set(z_lines) == expect_set, "x2 union line loss/gain"
assert len(z_lines) == len(expect_set), "x2 dup residue"
def line_ts(l):
    m = re.search(r"2026-10-0\d[T ]\d\d:\d\d:\d\d", l)
    return norm(m.group(0)) if m else ""
assert z_lines == sorted(z_lines, key=line_ts), "x2 ts order violated"
receipt["faces"][p] = {"mode": "union-ts-sort", "ours": len(o_lines), "theirs": len(t_lines), "merged": len(z_lines)}
ok += 1

# 5. CODELY.md memory-union integrity: both theirs-new lines + our r790 line present,
#    exactly once each; no side's entry lost
p = "CODELY.md"
z_txt = rev_blob(":0", p).decode("utf-8")
o_txt = rev_blob("HEAD", p).decode("utf-8"); t_txt = rev_blob("MERGE_HEAD", p).decode("utf-8")
o_set, t_set = set(o_txt.splitlines()), set(t_txt.splitlines())
only_t = [l for l in t_txt.splitlines() if l not in o_set and l.strip()]
only_o = [l for l in o_txt.splitlines() if l not in t_set and l.strip()]
assert len(only_t) == 2 and len(only_o) == 1, ("new-line sets drifted", len(only_t), len(only_o))
z_lines = z_txt.splitlines()
for l in only_t + only_o:
    assert z_lines.count(l) == 1, "CODELY union line count != 1: " + l[:60]
receipt["faces"][p] = {"mode": "memory-union", "theirs_new": len(only_t), "ours_new": len(only_o)}
ok += 1

# 6. real-marker scan (line-start anchored, r609-3 prose-quote false-positive law)
for p in ["CODELY.md", "results/x2_watch_log.jsonl", "results/token_usage.json"] + SNAP + list(TWINS.keys()):
    for l in rev_blob(":0", p).decode("utf-8", "replace").splitlines():
        assert not (l.startswith("<<<<<<< ") or l.startswith(">>>>>>> ") or l == "======="), \
            "REAL marker line-start in %s: %r" % (p, l[:40])

receipt["resolved_verified"] = ok
receipt["verdict"] = ("24/24 staged faces verified via :0: readback (18 take-newer ts-law + 3 twin-lock + "
                      "token per-key union + x2 union-ts-sort + CODELY memory-union); real-marker scan CLEAN; "
                      "stages collapsed in run-1 per r611-1, continuation per r611-3 zero-replay")
json.dump(receipt, io.open("results/_r790bma_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
subprocess.run(["git", "add", "results/_r790bma_merge_resolve.json"], capture_output=True)
print("CONTINUATION VERIFY: %d/24 faces OK, receipt written" % ok)
for k, v in receipt["faces"].items():
    print(" ", k, v.get("mode"), v.get("side", ""), "ts=%s" % v.get("staged_ts", v.get("merged", "")))
