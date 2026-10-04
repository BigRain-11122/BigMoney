# -*- coding: utf-8 -*-
"""r692 bm-a merge resolver: 18 S6 regen faces per-face ts-freshness
(r440/r690 law; blobs via HEAD:/MERGE_HEAD: per r657-2) +
runnable_pool.json per-entry owner_since newer-wins (r474 law; probe
adjudicated: theirs 19:10:12 > ours 18:58:12 on all 3 trio shards,
zero bm-a-unique entries -> theirs wholesale = per-entry max-merge
equivalent) + crash_fuse.json theirs (r687/r690 owner-semantics
precedent; probe: same keyset, 1-byte last-refusal-ts on one sig,
origin wave recorded the later tick) + token_usage.json per-key union
(r456/r466 law, side_pick>0 assert + whole-face ts fallback)."""
import json, re, subprocess, sys, io

CREATE_NO_WINDOW = 0x08000000
TS_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
POOL_FACE = "results/runnable_pool.json"
FUSE_FACE = "results/crash_fuse.json"
TOKEN_FACE = "results/token_usage.json"

TS_RE = re.compile(
    r'"(?:ts|generated|generated_at|asof|now|clock|clock_read|scan_ts|'
    r'updated)"\s*:\s*"?(\d{4}-\d{2}-\d{2})[ T]?(\d{2}:\d{2}:\d{2})')


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    return r.stdout if r.returncode == 0 else None


def best_ts(b):
    if not b:
        return ""
    m = TS_RE.search(b.decode("utf-8", "replace"))
    return (m.group(1) + " " + m.group(2)) if m else ""

log = {"faces": [], "probe": "r692bma_face_probe.py adjudication"}

# --- 17 ts-freshness regen faces ---
for path in TS_FACES:
    ours, theirs = blob("HEAD", path), blob("MERGE_HEAD", path)
    t_ours, t_theirs = best_ts(ours), best_ts(theirs)
    if t_ours and t_theirs:
        pick = "ours" if t_ours >= t_theirs else "theirs"
    else:
        pick = "theirs" if theirs is not None else "ours"
    data = ours if pick == "ours" else theirs
    if data is None:
        print("FATAL: no blob for %s" % path)
        sys.exit(2)
    with io.open(path, "wb") as fh:
        fh.write(data)
    log["faces"].append({"path": path, "pick": pick,
                         "ts_ours": t_ours, "ts_theirs": t_theirs})

# --- runnable_pool.json: per-entry owner_since newer-wins (r474) ---
ours_b, theirs_b = blob("HEAD", POOL_FACE), blob("MERGE_HEAD", POOL_FACE)
o = json.loads(ours_b.decode("utf-8"))
t = json.loads(theirs_b.decode("utf-8"))
oe = {e["id"]: e for e in o.get("entries", [])}
te = {e["id"]: e for e in t.get("entries", [])}
only_ours = sorted(set(oe) - set(te))
newer_ours = 0
newer_theirs = 0
for k in set(oe) & set(te):
    if oe[k] != te[k]:
        for so, st in zip(oe[k].get("shards", []),
                         te[k].get("shards", [])):
            a, b = so.get("owner_since") or "", st.get("owner_since") or ""
            if a and b:
                if a > b:
                    newer_ours += 1
                elif b > a:
                    newer_theirs += 1
# adjudication: zero ours-unique entries and theirs newer on every
# diffing owner_since -> theirs is the per-entry max-merge result
if only_ours or newer_ours > 0:
    print("FATAL: pool face has ours-unique content -- manual per-face "
          "merge required (r474); only_ours=%d newer_ours=%d"
          % (len(only_ours), newer_ours))
    sys.exit(2)
with io.open(POOL_FACE, "wb") as fh:
    fh.write(theirs_b)
log["faces"].append({"path": POOL_FACE, "pick": "theirs",
                     "mode": "per-entry owner_since max-merge "
                             "(r474; zero ours-unique, theirs-newer=%d)"
                     % newer_theirs})

# --- crash_fuse.json theirs (r687/r690 owner-semantics) ---
fuse_t = blob("MERGE_HEAD", FUSE_FACE)
if fuse_t is None:
    print("FATAL: no theirs blob for %s" % FUSE_FACE)
    sys.exit(2)
with io.open(FUSE_FACE, "wb") as fh:
    fh.write(fuse_t)
log["faces"].append({"path": FUSE_FACE, "pick": "theirs",
                     "mode": "owner-semantics (r687/r690 precedent; "
                             "1-byte last-refusal-ts, origin recorded "
                             "the later tick)"})

# --- token_usage.json per-key union (r456/r466) ---
ours_b, theirs_b = blob("HEAD", TOKEN_FACE), blob("MERGE_HEAD", TOKEN_FACE)
tok_log = {"path": TOKEN_FACE, "mode": "per-key-union"}
side_pick = 0
if ours_b is not None and theirs_b is not None:
    try:
        o = json.loads(ours_b.decode("utf-8"))
        t = json.loads(theirs_b.decode("utf-8"))
        o_m, t_m = o.get("machines", {}), t.get("machines", {})
        if o_m or t_m:
            merged = dict(t_m)
            for k, v in o_m.items():
                if k not in merged:
                    merged[k] = v
                    side_pick += 1
                else:
                    ts_o = str(o_m[k].get("ts", "")
                               or o_m[k].get("last_ts", ""))
                    ts_t = str(merged[k].get("ts", "")
                               or merged[k].get("last_ts", ""))
                    if ts_o > ts_t:
                        merged[k] = v
                        side_pick += 1
            o["machines"] = merged
            o["ts"] = max(str(o.get("ts", "")), str(t.get("ts", "")))
            if side_pick == 0:
                t_o, t_t = best_ts(ours_b), best_ts(theirs_b)
                pick = "ours" if t_o >= t_t else "theirs"
                data = ours_b if pick == "ours" else theirs_b
                tok_log["mode"] = "whole-face-fallback:%s" % pick
                side_pick = 1
            else:
                data = json.dumps(o, ensure_ascii=False,
                                  indent=1).encode("utf-8")
            tok_log["side_pick"] = side_pick
        else:
            raise ValueError("no machines dict")
    except Exception as e:
        t_ours, t_theirs = best_ts(ours_b), best_ts(theirs_b)
        pick = "ours" if t_ours >= t_theirs else "theirs"
        data = ours_b if pick == "ours" else theirs_b
        tok_log["mode"] = "whole-face-fallback:%s" % pick
        tok_log["err"] = repr(e)[:100]
        side_pick = 1
else:
    data = theirs_b if theirs_b is not None else ours_b
    tok_log["mode"] = "single-side"
    side_pick = 1
assert side_pick > 0, "token per-key union side_pick=0 without fallback"
with io.open(TOKEN_FACE, "wb") as fh:
    fh.write(data)
log["faces"].append(tok_log)

log["side_pick_ours"] = sum(1 for f in log["faces"]
                           if f.get("pick") == "ours")
log["side_pick_theirs"] = sum(1 for f in log["faces"]
                              if f.get("pick") == "theirs")
assert len(log["faces"]) == len(TS_FACES) + 3, "face coverage incomplete"
with io.open("results/_r692bma_merge_resolve.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
print("resolved %d faces (ours=%d theirs=%d, token=%s)"
      % (len(log["faces"]), log["side_pick_ours"],
         log["side_pick_theirs"], tok_log["mode"]))
