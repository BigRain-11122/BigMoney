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


# A prereg that carries one of these is a finished judgement, not supply.
# Kept deliberately short and literal: these are the words the two live
# closed rows actually use (W3 已判决关单 / W11 RETRACTED 撤回), and a wider
# vocabulary would start refusing live rows for narrative reasons.
CLOSED_MARKERS = ("已判决", "关单", "RETRACTED", "撤回", "判负终局")


def _closed_marker(text):
    """Return the closed marker found in `text`, else ''. r1381."""
    up = (text or "").upper()
    for marker in CLOSED_MARKERS:
        if marker.upper() in up:
            return marker
    return ""


def _gate_pass(gate, machine_id, pool, cand_runner=None, calendar=None):
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
                                              convention, r176 calibration;
                                              a frozen prereg whose status
                                              line marks it closed/retracted
                                              (已判决/关单/RETRACTED/撤回) is
                                              refused as DECIDED, never supply
                                              (r1381 SLOT-3 judged-negative
                                              live case)
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
                status_txt = m.group(1)
                if "FROZEN" not in status_txt.upper():
                    return False, "prereg not frozen (status=%s): %s" % (
                        status_txt[:40], p)
                # r1381: frozen is not open. A prereg whose own status line
                # says it was adjudicated closed (已判决关单 / judged-negative)
                # or retracted is a DECISION, not supply -- enqueuing it burns
                # a family whose parameters are already known to be negative.
                # Live case: INNOVATION-QUOTA-SLOT-3 (HIGHERMOM-TIMING-P1
                # judged-negative 0/3, r240) was held out of the pool only by
                # the consumer_plan schema field -- one glance at the board
                # said "add a consumer plan", which would have re-burned a
                # closed family. Status-line authority (r189) applies: the
                # narrative may mention 撤回 as history, the status field is
                # the live state.
                closed = _closed_marker(status_txt)
                if closed:
                    return False, "prereg closed (%s): %s" % (closed, p)
            else:
                closed = _closed_marker(head)
                if closed:
                    return False, "prereg closed (%s): %s" % (closed, p)
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
        elif req.startswith("calendar_admitted:"):
            # r1422: a candidate book the desk already judged and refused by its
            # own calendar must not be offered to the supply floor as "startable
            # today" -- the same defect class as the r1381 closed-family refusal,
            # one layer up. Only the literal word ADMIT passes; a book no receipt
            # declares is UNJUDGED, which is not admitted either (r98: unknown is
            # not empty, and unknown is not a pass).
            book = req.split(":", 1)[1].strip()
            cal = calendar if calendar is not None else _calendar_block()
            if cal.get("verdict") == "UNKNOWN":
                return False, "calendar face unreadable (unknown is not admitted): %s" % book
            rows = [r for r in (cal.get("candidates") or []) if r.get("candidate") == book]
            if not rows:
                return False, "book not declared in any calendar receipt " \
                              "(unjudged is not admitted): %s" % book
            row = rows[0]
            if not row.get("pass"):
                return False, "calendar refused %s (%s via %s)" % (
                    book, row.get("state"),
                    ", ".join(row.get("failing_checks") or []) or "no named check")
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


def runner_args_missing(cand):
    """r459 bm-a repair-2 third-face root fix (泊位登记三验 pit law
    mechanized): SLOT-6 first launch ran the runner bare -> argparse
    no-cmd exit 2 (r444 no-arg-leg family; W12-JUDGE ['judge', ...]
    convention is the house form). New candidates must carry runner_args
    as a non-empty LIST of non-empty strings -- deliberately stricter
    than the workers_plan both-forms gate: the launch face splats
    (*runner_args), so a bare string would splat per-character into a
    bogus command line. Same append-only grandfather scope."""
    ra = cand.get("runner_args")
    if not isinstance(ra, (list, tuple)):
        return True
    if not ra:
        return True
    return any(not str(a).strip() for a in ra)


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


FACE_PATH = os.path.join(ROOT, "results", "fill_ladder_face.json")


def _pool_entry_map(pool):
    return {(e.get("id") or ""): e for e in (pool or {}).get("entries", [])}


def _classify(cand, machine_id, pool, existing):
    """One catalog row -> (class, reason).

    Classes: spent / lane_foreign / blocked / available. The gate chain is the
    one run() applies, in the same order and with the same grandfather boundary
    (a row already in the pool is spent, never re-judged on schema), so this
    face cannot drift from the tool it reports on (single implementation, E289).
    """
    cid = cand.get("id") or ""
    if cid in existing:
        e = existing[cid]
        return "spent", "in pool as %s (entered %s)" % (
            e.get("status"), e.get("entered_at") or "?")
    if not _lane_ok(cand, machine_id):
        return "lane_foreign", "lane_owner=%s" % cand.get("lane_owner")
    ok, why = _gate_pass(cand.get("enqueue_gates"), machine_id, pool,
                         cand.get("runner"))
    if not ok:
        return "blocked", why
    if consumer_plan_missing(cand):
        return "blocked", "consumer_plan missing (O-1820 meaning law)"
    if workers_plan_missing(cand):
        return "blocked", "workers_plan missing (O-2130 multi-core law)"
    if runner_args_missing(cand):
        return "blocked", "runner_args missing (r444 no-arg-leg family)"
    return "available", ""


def _verdict_of_counts(counts):
    """Pure. 'nothing left to offer' and 'everything is gated' are opposite
    repair actions (write a prereg vs unblock a row) and run() printed the same
    sentence for both."""
    if counts.get("available"):
        return "SUPPLY_AVAILABLE"
    if not counts.get("catalog"):
        return "CATALOG_EMPTY"
    if counts.get("blocked") and not counts.get("spent") and not counts.get("lane_foreign"):
        return "ALL_ROWS_BLOCKED"
    return "EXHAUSTED_NO_LAWFUL_SUPPLY"


def _calendar_block():
    """The other half of "why is the floor red": the desk may hold candidates
    and every one of them was refused by its own calendar (r1421
    supply_calendar_face). Imported, never re-derived; an unreadable face is
    UNKNOWN, which is not "no candidates" (r98)."""
    sdir = os.path.join(ROOT, "scripts")
    try:
        if sdir not in sys.path:
            sys.path.insert(0, sdir)
        import supply_calendar_face as scf
        face = scf.build()
        return {
            "verdict": face.get("verdict"),
            "n_candidates": face.get("n_candidates"),
            "n_refused": face.get("n_refused"),
            "reading": face.get("reading"),
            "candidates": [
                {"candidate": r.get("candidate"), "state": r.get("state"),
                 "pass": bool(r.get("pass")),
                 "failing_checks": r.get("failing_checks") or []}
                for r in (face.get("candidates") or [])],
            # r1432: the reason a book was refused now comes from the ruler the
            # desk elected (r1431), not from the one r1426 disqualified; the
            # ladder prints it so "no lawful supply" also says why.
            "elected_ruler": face.get("elected_ruler"),
            "elected_reasons": face.get("elected_reasons") or [],
            # r1434: "refused at <ruler> median 2" is meaningless to an operator
            # unless the board also says whether that 2 moves when the window
            # moves. Carried as the face's own re-derived sentence; a face
            # without one prints nothing (exploratory probe, decides nothing).
            "window_sensitivity": (
                (face.get("window_sensitivity") or {}).get("sentence") or ""),
        }
    except Exception as exc:  # unreadable is not empty
        return {"verdict": "UNKNOWN",
                "reading": "calendar face unreadable: %s: %s" % (
                    type(exc).__name__, exc)}


def _explain_line(face):
    c = face["counts"]
    cal = face.get("calendar") or {}
    line = ("[ladder-face] ready=%d floor=%d | catalog %d rows: spent %d / blocked %d "
            "/ lane_foreign %d / available %d -> %s | calendar: %s (%s candidates, "
            "%s refused)" % (
                face["compatible_ready"], face["floor"], c["catalog"], c["spent"],
                c["blocked"], c["lane_foreign"], c["available"], face["verdict"],
                cal.get("verdict"), cal.get("n_candidates"), cal.get("n_refused")))
    if cal.get("elected_reasons"):
        line += " | reason (%s): %s" % (cal.get("elected_ruler") or "no election",
                                        "; ".join(cal["elected_reasons"]))
    if cal.get("window_sensitivity"):
        line += " | " + cal["window_sensitivity"]
    return line


def explain(machine_id=None, dry_run=False, out_path=None):
    """FACE (not a gate): classify every catalog row and join the calendar face.

    Why this exists: the pool has read `ready 0 < floor 3` for thirty rounds
    while run() printed at most one blocked row per tick. `existing_ids`
    idempotency silently drops every already-burned row from the report, so a
    catalog that is fully SPENT and one that is fully BLOCKED print the same
    sentence ("stands until preregs land") -- and only one of them is fixed by
    writing a prereg. r1199's rule (a red that cannot be acted on is not a
    flag) one layer up.
    """
    machine_id = machine_id or _machine_id()
    shared_path, _lane_path = _pool_paths(machine_id)
    pool = _merged_pool_view(shared_path)
    existing = _pool_entry_map(pool)
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    rows = []
    for cand in catalog.get("entries", []):
        cls, why = _classify(cand, machine_id, pool, existing)
        rows.append({"id": cand.get("id"), "class": cls, "reason": why})
    counts = {k: sum(1 for r in rows if r["class"] == k)
              for k in ("spent", "blocked", "lane_foreign", "available")}
    counts["catalog"] = len(rows)
    face = {
        "tool": "fill_ladder explain",
        "generated_at": _now(),
        "machine_id": machine_id,
        "floor": FLOOR_DEFAULT,
        "compatible_ready": _compatible_ready_count(pool, machine_id),
        "pool_entries": len(pool.get("entries", [])),
        "verdict": _verdict_of_counts(counts),
        "counts": counts,
        "rows": rows,
        "calendar": _calendar_block(),
    }
    print(_explain_line(face))
    if not dry_run:
        path = out_path or FACE_PATH
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        os.replace(tmp, path)
    for r in rows:
        if r["class"] != "spent":
            print("[ladder-face]   %s: %s (%s)" % (r["id"], r["class"], r["reason"]))
    return 0


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
    spent_n = sum(1 for cand in catalog.get("entries", []) if cand["id"] in existing_ids)
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
        if runner_args_missing(cand):
            blocked.append((cid, "runner_args missing (r444 no-arg-leg "
                                "family: first launch argparse no-cmd exit 2 "
                                "-- W12-JUDGE ['judge', ...] house form; "
                                "r459 SLOT-6 repair-2 live-fire)"))
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
              "floor breach %d<%d stands until preregs land (%d of %d catalog rows "
              "are already in the pool; `explain` names every row's class)"
              % (ready_n, floor, spent_n, len(catalog.get("entries", []))))
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
        # r1381 closed-family refusal: a FROZEN prereg whose status line says
        # the family was adjudicated closed or retracted is a decision, not
        # supply. Three legs: (d) judged-negative status refused, (e) RETRACTED
        # status refused, (f) narrative mention of 撤回 under a FROZEN status
        # still passes (r189 status-line authority -- history is not state).
        fd = os.path.join(tmp, "d_prereg.md")
        with open(fd, "w", encoding="utf-8") as f:
            f.write("# t\n> 状态：**已判决关单（judged-negative 0/3）**\nbody\n")
        okd, whyd = _gate_pass(["prereg_frozen:" + os.path.abspath(fd)], "bm-c", {"entries": []})
        assert not okd and "prereg closed" in whyd, whyd
        fe = os.path.join(tmp, "e_prereg.md")
        with open(fe, "w", encoding="utf-8") as f:
            f.write("# t\n> **状态：RETRACTED（撤回·烧前反重复拦截）**\nbody\n")
        oke, whye = _gate_pass(["prereg_frozen:" + os.path.abspath(fe)], "bm-c", {"entries": []})
        assert not oke and "prereg closed" in whye, whye
        ff = os.path.join(tmp, "f_prereg.md")
        with open(ff, "w", encoding="utf-8") as f:
            f.write("# t\n> 【状态：FROZEN——跑前冻结】前史：同族曾撤回一次，本件为独立新族\n")
        okf, whyf = _gate_pass(["prereg_frozen:" + os.path.abspath(ff)], "bm-c", {"entries": []})
        assert okf, whyf
        # live anchor: the row that starved nothing and would have re-burned a
        # closed family is refused for the RIGHT reason (not for schema).
        okl, whyl = _gate_pass(["prereg_frozen:research/INNOVATION_QUOTA_W3_PREREG.md"],
                              "bm-c", {"entries": []})
        assert not okl and "prereg closed" in whyl, whyl
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
        # r460 runner_args schema gate (r444 no-arg-leg family root fix):
        # missing / empty list / bare string (splat-per-char hazard) /
        # whitespace element all blocked; proper list passes.
        assert runner_args_missing({"id": "L10"}), "ra missing not caught"
        assert runner_args_missing({"id": "L11", "runner_args": []}), \
            "ra empty list not caught"
        assert runner_args_missing({"id": "L12", "runner_args": "run"}), \
            "ra bare string not caught (splat-per-char hazard)"
        assert runner_args_missing(
            {"id": "L13", "runner_args": ["run", "  "]}), \
            "ra whitespace element not caught"
        assert not runner_args_missing({"id": "L14", "runner_args": ["run"]}), \
            "ra proper list falsely flagged"
        assert not runner_args_missing(
            {"id": "L15", "runner_args": ["judge", "--shard", "0"]}), \
            "ra multi-arg list falsely flagged"
        # grandfather check: every EXISTING catalog entry (already burned
        # or gated, append-only rows) is exempt -- the gate binds only
        # candidates newly appended to the catalog from r193 on. Live
        # verification below documents current rows carry post-hoc
        # consumer faces in ticket_ref/note history (no rewrite).
        # r1422 explain() legs: a fully SPENT catalog and a fully BLOCKED one
        # must not read the same -- that identity is the defect this face
        # makes visible (run()'s idempotency drops spent rows from its report,
        # so thirty rounds of `ready 0 < floor 3` printed one blocked row and
        # said "stands until preregs land" either way).
        e_spent = {"id": "S1"}
        e_free = {"id": "S2", "enqueue_gates": [],
                  "consumer_plan": "judged verdict -> ledger row",
                  "workers_plan": {"workers": 4}, "runner_args": ["run"]}
        e_blocked = {"id": "S3",
                     "enqueue_gates": ["prereg_frozen:research/__absent__.md"]}
        e_foreign = {"id": "S4", "lane_owner": "bm-b", "enqueue_gates": [],
                     "consumer_plan": "x", "workers_plan": {"workers": 2},
                     "runner_args": ["run"]}
        pool_fx = {"entries": [{"id": "S1", "status": "done",
                               "entered_at": "2026-09-01 00:00:00"}]}
        existing_fx = _pool_entry_map(pool_fx)
        c_spent, w_spent = _classify(e_spent, "bm-c", pool_fx, existing_fx)
        assert c_spent == "spent" and "in pool as done" in w_spent, w_spent
        assert _classify(e_free, "bm-c", pool_fx, existing_fx)[0] == "available"
        assert _classify(e_blocked, "bm-c", pool_fx, existing_fx)[0] == "blocked"
        assert _classify(e_foreign, "bm-c", pool_fx, existing_fx)[0] == "lane_foreign"
        # grandfather boundary: schema-less row already in the pool is spent,
        # never "blocked by schema" -- run() skips it for the same reason.
        pool_bare = {"entries": [{"id": "S5", "status": "done"}]}
        assert _classify({"id": "S5"}, "bm-c", pool_bare,
                         _pool_entry_map(pool_bare))[0] == "spent"
        # a schema-less row NOT in the pool is blocked (the gate that binds new
        # candidates only -- the boundary has to cut on both sides)
        assert _classify({"id": "S6", "enqueue_gates": []}, "bm-c",
                         {"entries": []}, {})[0] == "blocked"
        # verdict words: an exhausted catalog is not an unblockable one
        assert _verdict_of_counts({"catalog": 3, "spent": 3, "blocked": 0,
                                   "lane_foreign": 0, "available": 0}) == \
            "EXHAUSTED_NO_LAWFUL_SUPPLY"
        assert _verdict_of_counts({"catalog": 2, "spent": 0, "blocked": 2,
                                   "lane_foreign": 0, "available": 0}) == \
            "ALL_ROWS_BLOCKED"
        assert _verdict_of_counts({"catalog": 0, "spent": 0, "blocked": 0,
                                   "lane_foreign": 0, "available": 0}) == \
            "CATALOG_EMPTY"
        assert _verdict_of_counts({"catalog": 1, "spent": 0, "blocked": 0,
                                   "lane_foreign": 0, "available": 1}) == \
            "SUPPLY_AVAILABLE"
        # calendar join speaks only the frozen vocabulary (unknown is a word,
        # never silently "no candidates")
        cal = _calendar_block()
        assert cal.get("verdict") in ("ADMITTED_CANDIDATE_EXISTS",
                                      "NO_CANDIDATE_PASSES_CALENDAR",
                                      "NO_CANDIDATES", "UNKNOWN"), cal
        # one-line summary must carry both halves, else the reader cannot tell
        # "write a prereg" from "wait for a year of evidence"
        line = _explain_line({"compatible_ready": 0, "floor": 3,
                              "counts": {"catalog": 23, "spent": 22, "blocked": 1,
                                         "lane_foreign": 0, "available": 0},
                              "verdict": "EXHAUSTED_NO_LAWFUL_SUPPLY",
                              "calendar": {"verdict": "NO_CANDIDATE_PASSES_CALENDAR",
                                           "n_candidates": 4, "n_refused": 4}})
        assert "spent 22" in line and "NO_CANDIDATE_PASSES_CALENDAR" in line, line
        # r1434: the board must also answer "does that number move if the window
        # moves" whenever the calendar face carries the exploratory window note --
        # and must print nothing when it does not (an absent probe is not a pass).
        line_w = _explain_line({"compatible_ready": 0, "floor": 3,
                                "counts": {"catalog": 23, "spent": 22, "blocked": 1,
                                           "lane_foreign": 0, "available": 0},
                                "verdict": "EXHAUSTED_NO_LAWFUL_SUPPLY",
                                "calendar": {
                                    "verdict": "NO_CANDIDATE_PASSES_CALENDAR",
                                    "n_candidates": 4, "n_refused": 4,
                                    "window_sensitivity": "window: SENTINEL-READING"}})
        assert "window: SENTINEL-READING" in line_w, line_w
        assert "window:" not in line, line
        # r1422 calendar_admitted gate: the supply floor must never be offered a
        # book the desk already refused by its own calendar, and an UNJUDGED book
        # is not admitted either. Four legs, injected calendar (hermetic):
        cal_admit = {"verdict": "ADMITTED_CANDIDATE_EXISTS", "candidates": [
            {"candidate": "BOOK-A", "state": "ADMIT", "pass": True,
             "failing_checks": []}]}
        okca, _ = _gate_pass(["calendar_admitted:BOOK-A"], "bm-c", {"entries": []},
                             None, cal_admit)
        assert okca, "admitted book must pass the calendar gate"
        cal_refuse = {"verdict": "NO_CANDIDATE_PASSES_CALENDAR", "candidates": [
            {"candidate": "BOOK-B", "state": "CONDITIONAL", "pass": False,
             "failing_checks": ["Y4_top2_share"]}]}
        okcr, whycr = _gate_pass(["calendar_admitted:BOOK-B"], "bm-c",
                                 {"entries": []}, None, cal_refuse)
        assert not okcr and "calendar refused" in whycr and "Y4_top2_share" in whycr, whycr
        okcu, whycu = _gate_pass(["calendar_admitted:BOOK-B"], "bm-c",
                                 {"entries": []}, None,
                                 {"verdict": "UNKNOWN", "candidates": []})
        assert not okcu and "unreadable" in whycu, whycu
        okcn, whycn = _gate_pass(["calendar_admitted:BOOK-C"], "bm-c",
                                 {"entries": []}, None, cal_refuse)
        assert not okcn and "not declared" in whycn, whycn
        print("selftest: all assertions PASS (double-file law / lane guard / "
              "ready count / gate refusal matrix / shard synthesis / "
              "consumer_plan schema gate / workers_plan schema gate / "
              "runner_args schema gate / r1422 explain class matrix + "
              "verdict words + calendar join + calendar_admitted gate)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if args and args[0] == "selftest":
        sys.exit(selftest())
    if args and args[0] == "explain":
        sys.exit(explain(dry_run=("--dry-run" in flags)))
    floor = FLOOR_DEFAULT
    for a in flags:
        if a.startswith("--floor="):
            floor = int(a.split("=", 1)[1])
    sys.exit(run(dry_run=("--dry-run" in flags), floor=floor))
