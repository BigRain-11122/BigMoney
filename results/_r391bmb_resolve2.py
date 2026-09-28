"""r391 bm-b rebase UU resolver #2 (main-commit replay vs bm-a round 174).

Files: results/runnable_pool.json (entry-level union), handled here.
scripts/compute_audit.py -> take origin side (bm-a first-committer v2.4
canonical; bmb duplicate yielded per fleet README sec.4 time-order law).
fleet/tasks/T-2026-09-28-107-P0.json -> hand-merge: bm-a claimed_by kept
(first-committer), both progress notes unioned, bmb yield receipt appended.

Pool union law: entry-level zero-loss union; status precedence
done > ready > waiting; same status -> newer ts field wins (owner_since /
done_at / entered_at, str() comparable ISO format); notes concatenated
when divergent (append-only ledger semantics); shards unioned per key with
the same precedence. Zero-loss check: union entry ids == |A ids ∪ B ids|.
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
TICKET = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-28-107-P0.json")


def stage(side, path):
    out = subprocess.run(["git", "show", f":{side}:{path}"],
                         capture_output=True).stdout
    return json.loads(out.decode("utf-8-sig"))


STATUS_RANK = {"done": 3, "ready": 2, "waiting": 1, None: 0}


def newer(*pairs):
    """Pick the non-None max by ISO-ish string comparison."""
    vals = [v for v in pairs if v]
    return max(vals) if vals else None


def union_shards(a, b):
    out = {}
    keys = {s.get("key") for s in (a or [])} | {s.get("key") for s in (b or [])}
    for k in keys:
        sa = next((s for s in (a or []) if s.get("key") == k), None)
        sb = next((s for s in (b or []) if s.get("key") == k), None)
        if sa is None:
            out[k] = sb
            continue
        if sb is None:
            out[k] = sa
            continue
        merged = dict(sa)
        ra, rb = STATUS_RANK.get(sa.get("status")), STATUS_RANK.get(sb.get("status"))
        base, other = (sa, sb) if ra >= rb else (sb, sa)
        merged = dict(base)
        for f in ("owner", "owner_since", "done_at", "checkpoint", "result_ref"):
            if other.get(f) and (not merged.get(f)
                                 or str(other[f]) > str(merged.get(f))):
                merged[f] = other[f]
        if sa.get("status") != sb.get("status"):
            merged["status"] = base["status"]
        out[k] = merged
    return [out[k] for k in sorted(out)]


def union_entry(a, b):
    base, other = (a, b) if STATUS_RANK.get(a.get("status"), 0) >= \
        STATUS_RANK.get(b.get("status"), 0) else (b, a)
    merged = dict(base)
    for f in ("done_at", "entered_at", "amended_at"):
        if other.get(f) and (not merged.get(f)
                             or str(other[f]) > str(merged.get(f))):
            merged[f] = other[f]
    merged["shards"] = union_shards(a.get("shards"), b.get("shards"))
    na, nb = str(a.get("note") or ""), str(b.get("note") or "")
    if na != nb:
        merged["note"] = (na + (" || " if na and nb else "") + nb).strip()
    # data_gates / workers_plan / ticket_ref / prereg_ref: prefer the side
    # that authored the entry change; keep base (higher status side) unless
    # only the other side has the field.
    for f in ("ticket_ref", "prereg_ref", "runner", "runner_args",
              "lane_owner", "priority", "workers_plan", "data_gates"):
        if other.get(f) and not merged.get(f):
            merged[f] = other[f]
    return merged


def main():
    a = stage(2, "results/runnable_pool.json")   # origin / bm-a r174
    b = stage(3, "results/runnable_pool.json")   # bmb r391 replay
    ea = a["entries"] if isinstance(a, dict) and "entries" in a else a
    eb = b["entries"] if isinstance(b, dict) and "entries" in b else b
    ids_a = {e["id"] for e in ea}
    ids_b = {e["id"] for e in eb}
    union = []
    for eid in sorted(ids_a | ids_b):
        ta = next((e for e in ea if e["id"] == eid), None)
        tb = next((e for e in eb if e["id"] == eid), None)
        union.append(union_entry(ta, tb) if (ta and tb) else (ta or tb))
    assert len(union) == len(ids_a | ids_b), "zero-loss entry-count check"
    pool = a if isinstance(a, dict) and "entries" in a else {"entries": []}
    pool["entries"] = union
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)
    os.replace(tmp, POOL)
    json.loads(open(POOL, encoding="utf-8").read())  # parse-validate
    print(f"pool union: |A|={len(ids_a)} |B|={len(ids_b)} "
          f"-> |union|={len(union)} (zero-loss OK)")
    for e in union:
        if e["id"] in ("DECISION-CHAIN-V2-P1", "TRIAL-LABOR-W4-JUDGE",
                       "MASS-TRIAL-W1-JUDGE-SHARD-0",
                       "MASS-TRIAL-W1-JUDGE-SHARD-1",
                       "MASS-TRIAL-W1-JUDGE-SHARD-2",
                       "MASS-TRIAL-W1-JUDGE-SHARD-3",
                       "SENTIMENT-AXES-FULLHIST-P1",
                       "T104-GRID-S3-DUALFACE-P1"):
            sh = [(s.get("key"), s.get("status"), s.get("owner"))
                  for s in e.get("shards", [])]
            print("  ", e["id"], "->", e.get("status"), sh[:4])

    # T-107 ticket hand-merge: bm-a first-committer claim kept, notes union
    ta = stage(2, "fleet/tasks/T-2026-09-28-107-P0.json")
    tb = stage(3, "fleet/tasks/T-2026-09-28-107-P0.json")
    t = dict(ta)  # origin side = bm-a claim (first on origin per sec.4)
    for k, v in tb.items():
        if k == "claimed_by" or k == "claimed_at":
            continue  # bm-a first-committer retained
        if k not in t:
            t[k] = v
        elif isinstance(v, str) and v != str(t[k]) and "progress" in k:
            t[k + "_bmb_same_window"] = v  # zero-loss second-arrival copy
    t["note"] = (str(ta.get("note") or "") + " || r391b bm-b same-window "
                 "second-arrival receipt: bmb T-107 claim 16:42 + slice-1 "
                 "(audit v2.4 supply_gap/supply_gap_p0/escalation + 7 "
                 "selftest cases) was in flight when bm-a r174 slice-1 "
                 "(supply-family 4-legs + supply floor + streak escalation "
                 "+ charter + utilization face) landed first on origin -> "
                 "bmb yields per fleet README sec.4 time-order law; "
                 "compute_audit.py canonical = bm-a version; bmb unique "
                 "delta (O-1625 ready==0+open-tickets candidate face) "
                 "ported separately only if absent").strip()
    tmp = TICKET + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=2)
    os.replace(tmp, TICKET)
    json.loads(open(TICKET, encoding="utf-8").read())
    print("T-107 merged: claimed_by=%s (first-committer kept), "
          "bmb progress preserved as _bmb_same_window"
          % t.get("claimed_by", "")[:60])


if __name__ == "__main__":
    main()
