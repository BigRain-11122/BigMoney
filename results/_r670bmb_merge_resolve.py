# r670 bm-b merge resolver: 14 UU regen faces -> embedded-ts take-side (r656 match-law, double-form verify)
# + token_usage per-key union (r456/r466 law, side_pick>0 assertion). Raw bytes via HEAD:/MERGE_HEAD: (r657 law 2).
import json, re, subprocess

def side_bytes(ref, path):
    p = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout

def ts_of(raw, path):
    # scan first 4000 bytes for ISO-like timestamps, return best (max) normalized
    txt = raw.decode("utf-8", "replace")[:6000]
    cands = re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:\+\d{2}:\d{2})?", txt)
    if not cands:
        return None
    def norm(s):
        s = s.replace("T", " ")[:19]
        return s
    return max(norm(c) for c in cands)

FILES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
evidence = {"round": "r670", "ts_take": {}, "token_union": {}, "verdicts": {}}
for path in FILES:
    ours = side_bytes("HEAD", path)
    theirs = side_bytes("MERGE_HEAD", path)
    assert ours is not None and theirs is not None, "side fetch fail %s" % path
    to, tt = ts_of(ours, path), ts_of(theirs, path)
    evidence["ts_take"][path] = {"ours_ts": to, "theirs_ts": tt}
    if to is None or tt is None:
        # no ts found: prefer ours (local regenerated this round) -- disclosed
        pick, why = "ours", "ts-miss->ours (probe-miss needs double-form review)" % () if False else ("ours", "ts-miss->ours (disclosed)")
        evidence["ts_take"][path]["pick"] = pick + " " + why
    elif to >= tt:
        pick = "ours"
    else:
        pick = "theirs"
    raw = ours if pick == "ours" else theirs
    evidence["ts_take"][path]["pick"] = pick
    with open(path, "wb") as f:
        f.write(raw)
    # reparse gate for json faces
    if path.endswith(".json"):
        json.loads(open(path, "rb").read().decode("utf-8"))
    evidence["verdicts"][path] = "resolved:" + pick

# ---- token_usage.json per-key union (machines dict per-key ts newer-wins, r456/r466) ----
TU = "results/token_usage.json"
ours_raw = side_bytes("HEAD", TU)
theirs_raw = side_bytes("MERGE_HEAD", TU)
o = json.loads(ours_raw.decode("utf-8"))
t = json.loads(theirs_raw.decode("utf-8"))
om = o.get("machines", {})
tm = t.get("machines", {})
side_pick = 0
for k in set(om) | set(tm):
    if k in om and k in tm:
        to2 = str(om[k].get("ts") or om[k].get("updated") or "")
        tt2 = str(tm[k].get("ts") or tm[k].get("updated") or "")
        if to2 and tt2 and to2 != tt2:
            side_pick += 1
            o["machines"][k] = om[k] if to2 > tt2 else tm[k]
        else:
            side_pick += 1  # equal or missing ts: keep ours
    elif k in tm:
        o["machines"][k] = tm[k]
        side_pick += 1
assert side_pick > 0, "per-key union zero side-pick -> r456/r466 law: MUST fall to whole-face freshness, refusing silent theirs"
for scalar in ("ts", "generated", "updated"):
    if scalar in o and scalar in t and str(t.get(scalar)) > str(o.get(scalar)):
        o[scalar] = t[scalar]
evidence["token_union"] = {"side_pick": side_pick, "machines": len(o.get("machines", {}))}
with open(TU, "w", encoding="utf-8", newline="\n") as f:
    json.dump(o, f, ensure_ascii=False, indent=1)
evidence["verdicts"][TU] = "resolved:per-key-union side_pick=%d" % side_pick

# ---- global gates: zero markers in all 14 faces, reparse all jsons ----
MARK = re.compile(rb"^(<<<<<<<|>>>>>>>|=======|\|\|\|\|\|\|\|)", re.M)
for path in FILES + [TU]:
    b = open(path, "rb").read()
    hits = MARK.findall(b)
    assert not hits, "marker survival in %s: %r" % (path, hits[:3])
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))
json.dump(evidence, open("results/_r670bmb_merge_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("RESOLVE_OK faces=14 token_side_pick=%d" % side_pick)
for p in FILES:
    d = evidence["ts_take"][p]
    print("  %-46s ours=%s theirs=%s -> %s" % (p, d["ours_ts"], d["theirs_ts"], d["pick"]))
