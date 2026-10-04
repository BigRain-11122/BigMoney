# r707 bm-a merge resolver: 35 UU faces vs origin/main (bm-b r705/706 + bm-c r508 waves)
# canon: whole-face ts-newer-wins (checkout --side, byte-exact) / append-only jsonl union (r630)
#        / token per-key max (r466) / crash_fuse per-sig max-merge (r701 lineage, r705 clone)
#        / pool per-entry in-place mutation (r704 aliasing-fix law + MSG-0612)
import subprocess, json, io, sys

def run(args):
    return subprocess.run(args, capture_output=True)

def sh(n, f):
    return run(["git", "show", f":{n}:{f}"]).stdout

def checkout_side(which, files):
    for f in files:
        r = run(["git", "checkout", f"--{which}", f])
        assert r.returncode == 0, (which, f, r.stderr.decode("utf-8", "replace")[:200])
    print(f"whole-face {which}: {len(files)} files")

def w(f, obj):
    with io.open(f, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    json.load(io.open(f, encoding="utf-8"))  # reparse proof

log = []

# ---- 1) whole-face THEIRS (bm-b 02:35-02:45 S6 wave fresher than my dead-session 02:07-02:12) ----
checkout_side("theirs", [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/regime_state.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
])
log.append("theirs: 19 regen faces (bm-b wave 02:35-02:45 > ours 02:07-02:12)")

# ---- 2) whole-face OURS (bm-a 02:10 marks wave > theirs 02:00) ----
checkout_side("ours", [
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
])
log.append("ours: 9 faces (paper marks/t35/export 02:10:41-44 > theirs 02:00:32-40)")

# ---- 3) compute_audit.json: latest theirs-newer (02:35:58>02:07:14) + history ts-union + launches union ----
o = json.loads(sh(2, "results/compute_audit.json")); t = json.loads(sh(3, "results/compute_audit.json"))
assert t["latest"]["ts"] > o["latest"]["ts"], (o["latest"]["ts"], t["latest"]["ts"])
hist = {}
for e in o.get("history", []) + t.get("history", []):
    k = e.get("ts")
    if k not in hist:
        hist[k] = e
merged = sorted(hist.values(), key=lambda e: e.get("ts") or "")
ca = {"latest": t["latest"], "history": merged}
for src in (o, t):
    if isinstance(src.get("launches"), dict):
        ca.setdefault("launches", {}).update(src["launches"])
for k in o:
    if k not in ca and k not in ("latest", "history", "launches"):
        ca[k] = o[k]
w("results/compute_audit.json", ca)
log.append(f"compute_audit: latest=theirs {t['latest']['ts']}; history union {len(o.get('history', []))}+{len(t.get('history', []))}->{len(merged)}; launches union")

# ---- 4) token_usage.json: top theirs-newer (02:39:59>02:11:36) + machines per-key max ----
o = json.loads(sh(2, "results/token_usage.json")); t = json.loads(sh(3, "results/token_usage.json"))
assert t["generated"] > o["generated"], (o["generated"], t["generated"])
base = dict(t)
om, tm = o.get("machines", {}), t.get("machines", {})
for m, b in om.items():
    a = base["machines"].setdefault(m, {})
    for k, v in b.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(a.get(k), (int, float)):
            a[k] = max(a[k], v)
        elif k not in a:
            a[k] = v
w("results/token_usage.json", base)
log.append("token_usage: top=theirs 02:39:59; machines per-key max union (monotone counters)")

# ---- 5) crash_fuse.json: active identical; sigs per-key max-merge; cleared per-key union newer-wins ----
o = json.loads(sh(2, "results/crash_fuse.json")); t = json.loads(sh(3, "results/crash_fuse.json"))
assert o["active"] == t["active"], "active face must be identical"
sigs = dict(o["sigs"])
for k, tv in t["sigs"].items():
    ov = sigs.get(k)
    if ov is None:
        sigs[k] = tv
    else:
        # max-merge: newer last_crash_ts wins, refusals/crashes take the larger count
        pick = ov if (ov.get("last_crash_ts", "") >= tv.get("last_crash_ts", "")) else tv
        for f in ("refusals", "crashes"):
            if isinstance(ov.get(f), int) and isinstance(tv.get(f), int):
                pick[f] = max(ov[f], tv[f])
        # preserve the other side's unique fields
        for f, v in (ov.items() if pick is tv else tv.items()):
            pick.setdefault(f, v)
        sigs[k] = pick
cleared = dict(o["cleared"])
for k, tv in t["cleared"].items():
    ov = cleared.get(k)
    if ov is None or tv.get("cleared_ts", "") >= ov.get("cleared_ts", ""):
        cleared[k] = tv
w("results/crash_fuse.json", {"active": o["active"], "sigs": sigs, "cleared": cleared})
log.append(f"crash_fuse: active identical; sigs per-key max-merge ({len(o['sigs'])}+{len(t['sigs'])}->{len(sigs)}); cleared union newer-wins ({len(o['cleared'])}+{len(t['cleared'])}->{len(cleared)})")

# ---- 6) runnable_pool.json: per-entry max-merge; all differing entries theirs-fresh (verified) ----
o = json.loads(sh(2, "results/runnable_pool.json")); t = json.loads(sh(3, "results/runnable_pool.json"))
oe = {e["id"]: i for i, e in enumerate(o["entries"])}
te = {e["id"]: e for e in t["entries"]}
assert set(oe) == set(te), "entry id set mismatch"
ndiff = 0
for eid, ti in te.items():
    idx = oe[eid]
    if o["entries"][idx] != eid and o["entries"][idx]["id"] != eid:
        continue
    if o["entries"][idx] != ti:
        # newer-wins verification per shard: theirs owner_since/done_at must be >= ours
        for a, b in zip(o["entries"][idx].get("shards", []), ti.get("shards", [])):
            assert b.get("owner_since", "") >= a.get("owner_since", ""), (eid, a, b)
            assert (b.get("done_at") or "") >= (a.get("done_at") or ""), (eid, a, b)
        o["entries"][idx] = ti  # in-place list mutation (r704 aliasing-fix law)
        ndiff += 1
w("results/runnable_pool.json", o)
vm = {x["id"]: x for x in json.load(io.open("results/runnable_pool.json", encoding="utf-8"))["entries"]}
for eid in ("PERPETUAL-N2-W15-JUDGE-SHARD-0", "PERPETUAL-N2-W15-JUDGE-SHARD-1", "PERPETUAL-N2-W15-JUDGE-SHARD-3"):
    assert vm[eid]["shards"][0].get("owner_since") == te[eid]["shards"][0].get("owner_since"), eid + " reverse-read must equal theirs"
log.append(f"runnable_pool: 403 entries, {ndiff} differing taken theirs (in-place mutation + reverse-read assert): trio keepalives + judge shards 0-5")

# ---- 7) jsonl append-only unions (r630, zero-loss both sides) ----
def union_jsonl(path, ts_key_hint=None):
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        raw = fh.read()
    out, state, ours, theirs = [], 0, [], []
    for ln in raw.split("\n"):
        if ln.startswith("<<<<<<<"):
            state = 1; continue
        if ln.startswith("======="):
            state = 2; continue
        if ln.startswith(">>>>>>>"):
            state = 0
            seen = set()
            for l in ours + [x for x in theirs if x not in ours]:
                if l not in seen and l.strip():
                    seen.add(l); out.append(l)
            ours, theirs = [], []
            continue
        if state == 1:
            ours.append(ln)
        elif state == 2:
            theirs.append(ln)
        else:
            out.append(ln)
    merged = "\n".join(out)
    assert "<<<<<<<" not in merged and ">>>>>>>" not in merged, path
    n_ours = len([l for l in sh(2, path).decode("utf-8", "replace").split("\n") if l.strip()])
    n_theirs = len([l for l in sh(3, path).decode("utf-8", "replace").split("\n") if l.strip()])
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(merged)
    body = [l.rstrip("\r") for l in merged.split("\n") if l.strip()]
    oset = {l.rstrip("\r") for l in sh(2, path).decode("utf-8", "replace").split("\n") if l.strip()}
    tset = {l.rstrip("\r") for l in sh(3, path).decode("utf-8", "replace").split("\n") if l.strip()}
    assert oset <= set(body) and tset <= set(body), path + " zero-loss assertion"
    return n_ours, n_theirs, len(body)

for p in ("results/pool_core_samples.jsonl", "results/pool_red_flags.jsonl", "results/x2_watch_log.jsonl"):
    a, b, c = union_jsonl(p)
    log.append(f"{p}: union ours {a} + theirs {b} -> {c} lines (zero-loss assert PASS)")

print("\n".join(log))
print("ALL RESOLVED")
