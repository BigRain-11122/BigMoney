# -*- coding: utf-8 -*-
# r629 bm-b rebase conflict resolver (22 UU, classify_conflicts.py recipe routing
# + hand-qualified UNKNOWNs per SKILL.md; r628 resolver lineage).
# Stage mapping during REBASE: stage2 = ours = upstream (origin tip), stage3 = theirs
# = my replayed commit. Same-second ties -> upstream side (r140 law).
import json, re, subprocess, sys

ROLLING = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions", "launches"],
}
JS_WRAPPER = ["results/dashboard_status.js"]
APPEND_LOG = ["results/pool_core_samples.jsonl"]
POOL_FACE = ["results/runnable_pool.json"]
# regenerated same-day docs / per-run evidence snapshots / determinstic re-derives:
# newest embedded ts wins wholesale (all are idempotent re-derive or per-run evidence)
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/_r633bma_finalize_rehearsal_fund_value_p1.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        sys.exit("STAGE FAIL %s stage %d: %s" % (path, stage,
                                                 r.stderr.decode("utf-8", "replace")[:120]))
    return r.stdout


def newest_ts(blob):
    hits = [m.group(0) for m in TS_RE.finditer(blob.decode("utf-8", "replace"))]
    return max(hits) if hits else ""


def union_rows(a, b):
    seen, out = set(), []
    for row in list(a) + list(b):
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def shard_rank(sh):
    # done beats everything; then newer owner_since; tie -> caller keeps upstream
    st = 1 if str(sh.get("status")) == "done" else 0
    return (st, sh.get("owner_since") or "")


def merge_shard(sa, sb):
    return sa if shard_rank(sa) >= shard_rank(sb) else sb


def merge_entry(a, b):
    # per-face: union shards by key, per-shard newer-wins (done first);
    # entry scalars from the side winning the stronger shard face sum
    ash = {s["key"]: s for s in a.get("shards", [])}
    bsh = {s["key"]: s for s in b.get("shards", [])}
    merged = {}
    a_wins = b_wins = 0
    for k in sorted(set(ash) | set(bsh)):
        if k in ash and k in bsh:
            w = merge_shard(ash[k], bsh[k])
            if w is ash[k]:
                a_wins += 1
            else:
                b_wins += 1
            merged[k] = w
        else:
            merged[k] = ash.get(k) or bsh[k]
            (a_wins, b_wins) = (a_wins + 1, b_wins) if k in ash else (a_wins, b_wins + 1)
    out = dict(b if b_wins > a_wins else a)  # scalars from winning side; tie->a(upstream)
    out["shards"] = [merged[k] for k in sorted(merged)]
    return out


def resolve_pool(o, t):
    oe = {e["id"]: e for e in o.get("entries", [])}
    te = {e["id"]: e for e in t.get("entries", [])}
    entries = []
    diff = []
    for eid in sorted(set(oe) | set(te)):
        if eid in oe and eid in te:
            m = merge_entry(oe[eid], te[eid])
            if m != oe[eid] or m != te[eid]:
                diff.append(eid)
            entries.append(m)
        else:
            side = oe.get(eid) or te[eid]
            entries.append(side)
            diff.append(eid + " (one-side)")
    out = {k: v for k, v in o.items() if k != "entries"}
    for k, v in t.items():
        if k != "entries" and k not in out:
            out[k] = v  # top-level keys mine has that origin lacks
    out["entries"] = entries
    return out, diff


def main():
    report = []
    for path in ROLLING:
        ours = json.loads(stage_bytes(path, 2).decode("utf-8", "replace"))
        theirs = json.loads(stage_bytes(path, 3).decode("utf-8", "replace"))
        base_n = {}
        for key in ROLLING[path]:
            a, b = ours.get(key) or [], theirs.get(key) or []
            merged = union_rows(a, b)
            assert len(merged) >= max(len(a), len(b)), "union shrink %s %s" % (path, key)
            base_n[key] = (len(a), len(b), len(merged))
            ours[key] = merged
        pick = theirs if newest_ts(stage_bytes(path, 3)) > newest_ts(stage_bytes(path, 2)) else ours
        for k, v in pick.items():
            if k not in ROLLING[path]:
                ours[k] = v
        merged = json.dumps(ours, ensure_ascii=False, indent=1)
        json.loads(merged)
        open(path, "w", encoding="utf-8", newline="").write(merged + "\n")
        report.append((path, "rolling-ledger union", base_n))

    for path in JS_WRAPPER:
        o, t = stage_bytes(path, 2), stage_bytes(path, 3)
        winner = t if newest_ts(t) > newest_ts(o) else o
        assert b"window.DASH_DATA" in winner, "wrapper missing"
        open(path, "wb").write(winner)
        report.append((path, "js-wrapper whole-byte take-new", None))

    for path in APPEND_LOG:
        o = stage_bytes(path, 2).decode("utf-8", "replace").splitlines()
        t = stage_bytes(path, 3).decode("utf-8", "replace").splitlines()
        seen, out = set(), []
        for ln in list(o) + list(t):
            if ln.strip() and ln not in seen:
                seen.add(ln)
                out.append(ln)
        assert len(out) >= max(len(o), len(t)), "append union shrink " + path
        open(path, "w", encoding="utf-8", newline="").write("\n".join(out) + "\n")
        report.append((path, "append-log union lines %d+%d->%d" % (len(o), len(t), len(out)), None))

    for path in POOL_FACE:
        o = json.loads(stage_bytes(path, 2).decode("utf-8", "replace"))
        t = json.loads(stage_bytes(path, 3).decode("utf-8", "replace"))
        merged, diff = resolve_pool(o, t)
        txt = json.dumps(merged, ensure_ascii=False, indent=1)
        json.loads(txt)
        open(path, "w", encoding="utf-8", newline="").write(txt + "\n")
        report.append((path, "pool per-face merge (entries union, shard newer-wins, done-first, tie->upstream)",
                       {"both_entries": len(o.get("entries", [])), "merged": len(merged["entries"]),
                        "face_diffs": diff[:12]}))

    for path in SNAPSHOTS:
        o, t = stage_bytes(path, 2), stage_bytes(path, 3)
        to, tt = newest_ts(o), newest_ts(t)
        winner = t if tt > to else o
        if path.endswith(".json"):
            json.loads(winner.decode("utf-8", "replace"))  # parse check
        open(path, "wb").write(winner)
        report.append((path, "snapshot take-new by ts (ours=%s theirs=%s)" % (to, tt), None))

    for path, recipe, extra in report:
        print("RESOLVED %-52s %s %s" % (path, recipe, extra or ""))


if __name__ == "__main__":
    main()
