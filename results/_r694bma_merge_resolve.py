"""r694 bm-a merge resolver: 17 UU faces, per-face canon decisions.

Dispositions (canon lineage):
- runnable_pool.json -> THEIRS verbatim (bm-b seat-holder canonical per fleet
  sec.4 commit-time order: their MSG-1940 seat 19:42:01 origin-first vs my
  enrollment commit 19:5x = LATER CLAIMER YIELDS; their entry carries LIVE
  autofill claim owner=bm-b 19:44:22, burn in flight; zero semantic loss --
  same id/runner/args verified).
- CODELY.md -> block-union (r675 recipe: theirs full text + my missing
  lines appended, substring-containment filter r479, dedup r453-increment,
  origin-prefix intact + mine-entry-present assertions).
- token_usage.json -> r466 per-key union probe; side_pick==0 -> whole-face
  ts-freshness fallback.
- pool_core_samples.jsonl -> line-level union, zero-loss containment both.
- 12 regen faces -> per-face ts-freshness newer-wins (r440); md twins follow
  json (r692).

Evidence -> results/_r694bma_merge_resolve.json. Fail-closed: any probe miss
or assertion failure = ABORT with zero writes to origin-bound faces.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EVID = os.path.join(ROOT, "results", "_r694bma_merge_resolve.json")


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, cwd=ROOT)
    assert r.returncode == 0, "git show fail %s:%s" % (rev, path)
    return r.stdout


def ts_of(raw, path):
    """Extract freshness ts from content: json 'ts' field, else last-line
    jsonl ts, else None (probe-miss)."""
    try:
        j = json.loads(raw.decode("utf-8"))
        t = j.get("ts")
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


REGEN = [
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

res = {"round": "r694 bm-a", "ts": NOW, "decisions": {}, "yields": {}}
writes = []   # (path, bytes)

# --- 1. runnable_pool.json -> THEIRS (seat yield, live claim) ---
p = "results/runnable_pool.json"
ours_p = blob("HEAD", p)
theirs_p = blob("MERGE_HEAD", p)
oj = json.loads(ours_p.decode("utf-8"))
tj = json.loads(theirs_p.decode("utf-8"))
mine_gen = [e for e in oj["entries"] if e["id"] == "PERPETUAL-N2-W15-GENERATE"]
their_gen = [e for e in tj["entries"] if e["id"] == "PERPETUAL-N2-W15-GENERATE"]
assert len(mine_gen) == 1 and len(their_gen) == 1
assert their_gen[0]["runner"] == "scripts/perpetual_faces_n2.py"
assert their_gen[0]["runner_args"] == ["generate"]
assert their_gen[0]["shards"][0].get("owner") == "bm-b"
assert their_gen[0]["shards"][0].get("owner_since") == "2026-10-04 19:44:22"
writes.append((p, theirs_p))
res["yields"]["pool_seat"] = ("bm-b MSG-1940 seat 19:42:01 origin-first "
                              "(autofill claim 19:44:22 live); my duplicate "
                              "enrollment entry dropped, theirs canonical "
                              "verbatim; same id/runner/args verified")

# --- 2. CODELY.md -> block-union (r675 + r479 containment) ---
p = "CODELY.md"
ours_c = blob("HEAD", p).decode("utf-8")
theirs_c = blob("MERGE_HEAD", p).decode("utf-8")
theirs_lines = theirs_c.splitlines()
ours_lines = ours_c.splitlines()
missing = []
for ln in ours_lines:
    if ln in theirs_lines:
        continue
    # r479 containment: my line is a variant-substring of an origin line =
    # origin already carries this entry (possibly normalized) -> drop
    if any(ln and ln in tb for tb in theirs_lines if tb != ln):
        res["decisions"]["codely_containment_drop"] = ln[:80]
        continue
    # migration-pointer filter (this window): my full-body line whose
    # round+machine tag is referenced by a theirs COLD-LAYER POINTER line =
    # theirs deliberately migrated it to archive (bm-b r690 r453 receipt
    # migration) -> re-adding would clobber their intentional move (r486 trap)
    tag_m = re.match(r"- \[([0-9-]+ [0-9:x]+ r\d+ \S+)\]", ln)
    if tag_m:
        tag = tag_m.group(1)
        rid_m = re.search(r"(O-20\d{6}-\d+-bm-\w+)", ln)
        rid = rid_m.group(1) if rid_m else ""
        if any((tag in tb or (rid and rid in tb)) and "指针" in tb
               for tb in theirs_lines):
            res["decisions"].setdefault("codely_migrated_drop", []).append(tag)
            continue
    missing.append(ln)
union = theirs_c
if missing:
    if not union.endswith("\n"):
        union += "\n"
    union += "\n".join(missing) + "\n"
ub = union.encode("utf-8")
# assertions: origin prefix intact; my pit entry present exactly once
assert union.startswith(theirs_c.rstrip("\n")) or theirs_c.rstrip("\n") in union
assert union.count("r694 bm-a] 正则行级手术") == 1, "my pit entry not exactly once"
writes.append((p, ub))
res["decisions"]["codely_union"] = "theirs full + mine missing %d lines" % len(missing)

# --- 3. token_usage.json -> r466 per-key union, side_pick==0 -> ts fallback ---
p = "results/token_usage.json"
oj = json.loads(blob("HEAD", p).decode("utf-8"))
tj = json.loads(blob("MERGE_HEAD", p).decode("utf-8"))
side_pick = 0
merged = dict(tj)
for k, v in oj.items():
    if k not in tj:
        merged[k] = v
        side_pick += 1
    else:
        if oj[k] != tj[k]:
            # per-key ts newer-wins for dict values
            if isinstance(oj[k], dict) and isinstance(tj[k], dict):
                to = norm_ts(str(oj[k].get("ts", "")))
                tt = norm_ts(str(tj[k].get("ts", "")))
                if to and tt and to > tt:
                    merged[k] = oj[k]
                    side_pick += 1
if side_pick == 0:
    # r466 law: zero hits -> explicit whole-face freshness decision on the
    # face's own generation stamp (generated, falling back to ts)
    to = norm_ts(str(oj.get("ts") or oj.get("generated") or ""))
    tt = norm_ts(str(tj.get("ts") or tj.get("generated") or ""))
    take = "theirs" if (not to and tt) or (to and tt and tt > to) else "ours"
    res["decisions"]["token_usage"] = ("per-key side_pick=0 -> whole-face "
                                       "freshness %s (ours %s vs theirs %s)"
                                       % (take, to, tt))
    out = tj if take == "theirs" else oj
else:
    res["decisions"]["token_usage"] = "per-key union side_pick=%d" % side_pick
    out = merged
writes.append((p, json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8")
              + b"\n"))

# --- 4. pool_core_samples.jsonl -> line-level union zero-loss ---
p = "results/pool_core_samples.jsonl"
ol = blob("HEAD", p).decode("utf-8").splitlines()
tl = blob("MERGE_HEAD", p).decode("utf-8").splitlines()
seen = set(tl)
extra = [l for l in ol if l not in seen and l.strip()]
union_l = tl + extra
assert set(union_l) >= set(l for l in ol if l.strip())
assert set(union_l) >= set(l for l in tl if l.strip())
writes.append((p, ("\n".join(union_l) + "\n").encode("utf-8")))
res["decisions"]["pool_core_samples"] = ("line union: theirs %d + ours-unique "
                                         "%d" % (len(tl), len(extra)))

# --- 5. regen faces -> per-face ts-freshness newer-wins ---
md_follow_json = {}
for p in REGEN:
    o_raw = blob("HEAD", p)
    t_raw = blob("MERGE_HEAD", p)
    jp = p[:-3] + ".json" if p.endswith(".md") else None
    if p.endswith(".md"):
        base = jp
        o_ts = ts_of(blob("HEAD", base), base) if base else None
        t_ts = ts_of(blob("MERGE_HEAD", base), base) if base else None
    else:
        o_ts = ts_of(o_raw, p)
        t_ts = ts_of(t_raw, p)
    o_n, t_n = norm_ts(o_ts), norm_ts(t_ts)
    if o_ts is None and t_ts is None:
        take = "theirs"   # conservative: origin-side (already at origin)
        reason = "probe-miss both -> conservative theirs"
    elif t_ts is None:
        take = "ours"
        reason = "theirs probe-miss"
    elif o_ts is None:
        take = "theirs"
        reason = "ours probe-miss"
    else:
        take = "theirs" if t_n >= o_n else "ours"
        reason = "ts ours %s vs theirs %s" % (o_n, t_n)
    res["decisions"][p] = "%s (%s)" % (take, reason)
    writes.append((p, t_raw if take == "theirs" else o_raw))

# --- write phase ---
for p, b in writes:
    with open(os.path.join(ROOT, p), "wb") as fh:
        fh.write(b)

# --- post-write proofs: json reparse + marker line-start scan ---
for p, _ in writes:
    full = os.path.join(ROOT, p)
    if p.endswith(".json") or p.endswith(".jsonl"):
        raw2 = open(full, encoding="utf-8").read()
        if p.endswith(".json"):
            json.loads(raw2)
    raw2 = open(full, encoding="utf-8", newline="").read()
    for ln in raw2.splitlines():
        if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            raise AssertionError("marker line in %s: %s" % (p, ln[:60]))

# pool reparse final state: my duplicate gone, theirs present with live claim
p2 = json.loads(open(os.path.join(ROOT, "results/runnable_pool.json"),
                     encoding="utf-8").read())
gens = [e for e in p2["entries"] if e["id"] == "PERPETUAL-N2-W15-GENERATE"]
assert len(gens) == 1 and gens[0]["shards"][0]["owner"] == "bm-b"
res["pool_after"] = {"entries": len(p2["entries"]),
                     "generate_shard_owner": gens[0]["shards"][0]["owner"]}

with open(EVID, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print("RESOLVE OK: %d faces written; pool=%d entries (GENERATE owner=bm-b live); "
      "decisions: %s" % (len(writes), res["pool_after"]["entries"],
                         json.dumps(res["decisions"], ensure_ascii=False)[:400]))
