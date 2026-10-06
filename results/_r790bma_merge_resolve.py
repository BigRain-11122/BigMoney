# -*- coding: utf-8 -*-
"""r790 bm-a close-window merge resolver -- 24-UU per-face empirical resolution
(r773 per-face ts law; r756 ts-normalize; r515 stage-sourced python-bytes;
r704 readback; r708 md-twins-lock-json-side; r758 x2 union ts-sort;
r516-3 token per-key union; r701 CODELY manual memory-union chron order).
Ours S6 regen 19:01-19:03 vs bm-c r636 S6 ~18:4x-18:5x -- per-face probe decides.
Receipt -> results/_r790bma_merge_resolve.json"""
import subprocess, json, io, re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def stage(s, p):
    r = subprocess.run(["git", "show", ":%d:%s" % (s, p)], capture_output=True)
    assert r.returncode == 0, "stage read fail " + p
    assert len(r.stdout) > 30, "stage blob suspiciously small " + p
    return r.stdout

def pick_ts(d):
    for k in ("ts", "generated", "generated_at", "asof", "updated"):
        v = d.get(k)
        if isinstance(v, str):
            return v
    # nested probes
    for path in (("latest", "generated"), ("latest", "ts"), ("meta", "generated")):
        cur = d
        try:
            for k in path: cur = cur[k]
            if isinstance(cur, str): return cur
        except Exception: pass
    return ""

def norm(s):
    return s.replace(" ", "T") if s else ""

receipt = {"window": "r790 bm-a close merge 24-UU", "faces": {}}
decisions = []

# ---- 1. CODELY.md manual memory-union (r701 precedent; theirs 2 new lines before our r790 line) ----
p = "CODELY.md"
o = stage(2, p).decode("utf-8"); t = stage(3, p).decode("utf-8")
ol, tl = o.splitlines(), t.splitlines()
oset, tset = set(ol), set(tl)
only_t = [l for l in tl if l not in oset and l.strip()]
only_o = [l for l in ol if l not in tset and l.strip()]
assert len(only_t) == 2 and len(only_o) == 1, (len(only_t), len(only_o))
r790_line = only_o[0]
out = o.replace(r790_line, "\n".join(only_t) + "\n" + r790_line, 1)
for l in only_t + [r790_line]:
    assert l in out, "union lost line"
io.open(p, "w", encoding="utf-8", newline="").write(out)
subprocess.run(["git", "add", p], capture_output=True)
receipt["faces"][p] = {"mode": "memory-union", "theirs_new": len(only_t), "ours_new": len(only_o)}
decisions.append((p, "memory-union", "theirs r636 x2 + ours r790 x1, chronological"))

# ---- 2. x2_watch_log.jsonl append-only union + ts sort (r758) ----
p = "results/x2_watch_log.jsonl"
o_txt = stage(2, p).decode("utf-8"); t_txt = stage(3, p).decode("utf-8")
o_lines, t_lines = o_txt.splitlines(), t_txt.splitlines()
seen, merged = set(), []
for l in o_lines + t_lines:
    if l.strip() and l not in seen:
        seen.add(l); merged.append(l)
def line_ts(l):
    m = re.search(r"2026-10-0\d[T ]\d\d:\d\d:\d\d", l)
    return norm(m.group(0)) if m else ""
merged.sort(key=line_ts)
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(merged) + ("\n" if merged else ""))
subprocess.run(["git", "add", p], capture_output=True)
receipt["faces"][p] = {"mode": "union-ts-sort", "ours": len(o_lines), "theirs": len(t_lines), "merged": len(merged)}
decisions.append((p, "union-ts-sort", "ours=%d theirs=%d -> merged=%d" % (len(o_lines), len(t_lines), len(merged))))

# ---- 3. token_usage.json per-key union by generated ts (r516-3 / r703) ----
p = "results/token_usage.json"
o = json.loads(stage(2, p).decode("utf-8")); t = json.loads(stage(3, p).decode("utf-8"))
merged, picks = {}, {"ours": 0, "theirs": 0}
for k in set(list(o.keys()) + list(t.keys())):
    ov, tv = o.get(k), t.get(k)
    if isinstance(ov, dict) and isinstance(tv, dict):
        og, tg = str(ov.get("generated", "")), str(tv.get("generated", ""))
        if og >= tg: merged[k] = ov; picks["ours"] += 1
        else: merged[k] = tv; picks["theirs"] += 1
    elif ov is not None and tv is None: merged[k] = ov; picks["ours"] += 1
    elif tv is not None and ov is None: merged[k] = tv; picks["theirs"] += 1
    else: merged[k] = ov; picks["ours"] += 1
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
subprocess.run(["git", "add", p], capture_output=True)
receipt["faces"][p] = {"mode": "per-key-union", "keys": len(merged), "picks": picks}
decisions.append((p, "per-key-union", "keys=%d picks=%s" % (len(merged), picks)))

# ---- 4. snapshot JSON faces: per-face ts take-newer (r756 normalize) ----
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
side_of = {}
for p in SNAP:
    ob, tb = stage(2, p), stage(3, p)
    try:
        to = norm(pick_ts(json.loads(ob.decode("utf-8"))))
        tt = norm(pick_ts(json.loads(tb.decode("utf-8"))))
    except Exception:
        to, tt = "", ""
    side = "ours" if to >= tt else "theirs"   # ties -> ours (host bm-a fresh S6)
    blob = ob if side == "ours" else tb
    # readback: reparse assertion (r704)
    json.loads(blob.decode("utf-8"))
    io.open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], capture_output=True)
    side_of[p] = side
    receipt["faces"][p] = {"mode": "take-newer", "ours_ts": to, "theirs_ts": tt, "side": side}
    decisions.append((p, "take-newer", "ours=%s theirs=%s -> %s" % (to or "NOTS", tt or "NOTS", side)))

# ---- 5. md twins locked to json twin side (r708) ----
TWINS = {
    "docs/daily_report/REPORT-2026-10-06.md": "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md": "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
for p, twin in TWINS.items():
    side = side_of[twin]
    blob = stage(2, p) if side == "ours" else stage(3, p)
    io.open(p, "wb").write(blob)
    subprocess.run(["git", "add", p], capture_output=True)
    receipt["faces"][p] = {"mode": "twin-lock", "side": side, "twin": twin}
    decisions.append((p, "twin-lock", "locked to %s side=%s" % (twin, side)))

# ---- 6. marker scan over ALL resolved faces (r503 head-anchor; r609-3 real-marker
# semantics: line-start anchored only -- prose quotes of marker strings are false positives) ----
allf = ["CODELY.md", "results/x2_watch_log.jsonl", "results/token_usage.json"] + SNAP + list(TWINS.keys())
for p in allf:
    for l in io.open(p, encoding="utf-8", newline="").read().splitlines():
        assert not (l.startswith("<<<<<<< ") or l.startswith(">>>>>>> ") or l == "======="), \
            "REAL conflict marker at line start in %s: %r" % (p, l[:40])

receipt["resolved"] = len(allf)
receipt["decisions"] = decisions
receipt["verdict"] = "24/24 faces resolved (1 memory-union + 1 union-ts-sort + 1 per-key-union + 18 take-newer + 3 twin-lock), marker scan CLEAN"
json.dump(receipt, io.open("results/_r790bma_merge_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
subprocess.run(["git", "add", "results/_r790bma_merge_resolve.json"], capture_output=True)
print(receipt["verdict"])
for d in decisions: print(" ", d)
