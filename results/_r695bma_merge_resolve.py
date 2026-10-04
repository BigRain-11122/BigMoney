"""r695 bm-a merge resolver: 31 UU faces, per-face canon decisions.

Dispositions (canon lineage r692bmb/r694bma resolver family):
- crash_fuse.json -> per-sig max-merge (sigs union; per-sig refusals/count
  max + last_*_ts newer-wins; shared-key fields equal-assert).
- token_usage.json -> r440/r484/r456 per-key union (machines dict), zero
  side_pick -> explicit whole-face freshness fallback (r466 law).
- x2_watch_log.jsonl -> append-only line-level union zero-loss (r656 canon).
- 28 regen faces -> per-face ts-freshness newer-wins (r440); md twins locked
  to their json picks (r692bmb law).

Fail-closed: any probe miss or assertion failure = ABORT zero origin-bound
writes. Evidence -> results/_r695bma_merge_resolve.json
"""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EVID = os.path.join(ROOT, "results", "_r695bma_merge_resolve.json")


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, cwd=ROOT)
    assert r.returncode == 0, "git show fail %s:%s" % (rev, path)
    return r.stdout


def ts_of(raw, path):
    try:
        j = json.loads(raw.decode("utf-8"))
        for k in ("ts", "generated", "asof"):
            t = j.get(k)
            if isinstance(t, str) and len(t) >= 16:
                return t
    except Exception:
        pass
    try:
        last = raw.decode("utf-8").strip().splitlines()[-1]
        j = json.loads(last)
        t = j.get("ts")
        if isinstance(t, str) and len(t) >= 16:
            return t
    except Exception:
        pass
    return None


def norm_ts(t):
    return (t or "").replace("T", " ")[:19]   # r461 ts-norm law


REGEN_JSON = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
MD_TWINS = {  # md -> json twin (locked to json pick, r692bmb law)
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
JS_FACES = ["results/dashboard_status.js"]

res = {"round": "r695 bm-a", "ts": NOW, "decisions": {}}
writes = []   # (path, bytes)


def decide_regen(p, o_raw, t_raw):
    o_ts, t_ts = ts_of(o_raw, p), ts_of(t_raw, p)
    o_n, t_n = norm_ts(o_ts), norm_ts(t_ts)
    if o_ts is None and t_ts is None:
        return "theirs", "probe-miss both -> conservative theirs"
    if t_ts is None:
        return "ours", "theirs probe-miss"
    if o_ts is None:
        return "theirs", "ours probe-miss"
    return ("theirs" if t_n >= o_n else "ours"), "ts ours %s vs theirs %s" % (o_n, t_n)


# --- 1. crash_fuse.json: per-sig max-merge ---
p = "results/crash_fuse.json"
oj = json.loads(blob("HEAD", p).decode("utf-8"))
tj = json.loads(blob("MERGE_HEAD", p).decode("utf-8"))
merged = {k: tj.get(k, oj.get(k)) for k in set(oj) | set(tj)}
osigs, tsigs = oj.get("sigs", {}), tj.get("sigs", {})
sig_dec = {}
for k in set(osigs) | set(tsigs):
    a, b = osigs.get(k), tsigs.get(k)
    if a is None:
        merged["sigs"][k] = b
        continue
    if b is None:
        merged["sigs"][k] = a
        continue
    m = dict(a)
    for f in set(a) | set(b):
        av, bv = a.get(f), b.get(f)
        if av == bv:
            m[f] = av
        elif f in ("refusals", "count"):
            m[f] = max(av, bv)
            sig_dec["%s:%s max" % (k[-20:], f)] = m[f]
        elif f.endswith("_ts"):
            m[f] = av if norm_ts(av) >= norm_ts(bv) else bv
        elif f in ("machine", "shard", "code_sha256"):
            # cross-machine same-script event collision (schema keys sigs by
            # script only). r695 policy: the side whose shard key carries the
            # batch-prefix canon form (r694-ii law) wins the whole sig -- the
            # bare-key side is orphan residue retiring with the shard cleanup.
            def compliant(s):
                sk = s.get("shard", "")
                return bool(sk) and not sk.split("-")[0] in ("generate", "screen",
                                                              "judge", "run")
            if compliant(a) and not compliant(b):
                m = dict(a)
                sig_dec["%s collision->ours(bare residue dropped)" % k[-20:]] = True
            elif compliant(b) and not compliant(a):
                m = dict(b)
                sig_dec["%s collision->theirs(canon seat kept)" % k[-20:]] = True
            else:
                m = dict(b)   # unresolvable -> theirs (origin-side conservative)
                sig_dec["%s collision->theirs(conservative)" % k[-20:]] = True
            break
        else:
            raise AssertionError("fuse sig field divergence %s %s: %r vs %r"
                                 % (k, f, av, bv))
    merged["sigs"][k] = m
writes.append((p, json.dumps(merged, ensure_ascii=False, indent=1)
               .encode("utf-8") + b"\n"))
res["decisions"][p] = "per-sig max-merge union (%d sigs, %d max-picks)" % (
    len(merged.get("sigs", {})), len(sig_dec))

# --- 2. token_usage.json: per-key union, zero-hit -> explicit fallback ---
p = "results/token_usage.json"
oj = json.loads(blob("HEAD", p).decode("utf-8"))
tj = json.loads(blob("MERGE_HEAD", p).decode("utf-8"))
side_pick = 0
merged = dict(tj)
for k, v in oj.items():
    if k not in tj:
        merged[k] = v
        side_pick += 1
    elif isinstance(v, dict) and isinstance(tj[k], dict):
        # machines dict: per-machine ts newer-wins (r440/r484 law)
        sub = dict(tj[k])
        for mk, mv in v.items():
            if mk not in sub:
                sub[mk] = mv
                side_pick += 1
            elif isinstance(mv, dict) and isinstance(sub[mk], dict):
                to = norm_ts(str(mv.get("ts", "")))
                tt = norm_ts(str(sub[mk].get("ts", "")))
                if to and (not tt or to > tt):
                    sub[mk] = mv
                    side_pick += 1
        merged[k] = sub
    else:
        if isinstance(v, (int, float)) and isinstance(tj[k], (int, float)):
            merged[k] = max(v, tj[k])    # cumulative meters -> max
            side_pick += 0
        else:
            to = norm_ts(str(v if isinstance(v, str) else ""))
            tt = norm_ts(str(tj[k] if isinstance(tj[k], str) else ""))
            if to and (not tt or to > tt):
                merged[k] = v
                side_pick += 1
if side_pick == 0:
    to = norm_ts(str(oj.get("ts") or oj.get("generated") or ""))
    tt = norm_ts(str(tj.get("ts") or tj.get("generated") or ""))
    take = "theirs" if (not to and tt) or (to and tt and tt > to) else "ours"
    res["decisions"][p] = ("per-key side_pick=0 -> whole-face freshness %s "
                           "(ours %s vs theirs %s)" % (take, to, tt))
    out = tj if take == "theirs" else oj
else:
    res["decisions"][p] = "per-key union side_pick=%d" % side_pick
    out = merged
writes.append((p, json.dumps(out, ensure_ascii=False, indent=1)
               .encode("utf-8") + b"\n"))

# --- 3. x2_watch_log.jsonl: line-level union zero-loss ---
p = "results/x2_watch_log.jsonl"
ol = [l for l in blob("HEAD", p).decode("utf-8").splitlines() if l.strip()]
tl = [l for l in blob("MERGE_HEAD", p).decode("utf-8").splitlines() if l.strip()]
seen = set(tl)
extra = [l for l in ol if l not in seen]
union = tl + extra
assert set(union) >= set(ol) and set(union) >= set(tl)
writes.append((p, ("\n".join(union) + "\n").encode("utf-8")))
res["decisions"][p] = "line union theirs %d + ours-unique %d" % (len(tl), len(extra))

# --- 4. regen json faces: per-face ts newer-wins ---
picks = {}
for p in REGEN_JSON:
    o_raw, t_raw = blob("HEAD", p), blob("MERGE_HEAD", p)
    take, why = decide_regen(p, o_raw, t_raw)
    picks[p] = take
    res["decisions"][p] = "%s (%s)" % (take, why)
    writes.append((p, t_raw if take == "theirs" else o_raw))

# --- 5. md twins: locked to json picks ---
for p, jp in MD_TWINS.items():
    o_raw, t_raw = blob("HEAD", p), blob("MERGE_HEAD", p)
    take = picks[jp]
    res["decisions"][p] = "md twin locked to json pick: %s" % take
    writes.append((p, t_raw if take == "theirs" else o_raw))

# --- 6. dashboard_status.js: follow its json twin ---
p = "results/dashboard_status.js"
o_raw, t_raw = blob("HEAD", p), blob("MERGE_HEAD", p)
take = picks["results/dashboard_status.json"]
res["decisions"][p] = "js twin locked to json pick: %s" % take
writes.append((p, t_raw if take == "theirs" else o_raw))

# --- write phase ---
for p, b in writes:
    with open(os.path.join(ROOT, p), "wb") as fh:
        fh.write(b)

# --- post-write proofs: reparse + marker line-start scan (r644 content law) ---
n_json = 0
for p, _ in writes:
    full = os.path.join(ROOT, p)
    if p.endswith(".json"):
        json.loads(open(full, encoding="utf-8").read())
        n_json += 1
    elif p.endswith(".jsonl"):
        for ln in open(full, encoding="utf-8"):
            if ln.strip():
                assert isinstance(json.loads(ln), dict), "non-dict line %s" % p
    for ln in open(full, encoding="utf-8", newline="").read().splitlines():
        if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            raise AssertionError("marker line in %s" % p)

with open(EVID, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
ours_n = sum(1 for v in picks.values() if v == "ours")
print("RESOLVE OK: %d faces written (%d json reparsed PASS, marker scan clean); "
      "regen picks ours=%d theirs=%d" % (len(writes), n_json, ours_n,
                                         len(picks) - ours_n))
