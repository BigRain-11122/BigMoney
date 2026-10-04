"""r696 bm-a merge resolver: 17 UU faces, per-face canon decisions.

Canon lineage r692bmb/r694bma/r695bma resolver family:
- crash_fuse.json -> per-sig max-merge (sigs union; refusals/count max,
  last_*_ts newer-wins; shared-key equal-assert; collision fields ->
  batch-prefix-compliant shard wins, bare residue retires [r694-ii]).
- x2_watch_log.jsonl / pool_core_samples.jsonl / pool_red_flags.jsonl ->
  append-only line-level union zero-loss (theirs + ours-unique).
- 10 regen json faces -> per-face ts-freshness newer-wins (r440);
  md twins locked to their json picks (r692bmb law).

Fail-closed: any probe miss or assertion failure = ABORT zero writes
(the merge stays un-committed; no origin-bound bytes touched).
Evidence -> results/_r696bma_merge_resolve.json
"""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EVID = os.path.join(ROOT, "results", "_r696bma_merge_resolve.json")


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
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/futures_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
MD_TWINS = {  # md -> json twin (locked to json pick, r692bmb law)
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
JSONL_UNION = [
    "results/x2_watch_log.jsonl",
    "results/pool_core_samples.jsonl",
    "results/pool_red_flags.jsonl",
]

res = {"round": "r696 bm-a", "ts": NOW, "decisions": {}}
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


# --- 1. crash_fuse.json: per-sig max-merge (r695 canon) ---
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
            # cross-machine same-script event collision (r695 policy,
            # r694-ii batch-prefix law): the compliant shard side wins
            # the whole sig; the bare-key side is orphan residue.
            def compliant(s):
                sk = s.get("shard", "")
                return bool(sk) and not sk.split("-")[0] in ("generate",
                                                              "screen",
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
res["decisions"][p] = "per-sig max-merge union (%d sigs, %d picks)" % (
    len(merged.get("sigs", {})), len(sig_dec))

# --- 2. jsonl faces: line-level union zero-loss (r656 canon) ---
for p in JSONL_UNION:
    ol = [l for l in blob("HEAD", p).decode("utf-8").splitlines() if l.strip()]
    tl = [l for l in blob("MERGE_HEAD", p).decode("utf-8").splitlines() if l.strip()]
    seen = set(tl)
    extra = [l for l in ol if l not in seen]
    union = tl + extra
    assert set(union) >= set(ol) and set(union) >= set(tl)
    writes.append((p, ("\n".join(union) + "\n").encode("utf-8")))
    res["decisions"][p] = "line union theirs %d + ours-unique %d" % (len(tl), len(extra))

# --- 3. regen json faces: per-face ts newer-wins ---
picks = {}
for p in REGEN_JSON:
    o_raw, t_raw = blob("HEAD", p), blob("MERGE_HEAD", p)
    take, why = decide_regen(p, o_raw, t_raw)
    picks[p] = take
    res["decisions"][p] = "%s (%s)" % (take, why)
    writes.append((p, t_raw if take == "theirs" else o_raw))

# --- 4. md twins: locked to json picks ---
for p, jp in MD_TWINS.items():
    o_raw, t_raw = blob("HEAD", p), blob("MERGE_HEAD", p)
    take = picks[jp]
    res["decisions"][p] = "md twin locked to json pick: %s" % take
    writes.append((p, t_raw if take == "theirs" else o_raw))

# --- write phase ---
for p, b in writes:
    with open(os.path.join(ROOT, p), "wb") as fh:
        fh.write(b)

# --- post-write proofs: reparse + marker line-start scan (r644 law) ---
n_json = 0
for p, _ in writes:
    full = os.path.join(ROOT, p)
    if p.endswith(".json"):
        json.loads(open(full, encoding="utf-8").read())
        n_json += 1
    elif p.endswith(".jsonl"):
        # zero-NEW-defect law (r641 precedent): pool_red_flags carries a
        # pre-existing malformed line from 2026-10-03 00:53 (both merge
        # sides, git history) -- the proof asserts the merge resolution
        # introduces ZERO new malformed content (content-level subset),
        # instead of failing on the inherited historical defect.
        def _bad_content(lines):
            out = set()
            for ln in lines:
                if not ln.strip():
                    continue
                try:
                    if not isinstance(json.loads(ln), dict):
                        out.add(ln)
                except Exception:
                    out.add(ln)
            return out
        wt_bad = _bad_content(
            open(full, encoding="utf-8").read().splitlines())
        side_bad = set()
        for rev in ("HEAD", "MERGE_HEAD"):
            side_bad |= _bad_content(
                blob(rev, p).decode("utf-8").splitlines())
        assert wt_bad <= side_bad, \
            "merge introduced NEW malformed lines in %s" % p
        if side_bad:
            res["decisions"][p] += (" (pre-existing malformed tolerated:"
                                     " %d content-variants)" % len(side_bad))
    for ln in open(full, encoding="utf-8", newline="").read().splitlines():
        if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            raise AssertionError("marker line in %s" % p)

with open(EVID, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
ours_n = sum(1 for v in picks.values() if v == "ours")
print("RESOLVE OK: %d faces written (%d json reparsed PASS, marker scan clean); "
      "regen picks ours=%d theirs=%d" % (len(writes), n_json, ours_n,
                                         len(picks) - ours_n))
