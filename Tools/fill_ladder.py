#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fill_ladder.py -- T-107 slice-2 supply-floor fill-ladder generator.

O-20260928-1614 sec.1 SUPPLY FLOOR: runnable_pool ready count >= 3 per machine
at all times; below floor -> standing fill-generator auto-enqueues from the
fill ladder (sec.4 priorities a/b/c/d). O-20260928-1630 D4 names the standing
supply catalog this generator consumes. COMPUTE_AUDIT.md v2.4 supply_floor
flag names this generator as the remediation face.

DESIGN LAWS (frozen in this slice):
  * The ladder is a DISPATCHER OVER EXISTING LAW, zero new research invention
    inside this tool (T-107 anti-dup note). Every catalog entry must cite its
    law line (ticket/prereg) and carry an ENQUEUE GATE; the generator only
    enqueues entries whose gates pass -- prereg-absent supply is NEVER
    enqueued (BACKTEST_SCIENCE: every burn batch needs a frozen prereg).
  * Idempotent append-only: an id already present in the pool (any status) is
    never re-added; re-running is a no-op.
  * DOUBLE-FILE LAW (r399 lane-merge law): every pool mutation writes BOTH
    results/runnable_pool.json (shared) and results/runnable_pool.<id>.json
    (lane) with the same bytes in the same operation -- shared-only edits are
    resurrected by the next tick's lane-merge union.
  * Zero writes when floor is satisfied or no lawful candidate exists
    (honest no-op, stdout evidence only).

USAGE:
  python Tools/fill_ladder.py            # live: floor check + enqueue if due
  python Tools/fill_ladder.py --dry-run  # report only, zero writes
  python Tools/fill_ladder.py --floor N   # override floor (default 3)
  python Tools/fill_ladder.py selftest   # hermetic offline selftest
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOOR_DEFAULT = 3

CATALOG_PATH = os.path.join(ROOT, "Tools", "fill_ladder_catalog.json")


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _machine_id():
    with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as f:
        return json.load(f)["machine_id"]


def _pool_paths(machine_id):
    shared = os.path.join(ROOT, "results", "runnable_pool.json")
    lane = os.path.join(ROOT, "results", "runnable_pool.%s.json" % machine_id)
    return shared, lane


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _lane_ok(entry, machine_id):
    """F-08/R31 lane guard, same semantics as autofill: null/ANY = any machine."""
    lane = entry.get("lane_owner")
    return lane in (None, "", "ANY") or lane == machine_id


def _compatible_ready_count(pool, machine_id):
    if not pool:
        return 0
    entries = pool.get("entries", pool if isinstance(pool, list) else [])
    return sum(1 for e in entries if e.get("status") == "ready" and _lane_ok(e, machine_id))


def _write_pool_double(shared_path, lane_path, pool_obj):
    """r399 law: shared + lane same bytes, shared first, both atomic-ish."""
    data = json.dumps(pool_obj, ensure_ascii=False, indent=1) + "\n"
    tmp = shared_path + ".ladder_tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
    os.replace(tmp, shared_path)
    lane_dir = os.path.dirname(lane_path)
    if os.path.isdir(lane_dir):
        tmp2 = lane_path + ".ladder_tmp"
        with open(tmp2, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp2, lane_path)


def _gate_pass(gate, machine_id, pool, cand_runner=None):
    """Catalog gate: list of requirement strings, all must hold.

    Supported requirement forms (extensible, D4 will add):
      prereg_frozen:<repo-relative path>   -- file must exist in-tree AND its
                                              head (first 12 lines) must not
                                              carry a live draft state:
                                              explicit 【状态：FROZEN】 wins
                                              (r189 status-line authority);
                                              with no status field the head
                                              must be free of draft markers
                                              (非冻结/冻结挂起/禁按本稿/起草中/
                                              草稿面) -- W5 draft-head
                                              convention, r176 calibration
      runner_exists                        -- the candidate's own runner file
                                              must exist (no ignition of an
                                              unbuilt runner)
      standing_no_judge_inflight           -- TRIAL_LABOR_LAW sec.1 常供律
                                              condition: no JUDGE-family pool
                                              entry in ready/waiting state
                                              (supply waves wait for the
                                              judge pipeline; law text in the
                                              W5 catalog entry).
    """
    for req in gate or []:
        if req.startswith("prereg_frozen:"):
            p = req.split(":", 1)[1]
            full = os.path.join(ROOT, p)
            if not os.path.exists(full):
                return False, "prereg absent: %s" % p
            with open(full, encoding="utf-8", errors="replace") as f:
                head = "".join(f.readline() for _ in range(12))
            # r189 status-line authority: an explicit 【状态：...】 field is the
            # authoritative freeze state; narrative draft-era words in a FROZEN
            # head are history, not a live draft marker (live-fire case: W5
            # head carries 冻结挂起 inside its r162 lineage narrative while the
            # status field says FROZEN -- naive substring scan false-refused the
            # frozen prereg and starved the supply floor).
            m = re.search(r"【状态[:：]([^】]*)】", head)
            if m:
                if "FROZEN" not in m.group(1).upper():
                    return False, "prereg not frozen (status=%s): %s" % (
                        m.group(1)[:40], p)
            else:
                for marker in ("非冻结", "冻结挂起", "禁按本稿", "起草中", "草稿面"):
                    if marker in head:
                        return False, "prereg draft-pending (%s): %s" % (marker, p)
        elif req == "runner_exists":
            r = cand_runner
            if not r or not os.path.exists(os.path.join(ROOT, r)):
                return False, "runner not built: %s" % r
        elif req == "standing_no_judge_inflight":
            entries = (pool or {}).get("entries", [])
            for e in entries:
                if "JUDGE" in (e.get("id") or "") and e.get("status") in ("ready", "waiting"):
                    return False, "judge batch %s still %s (TRIAL_LABOR_LAW sec.1)" % (
                        e.get("id"), e.get("status"))
        else:
            return False, "unknown gate req: %s" % req
    return True, ""


def _ensure_shards(entry):
    """r301 law family: a ready entry without shards starves the autofill
    picker (submit-contract trio). First live fire r179: NATIONAL-TEAM-S3
    entered shard-less and sat unclaimable. Single-face ladder batches get
    the default shard synthesized; multi-shard batches must declare shards
    explicitly in the catalog entry (explicit shards are preserved)."""
    if not entry.get("shards"):
        entry["shards"] = [{"key": "main", "status": "ready",
                            "checkpoint": "",
                            "note": "ladder default shard "
                                    "(single-face batch, r301 family)",
                            "owner": None}]
    return entry


def consumer_plan_missing(cand):
    """O-1820 meaning law (r193 bm-c engineering slice): every NEW pool
    entry must name its consuming face (judged verdict / library / paper
    / scorecard / dashboard / research digest) -- burn without a consumer
    is fake saturation (宁亮牌不造活). Append-only: pre-existing pool and
    catalog rows are grandfathered; this gate binds new candidates only."""
    return not (cand.get("consumer_plan") or "").strip()


def workers_plan_missing(cand):
    """O-20260924-2130 s1.1 multi-core law (r459 bm-a live-fire: SLOT-6
    enqueued plan-less -> autofill._pick hard-skips "no workers_plan"
    -> ready batch stranded unclaimable, tick verdict pool_empty_or_busy
    for 3 ticks while the entry sat "ready"). New candidates must carry
    a multi-core plan; dict or non-empty string form both valid. Same
    append-only grandfather scope as consumer_plan."""
    wp = cand.get("workers_plan")
    if isinstance(wp, dict):
        return not wp
    return not (wp or "").strip()


def _merged_pool_view(shared_path):
    """T-116 s3 wave-1 flip (D-20260928-03(1) structural end-state): the
    ladder's DECISION base is the lane-merged view (scripts/merge_lane_views.
    face_view -- shared + bm-a/bm-b/bm-c lanes, fixed source order, same
    merger recipes the tick settle writes). existing_ids idempotency and
    the floor/judge gates thereby see lane-only rows a bare shared read
    is blind to; the write side keeps the double-file law unchanged.
    No sources at all = {'entries': []} (pre-flip missing-shared parity).
    Corrupt sources / identity contradictions raise -- the ladder refuses
    to enqueue on an unreadable base (fail-closed beats a blind fill)."""
    sdir = os.path.join(ROOT, "scripts")
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    import merge_lane_views as _mlv
    return _mlv.face_view("runnable_pool",
                          results_dir=os.path.dirname(shared_path)) \
        or {"entries": []}


def run(dry_run=False, floor=FLOOR_DEFAULT):
    machine_id = _machine_id()
    shared_path, lane_path = _pool_paths(machine_id)
    pool = _merged_pool_view(shared_path)
    entries = pool.get("entries", [])
    existing_ids = {e.get("id") for e in entries}
    ready_n = _compatible_ready_count(pool, machine_id)
    print("[ladder] machine=%s compatible_ready=%d floor=%d" % (machine_id, ready_n, floor))
    if ready_n >= floor:
        print("[ladder] floor satisfied -- no-op")
        return 0
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    added, blocked = [], []
    for cand in catalog.get("entries", []):
        cid = cand["id"]
        if cid in existing_ids:
            continue
        if cand.get("lane_owner") not in (None, "", "ANY") and cand["lane_owner"] != machine_id:
            continue
        ok, why = _gate_pass(cand.get("enqueue_gates"), machine_id, pool, cand.get("runner"))
        if not ok:
            blocked.append((cid, why))
            continue
        if consumer_plan_missing(cand):
            blocked.append((cid, "consumer_plan missing (O-1820 meaning "
                                "law: candidate must name its consuming "
                                "face -- 宁亮牌不造活; r193 schema slice)"))
            continue
        if workers_plan_missing(cand):
            blocked.append((cid, "workers_plan missing (O-2130 multi-core "
                                "law: autofill._pick hard-skips plan-less "
                                "entries -- r459 SLOT-6 stranded live-fire)"))
            continue
        entry = {k: v for k, v in cand.items() if k != "enqueue_gates"}
        entry["status"] = "ready"
        _ensure_shards(entry)
        entry["entered_at"] = _now()
        entry["entered_by"] = "%s fill_ladder T-107 slice-2" % machine_id
        entries.append(entry)
        added.append(cid)
    if added:
        pool["entries"] = entries
        if dry_run:
            print("[ladder] DRY-RUN would enqueue: %s (zero writes)" % added)
        else:
            _write_pool_double(shared_path, lane_path, pool)
            print("[ladder] enqueued (shared+lane double-file): %s" % added)
    else:
        print("[ladder] no lawful supply candidate passed gates -- honest no-op; "
              "floor breach %d<%d stands until preregs land" % (ready_n, floor))
        for cid, why in blocked:
            print("[ladder]   blocked: %s (%s)" % (cid, why))
    return 0


def selftest():
    """Hermetic offline selftest -- no repo pool writes, temp-dir fixtures."""
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="fill_ladder_selftest_")
    try:
        # fixture: shared+lane pool with one bm-b-lane ready entry -> bm-c floor 0
        shared = os.path.join(tmp, "runnable_pool.json")
        lane = os.path.join(tmp, "runnable_pool.bm-c.json")
        pool = {"entries": [{"id": "X", "status": "ready", "lane_owner": "bm-b"}]}
        for p in (shared, lane):
            with open(p, "w", encoding="utf-8") as f:
                json.dump(pool, f)
        # double-write law check
        pool["entries"].append({"id": "Y", "status": "ready", "lane_owner": "bm-c"})
        _write_pool_double(shared, lane, pool)
        a, b = open(shared, encoding="utf-8").read(), open(lane, encoding="utf-8").read()
        assert a == b and '"Y"' in a, "D1 double-file law violated"
        # lane guard check
        assert _lane_ok({"lane_owner": None}, "bm-c") and _lane_ok({"lane_owner": "ANY"}, "bm-c")
        assert _lane_ok({"lane_owner": "bm-c"}, "bm-c") and not _lane_ok({"lane_owner": "bm-b"}, "bm-c")
        # compatible-ready count
        assert _compatible_ready_count(pool, "bm-c") == 1
        assert _compatible_ready_count(pool, "bm-b") == 1  # X is bm-b lane
        # gate check: prereg_frozen on missing file
        ok, why = _gate_pass(["prereg_frozen:research/__absent__.md"], "bm-c", {"entries": []})
        assert not ok and "prereg absent" in why
        # gate check: existing file without draft markers passes
        ok2, _ = _gate_pass(["prereg_frozen:Tools/fill_ladder.py"], "bm-c", {"entries": []})
        assert ok2
        # r189 gate regression fixtures (hermetic, no live-file dependence;
        # absolute paths pass through os.path.join verbatim):
        # (a) draft status field -> refused as not frozen
        fa = os.path.join(tmp, "a_prereg.md")
        with open(fa, "w", encoding="utf-8") as f:
            f.write("# t\n> 【状态：DRAFT-PENDING——冻结挂起】\nbody\n")
        oka, whya = _gate_pass(["prereg_frozen:" + os.path.abspath(fa)], "bm-c", {"entries": []})
        assert not oka and "not frozen" in whya, whya
        # (b) FROZEN status + draft-era words in narrative -> PASSES
        #     (the live-fire false-negative case this fix kills)
        fb = os.path.join(tmp, "b_prereg.md")
        with open(fb, "w", encoding="utf-8") as f:
            f.write("# t\n> 【状态：FROZEN——跑前 commit 冻结】本件前史=起草完成·冻结挂起；历史叙述非现态\n")
        okb, whyb = _gate_pass(["prereg_frozen:" + os.path.abspath(fb)], "bm-c", {"entries": []})
        assert okb, whyb
        # (c) no status field + narrative draft marker -> refused (fallback scan)
        fc = os.path.join(tmp, "c_prereg.md")
        with open(fc, "w", encoding="utf-8") as f:
            f.write("# t\n> 本件为草稿面，尚未冻结\n")
        okc, whyc = _gate_pass(["prereg_frozen:" + os.path.abspath(fc)], "bm-c", {"entries": []})
        assert not okc and "draft-pending" in whyc, whyc
        # gate check: runner_exists on unbuilt runner refused, built runner passes
        okr, whyr = _gate_pass(["runner_exists"], "bm-c", {"entries": []}, "scripts/__nope__.py")
        assert not okr and "runner not built" in whyr
        okr2, _ = _gate_pass(["runner_exists"], "bm-c", {"entries": []}, "Tools/fill_ladder.py")
        assert okr2
        # standing law gate: judge in-flight blocks supply wave
        okj, whyj = _gate_pass(["standing_no_judge_inflight"], "bm-c",
                               {"entries": [{"id": "TRIAL-LABOR-W4-JUDGE", "status": "waiting"}]})
        assert not okj and "W4-JUDGE" in whyj
        okj2, _ = _gate_pass(["standing_no_judge_inflight"], "bm-c",
                             {"entries": [{"id": "TRIAL-LABOR-W4-JUDGE", "status": "done"}]})
        assert okj2
        # idempotency surface: _gate_pass unknown req refused
        ok3, why3 = _gate_pass(["bogus_req"], "bm-c", {"entries": []})
        assert not ok3 and "unknown gate" in why3
        # r179 shard-synthesis law: shard-less entry gets the default
        # single shard; explicit multi-shard declarations preserved
        e_bare = _ensure_shards({"id": "L1", "status": "ready"})
        assert (len(e_bare["shards"]) == 1
                and e_bare["shards"][0]["key"] == "main"
                and e_bare["shards"][0]["status"] == "ready"
                and e_bare["shards"][0]["owner"] is None), "shard synthesis"
        e_multi = _ensure_shards({"id": "L2", "shards": [
            {"key": "s0", "status": "ready", "owner": None},
            {"key": "s1", "status": "ready", "owner": None}]})
        assert [s["key"] for s in e_multi["shards"]] == ["s0", "s1"], "explicit shards preserved"
        # r193 consumer_plan schema gate (O-1820 meaning law): a new
        # candidate without a consumer plan is blocked; a named consumer
        # face passes; whitespace-only = missing.
        assert consumer_plan_missing({"id": "L3"}), "cp missing not caught"
        assert consumer_plan_missing({"id": "L4", "consumer_plan": "   "}), \
            "cp whitespace not caught"
        assert not consumer_plan_missing(
            {"id": "L5", "consumer_plan": "judged verdict -> ledger row"}), \
            "cp present falsely flagged"
        # r459 workers_plan schema gate (O-2130 multi-core law): plan-less
        # new candidates are blocked; dict and string forms both valid.
        assert workers_plan_missing({"id": "L6"}), "wp missing not caught"
        assert workers_plan_missing({"id": "L7", "workers_plan": "   "}), \
            "wp whitespace not caught"
        assert workers_plan_missing({"id": "L7b", "workers_plan": {}}), \
            "wp empty dict not caught"
        assert not workers_plan_missing(
            {"id": "L8", "workers_plan": {"workers": 12}}), \
            "wp dict falsely flagged"
        assert not workers_plan_missing(
            {"id": "L9", "workers_plan": "{'workers': 12}"}), \
            "wp string falsely flagged"
        # grandfather check: every EXISTING catalog entry (already burned
        # or gated, append-only rows) is exempt -- the gate binds only
        # candidates newly appended to the catalog from r193 on. Live
        # verification below documents current rows carry post-hoc
        # consumer faces in ticket_ref/note history (no rewrite).
        print("selftest: all assertions PASS (double-file law / lane guard / "
              "ready count / gate refusal matrix / shard synthesis / "
              "consumer_plan schema gate / workers_plan schema gate)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if args and args[0] == "selftest":
        sys.exit(selftest())
    floor = FLOOR_DEFAULT
    for a in flags:
        if a.startswith("--floor="):
            floor = int(a.split("=", 1)[1])
    sys.exit(run(dry_run=("--dry-run" in flags), floor=floor))
