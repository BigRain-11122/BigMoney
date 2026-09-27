"""Merge lane views: A-family deterministic reader merger (D-20260928-03 batch-1).

Group decision D-20260928-03(1) lane migration, batch-1 execution piece:
per-machine lane files ``results/<face>.<machine>.json`` are the structural
end-state; consumers (dashboard / daily_report / aggregators) read a
DETERMINISTIC MERGED VIEW instead of one shared blob.  This module is that
reader: it unions lane files + the legacy shared file with the SAME laws the
conflict-resolver skill uses live (rolling-ledger ts-key union, whole-row
identity union, autofill cap50/asc, pool done-absorption + governance
non-null-first r370 pit-law, post_review id-union with newer-reconcile wins).

Source order is FIXED (legacy shared file first, then lane files bm-a/bm-b/
bm-c) so every machine derives the byte-identical merged view from the same
inputs -- no new shared writable face is created (merge prints, never writes
repo files; consumers import this as a library at switch time).

Faces (A-family, LANE_MIGRATION_S1 census):
  compute_audit | regime_state | autofill_state | runnable_pool
  gate_attrition | post_review_criteria
Faces (B-family, batch-2 census):
  update_status | heat_update_status | lhb_update_status
  futures_update_status | fundamental_status | token_usage
  crash_fuse | market_clock/call_latest

Usage:
  python scripts/merge_lane_views.py merge [--face F]     # merged-view summary
  python scripts/merge_lane_views.py reconcile [--face F] # vs shared file
  python scripts/merge_lane_views.py selftest             # offline fixtures

Exit codes: 0 ok / 1 reconcile drift (or selftest fail) / 2 mechanism fault.
Zero network, zero engine, L1 deterministic; fail-closed on shape surprises.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402

A_FACES = ("compute_audit", "regime_state", "autofill_state",
           "runnable_pool", "gate_attrition", "post_review_criteria")
MACHINES = ("bm-a", "bm-b", "bm-c")
# r370 pit-law: resolver/union may swallow the OTHER machine's in-tree fixes
# for governance fields -- non-empty-first with annotation, never blind-pick.
GOVERNANCE_FIELDS = ("lane_owner", "lane_note", "claimed_by", "claimed_at",
                     "claim_note", "yield_note")
_RECON_TS = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


def _row_id(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def _lane_path(face, machine):
    return os.path.join(PATHS.results_dir, f"{face}.{machine}.json")


def _merge_shard_same_key(a, b):
    """Same-key shard rows: the row with the newer ``owner_since`` is
    the base (r311 latest.ts deep-probe law); fields missing on the
    base fill from the other side (r370 non-null-first family; ts ties
    resolve deterministically to the first side)."""
    ta, tb = str(a.get("owner_since", "")), str(b.get("owner_since", ""))
    base, other = (a, b) if ta >= tb else (b, a)
    out = dict(base)
    for k, v in other.items():
        if out.get(k) in (None, "") and v not in (None, ""):
            out[k] = v
    return out


def _union_shard_rows(ra, rb):
    """Shard rows unioned by shard ``key`` (identity), not whole-row.

    A stale lane snapshot and the living shared face legitimately
    differ on time-varying shard fields (owner_since/checkpoint) --
    whole-row union turned that lag into duplicate rows (r373
    reconcile drift catch on DECISION-CHAIN-V2-P1 / CENSUS-FUS-S2-W2A).
    Same-key rows merge via _merge_shard_same_key; keyless rows keep
    the whole-row append-log union (no identity -> no merge key);
    same-key duplicates within one side self-heal into the first
    occurrence.  Base order preserved (append-log law)."""
    out = list(ra)
    have = {}
    for i, row in enumerate(out):
        k = row.get("key")
        if k is not None and k not in have:
            have[k] = i
    seen_keyless = {_row_id(x) for x in out if x.get("key") is None}
    for row in rb:
        k = row.get("key")
        if k is None:
            rid = _row_id(row)
            if rid not in seen_keyless:
                seen_keyless.add(rid)
                out.append(row)
            continue
        if k in have:
            i = have[k]
            out[i] = _merge_shard_same_key(out[i], row)
        else:
            have[k] = len(out)
            out.append(row)
    return out


def _shared_path(face):
    return os.path.join(PATHS.results_dir, f"{face}.json")


def load_sources(face):
    """Fixed-order sources: legacy shared blob first, then lane files.

    Each lane file may self-sign with a top-level ``lane_machine`` field;
    a signature contradicting the filename is fail-closed (r98 identity
    lesson: never guess machine identity from stale content)."""
    sources = []
    shared = _shared_path(face)
    if os.path.exists(shared):
        with open(shared, encoding="utf-8") as fh:
            sources.append(("legacy", json.load(fh)))
    for machine in MACHINES:
        p = _lane_path(face, machine)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                data = json.load(fh)
            signed = data.get("lane_machine")
            if signed is not None and signed != machine:
                raise SystemExit(
                    f"merge_lane_views: lane_machine={signed!r} contradicts "
                    f"filename {p!r} -- fail-closed (r98 identity law)")
            # lane_machine is a signature, not face data: strip it on
            # load so the merged view stays comparable with the shared
            # file (reconcile would false-red on the extra key as soon
            # as real lane files exist).
            if isinstance(data, dict):
                data = {k: v for k, v in data.items() if k != "lane_machine"}
            sources.append((machine, data))
    return sources


def _deep_ts(d, *keys):
    """Existence-checked nested ts probe (r311/r319: top-level miss != no ts;
    comparing a missing path is always-false, probe existence first)."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return ""
        cur = cur[k]
    return str(cur)


def _flat_winner(sources, probe):
    """Index of the source whose probe ts is newest; ties -> first-seen."""
    best, best_ts = 0, ""
    for i, (_label, data) in enumerate(sources):
        ts = probe(data)
        if ts > best_ts:
            best, best_ts = i, ts
    return best


def _union_rows(base_rows, extra_rows):
    """Whole-row identity union, base order preserved (append-log law)."""
    seen = {_row_id(x) for x in base_rows}
    return list(base_rows) + [x for x in extra_rows
                             if _row_id(x) not in seen]


def merge_compute_audit(sources):
    out, notes = {}, []
    base_rows, seen_ts = [], set()
    for _label, data in sources:
        for h in data.get("history", []):
            ts = str(h.get("ts", ""))
            if ts not in seen_ts:
                seen_ts.add(ts)
                base_rows.append(h)
    base_rows.sort(key=lambda h: str(h.get("ts", "")))
    # state fields: whole-side take by deep ts probe latest.ts (r311 live:
    # top-level scan misses the nested latest.ts truth)
    win = _flat_winner(sources, lambda d: _deep_ts(d, "latest", "ts"))
    for k, v in sources[win][1].items():
        if k != "history":
            out[k] = v
    out["history"] = base_rows
    notes.append(f"history ts-key union -> {len(base_rows)} rows; "
                 f"state fields from {sources[win][0]} (latest.ts probe)")
    return out, notes


def merge_regime_state(sources):
    notes = []
    win = _flat_winner(sources, lambda d: str(d.get("updated", "")))
    out = dict(sources[win][1])
    merged_lists = {}
    for k in ("triggers", "transitions", "history"):
        rows = []
        for _label, data in sources:
            rows = _union_rows(rows, data.get(k, []))
        merged_lists[k] = rows
        if len(sources) > 1:
            notes.append(f"{k}: whole-row union -> {len(rows)}")
    out.update(merged_lists)
    notes.append(f"flat fields from {sources[win][0]} (updated probe)")
    return out, notes


def merge_autofill_state(sources):
    notes = []
    rows = []
    for _label, data in sources:
        rows = _union_rows(rows, data.get("launches", []))
    rows.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
    dropped = max(0, len(rows) - 50)
    rows = rows[:50]
    rows.sort(key=lambda x: str(x.get("ts", "")))  # r245: write asc
    out = {"launches": rows}
    # last_tick: internal-ts dict compare, never str() the whole dict (r140)
    best, best_ts = None, ""
    for label, data in sources:
        lt = data.get("last_tick")
        if not isinstance(lt, dict):
            continue
        ts = str(lt.get("ts", ""))
        if ts > best_ts:
            best, best_ts = lt, ts
    if best is not None:
        out["last_tick"] = best
    assert isinstance(out.get("last_tick", {}), dict), \
        "last_tick must stay dict (r140 law)"
    notes.append(f"launches identity-union -> {len(rows)} kept "
                 f"({dropped} beyond cap50 dropped as newest-50 semantics); "
                 f"last_tick ts={best_ts!r}")
    return out, notes


def _merge_pool_entry(a, b, notes, label_a, label_b):
    """r312 done-absorption + r370 governance non-null-first, field-annotated."""
    if a.get("status") == "done" or b.get("status") == "done":
        done, other = (a, b) if a.get("status") == "done" else (b, a)
        out = dict(done)
        for f in GOVERNANCE_FIELDS:
            if not out.get(f) and other.get(f):
                out[f] = other[f]
                notes.append(f"entry {a.get('id')}: done-absorb + "
                             f"governance {f} from "
                             f"{label_b if done is a else label_a}")
        return out
    if a.get("status") == b.get("status"):
        out = dict(a)
        for f in GOVERNANCE_FIELDS:  # non-empty-first across sides
            if not out.get(f) and b.get(f):
                out[f] = b[f]
                notes.append(f"entry {a.get('id')}: governance {f} "
                             f"non-null-first from {label_b}")
        sa, sb = a.get("shards"), b.get("shards")
        if isinstance(sa, list) or isinstance(sb, list):
            rows = _union_shard_rows(sa or [], sb or [])
            out["shards"] = rows
            notes.append(f"entry {a.get('id')}: shards key-union "
                         f"-> {len(rows)}")
        for k, v in b.items():
            if k not in out or (out[k] in (None, "") and v not in (None, "")):
                out[k] = v
        return out
    # differing non-done statuses: keep the further-along side (done already
    # handled; ready/waiting mix -> prefer ready), annotate the divergence
    rank = {"ready": 2, "waiting": 1}
    out = dict(a if rank.get(a.get("status"), 0) >=
               rank.get(b.get("status"), 0) else b)
    notes.append(f"entry {a.get('id')}: status {a.get('status')!r} vs "
                 f"{b.get('status')!r} -> kept {out.get('status')!r}")
    return out


def merge_runnable_pool(sources):
    notes = []
    by_id, order = {}, []
    for label, data in sources:
        for e in data.get("entries", []):
            eid = e.get("id")
            if eid not in by_id:
                by_id[eid] = (e, label)
                order.append(eid)
            else:
                prev, prev_label = by_id[eid]
                by_id[eid] = (_merge_pool_entry(prev, e, notes,
                                                prev_label, label), label)
    win = _flat_winner(sources, lambda d: str(d.get("updated_at", "")))
    out = dict(sources[win][1])
    out["entries"] = [by_id[eid][0] for eid in order]
    notes.append(f"entries id-union -> {len(order)} (done-absorption + "
                 f"governance non-null-first); meta from {sources[win][0]}")
    return out, notes


def merge_gate_attrition(sources):
    notes = []
    rows_entries, rows_history = [], []
    for _label, data in sources:
        rows_entries = _union_rows(rows_entries, data.get("entries", []))
        rows_history = _union_rows(rows_history, data.get("history", []))
    # flat keys from the source holding the newest ledger row (constants are
    # stable in practice; this stays deterministic and freshness-ordered)
    def _max_row_ts(d):
        ts = ""
        for r in d.get("entries", []) + d.get("history", []):
            ts = max(ts, str(r.get("ts", "")))
        return ts
    win = _flat_winner(sources, _max_row_ts)
    out = dict(sources[win][1])
    out["entries"] = rows_entries
    out["history"] = rows_history
    notes.append(f"entries -> {len(rows_entries)}, history -> "
                 f"{len(rows_history)} (whole-row identity union, full-volume "
                 f"semantics preserved for the 47 consumers); flat from "
                 f"{sources[win][0]}")
    return out, notes


def merge_post_review_criteria(sources):
    notes = []

    def _ts(s):
        m = _RECON_TS.search(str(s.get("_reconciled", "")))
        return m.group(1) if m else ""

    # deterministic explicit scan for the newer _reconciled side
    best, best_ts = 0, ""
    for i, (_label, data) in enumerate(sources):
        ts = _ts(data)
        if ts > best_ts:
            best, best_ts = i, ts
    base = dict(sources[best][1])
    items = {it["id"]: dict(it) for it in base.get("items", [])}
    for i, (label, data) in enumerate(sources):
        if i == best:
            continue
        added = 0
        for it in data.get("items", []):
            if it["id"] not in items:
                items[it["id"]] = dict(it)
                added += 1
        if added:
            notes.append(f"+{added} items from {label}")
    base["items"] = list(items.values())
    notes.append(f"items id-union -> {len(items)}; collision winner side = "
                 f"{sources[best][0]} (newer _reconciled ts {best_ts!r})")
    return base, notes


MERGERS = {
    "compute_audit": merge_compute_audit,
    "regime_state": merge_regime_state,
    "autofill_state": merge_autofill_state,
    "runnable_pool": merge_runnable_pool,
    "gate_attrition": merge_gate_attrition,
    "post_review_criteria": merge_post_review_criteria,
}


# ---------------------------------------------------------------------------
# B-family (batch-2, LANE_MIGRATION_S1 census): per-machine gate / meter
# status snapshots.  Census-frozen merge semantics = max-cutoff freshness,
# with two lawful exceptions:
#   * heat_update_status: R31 lane-ownership precedent -- snapshots derive
#     from the host's machine-local data/heat face (gitignored), so a
#     fresher non-host no-op write is NOT authoritative (ts新 != 数据权威新).
#   * crash_fuse: per-runner sig key union with newer-event-wins (the fuse
#     is an append/monotone-counter face, never a last-writer blob).
# ---------------------------------------------------------------------------

B_FACES = ("update_status", "heat_update_status", "lhb_update_status",
           "futures_update_status", "fundamental_status", "token_usage",
           "crash_fuse", "market_clock/call_latest")

_HEAT_HOST = "bm-a"   # R19 wiring / R31 resolver verdict lineage


def _make_take_new(face, probe):
    """Max-cutoff whole-dict take (census B recipe): the source whose
    ``probe`` ts is newest wins wholesale; ties -> first-seen (= legacy
    at bootstrap, so single-source reconcile stays zero-drift even when
    the probe key is absent)."""
    def _merge(sources):
        win = _flat_winner(sources, lambda d: str(d.get(probe, "")))
        return (dict(sources[win][1]),
                [f"max-cutoff take by {probe!r} from {sources[win][0]} "
                 f"({len(sources)} source(s))"])
    return _merge


def merge_heat_update_status(sources):
    """Host-lane priority (R31): the heat host's lane IS the authority;
    max-cutoff only before the host lane exists (pre-wiring rounds)."""
    for label, data in sources:
        if label == _HEAT_HOST:
            return (dict(data),
                    [f"host-lane priority from {_HEAT_HOST} (R31 authority "
                     f"law); {len(sources)} source(s) scanned"])
    return _make_take_new("heat_update_status", "updated")(sources)


def merge_crash_fuse(sources):
    notes = []

    def _sig_ts(sig):
        if not isinstance(sig, dict):
            return ""
        return max(str(sig.get("last_crash_ts", "")),
                   str(sig.get("last_refusal_ts", "")))

    def _max_sig_ts(d):
        best = ""
        for sig in d.get("sigs", {}).values():
            best = max(best, _sig_ts(sig))
        return best

    win = _flat_winner(sources, _max_sig_ts)
    out = dict(sources[win][1])
    sigs = {}
    for label, data in sources:
        for key, sig in data.get("sigs", {}).items():
            if key not in sigs:
                sigs[key] = sig
                continue
            if _sig_ts(sig) > _sig_ts(sigs[key]):
                sigs[key] = sig
                notes.append(f"sig {key!r}: newer event from {label}")
    out["sigs"] = sigs
    notes.append(f"sigs key-union -> {len(sigs)} runner sig(s), same-key "
                 f"newer-event-wins; flat from {sources[win][0]}")
    return out, notes


MERGERS.update({
    "update_status": _make_take_new("update_status", "updated"),
    "lhb_update_status": _make_take_new("lhb_update_status", "updated"),
    "futures_update_status": _make_take_new("futures_update_status", "ts"),
    "fundamental_status": _make_take_new("fundamental_status", "updated"),
    "token_usage": _make_take_new("token_usage", "generated"),
    "market_clock/call_latest": _make_take_new("market_clock/call_latest",
                                               "asof"),
    "heat_update_status": merge_heat_update_status,
    "crash_fuse": merge_crash_fuse,
})

ALL_FACES = A_FACES + B_FACES


def merge_face(face, sources):
    if face not in MERGERS:
        raise SystemExit(f"merge_lane_views: unknown face {face!r} "
                         f"(ALL_FACES={ALL_FACES}) -- fail-closed")
    if not sources:
        raise SystemExit(f"merge_lane_views: face {face!r} has no sources")
    return MERGERS[face](sources)


def _cmd_merge(faces):
    for face in faces:
        sources = load_sources(face)
        merged, notes = merge_face(face, sources)
        print(f"[{face}] sources={[s[0] for s in sources]}")
        for n in notes:
            print(f"  - {n}")
    return 0


def _cmd_reconcile(faces):
    drift = []
    for face in faces:
        sources = load_sources(face)
        if not any(lbl == "legacy" for lbl, _ in sources):
            print(f"[{face}] SKIP: no legacy shared file to reconcile "
                  f"against (lane-only face)")
            continue
        merged, _notes = merge_face(face, sources)
        shared = dict(next(d for lbl, d in sources if lbl == "legacy"))
        if merged == shared:
            print(f"[{face}] ZERO-DRIFT (merged view == shared file, "
                  f"{len(sources)} source(s))")
        else:
            drift.append(face)
            print(f"[{face}] DRIFT DETECTED vs shared file -- full diff "
                  f"required before any switch (D-03 batch gate)")
    if drift:
        print(f"reconcile: {len(drift)} face(s) with drift: {drift}")
        return 1
    print("reconcile: all faces zero-drift")
    return 0


def _selftest():
    fails = []

    def check(name, cond):
        print(f"  [{name}] {'PASS' if cond else 'FAIL'}")
        if not cond:
            fails.append(name)

    # 1. bootstrap identity: single source -> unchanged, all six faces
    shared = {
        "compute_audit": {"latest": {"ts": "2026-09-28 01:40:02",
                                      "py_cpu_pct": 0.2},
                           "history": [{"ts": "2026-09-28 01:40:02",
                                        "py_cpu_pct": 0.2}]},
        "regime_state": {"updated": "2026-09-28 01:50:38", "state": "ORANGE",
                         "triggers": ["a", "b"],
                         "history": [{"asof": "2026-09-24", "raw": "ORANGE"}],
                         "transitions": []},
        "autofill_state": {"last_tick": {"ts": "2026-09-28 01:40:02",
                                          "machine": "bm-a"},
                           "launches": [{"ts": f"2026-09-28 01:{i:02d}:02"}
                                        for i in range(50)]},
        "runnable_pool": {"updated_at": "2026-09-28 00:41:57",
                          "entries": [{"id": "X", "status": "ready",
                                       "lane_owner": "bm-b"}]},
        "gate_attrition": {"schema": "gate-attrition-ledger v1",
                           "entries": [{"batch": "B1", "ts":
                                        "2026-09-24 03:03:01"}],
                           "history": []},
        "post_review_criteria": {"_law": "frozen",
                                  "_reconciled": "2026-09-24 21:43:10 r71",
                                  "items": [{"id": "P-1", "status": "YES"}]},
    }
    for face in A_FACES:
        merged, _ = merge_face(face, [("legacy", shared[face])])
        check(f"bootstrap-identity:{face}", merged == shared[face])

    # 2. compute_audit: history ts-key union zero-loss + nested latest probe
    a = {"latest": {"ts": "01:00:00", "py_cpu_pct": 1.0},
         "history": [{"ts": "01:00:00"}, {"ts": "00:30:00"}]}
    b = {"latest": {"ts": "01:20:00", "py_cpu_pct": 0.3},
         "history": [{"ts": "01:20:00"}, {"ts": "01:00:00"}]}
    m, _ = merge_compute_audit([("bm-a", a), ("bm-b", b)])
    check("audit:union-zero-loss", len(m["history"]) == 3)
    check("audit:latest-deep-probe", m["latest"]["ts"] == "01:20:00"
          and m["latest"]["py_cpu_pct"] == 0.3)

    # 3. regime_state: row union + flat take-new
    a = {"updated": "01:00:00", "state": "ORANGE",
         "triggers": ["t1"], "transitions": [], "history": [{"asof": "d1"}]}
    b = {"updated": "02:00:00", "state": "RED",
         "triggers": ["t1", "t2"], "transitions": [], "history": []}
    m, _ = merge_regime_state([("bm-a", a), ("bm-b", b)])
    check("regime:union+take-new", m["state"] == "RED"
          and m["triggers"] == ["t1", "t2"] and m["history"] == [{"asof": "d1"}])

    # 4. autofill: dup dedupe + cap50 keeps newest + asc write + last_tick max
    rows_a = [{"ts": f"2026-09-27 {i:02d}:00:02"} for i in range(30)]
    rows_b = [{"ts": f"2026-09-28 {i:02d}:00:02"} for i in range(30)]
    a = {"last_tick": {"ts": "2026-09-28 01:00:02"},
         "launches": rows_a + rows_b[:5]}
    b = {"last_tick": {"ts": "2026-09-28 02:00:02"}, "launches": rows_b}
    m, _ = merge_autofill_state([("bm-a", a), ("bm-b", b)])
    check("autofill:cap50-newest", len(m["launches"]) == 50
          and m["launches"][0]["ts"] == "2026-09-27 10:00:02"
          and m["launches"] == sorted(m["launches"],
                                      key=lambda x: x["ts"]))
    check("autofill:last_tick-max", m["last_tick"]["ts"] == "2026-09-28 02:00:02")

    # 5. runnable_pool: done-absorption + governance non-null-first (r370)
    a = {"updated_at": "01:00:00", "entries": [
        {"id": "P1", "status": "ready", "lane_owner": None,
         "lane_note": None},
        {"id": "P2", "status": "done", "shards": [{"s": 1}],
         "result_ref": "r.json"}]}
    b = {"updated_at": "02:00:00", "entries": [
        {"id": "P1", "status": "ready", "lane_owner": "bm-b",
         "lane_note": "pinned"},
        {"id": "P2", "status": "ready", "shards": []},
        {"id": "P3", "status": "waiting"}]}
    m, _ = merge_runnable_pool([("bm-a", a), ("bm-b", b)])
    p1 = next(e for e in m["entries"] if e["id"] == "P1")
    p2 = next(e for e in m["entries"] if e["id"] == "P2")
    p3 = next(e for e in m["entries"] if e["id"] == "P3")
    check("pool:gov-nonnull-first", p1["lane_owner"] == "bm-b"
          and p1["lane_note"] == "pinned")
    check("pool:done-absorb", p2["status"] == "done"
          and p2["shards"] == [{"s": 1}])
    check("pool:single-side-keep", p3["status"] == "waiting")
    check("pool:meta-newer", m["updated_at"] == "02:00:00")

    # 5b. runnable_pool shards key-union (r373 drift fix): stale lane
    # lag on owner_since must absorb into the newer shared row (zero
    # drift), a swallowed shared row must recover from the lane, and
    # keyless rows keep the whole-row append-log union.
    fresh = {"updated_at": "03:00:00", "entries": [
        {"id": "S", "status": "ready", "shards": [
            {"key": "v2-0of1", "status": "ready", "owner": "bm-b",
             "owner_since": "2026-09-28 02:33:18", "checkpoint": None},
            {"note": "keyless-extra"}]}]}
    stale_lane = {"updated_at": "02:00:00", "entries": [
        {"id": "S", "status": "ready", "shards": [
            {"key": "v2-0of1", "status": "ready", "owner": "bm-b",
             "owner_since": "2026-09-28 02:13:19",
             "checkpoint": "results/cp.json"}]}]}
    m, _ = merge_runnable_pool([("legacy", fresh), ("bm-a", stale_lane)])
    s = next(e for e in m["entries"] if e["id"] == "S")
    check("pool:shard-lag-absorbs", s["shards"][0]["owner_since"]
          == "2026-09-28 02:33:18"
          and s["shards"][0]["checkpoint"] == "results/cp.json"
          and len([r for r in s["shards"] if r.get("key") == "v2-0of1"]) == 1)
    check("pool:shard-keyless-union", {"note": "keyless-extra"}
          in s["shards"])
    # swallow direction: shared reverted to the old fork, lane holds the
    # newer keepalive -> merged must recover the newer truth.
    m, _ = merge_runnable_pool([("legacy", stale_lane), ("bm-a", fresh)])
    s = next(e for e in m["entries"] if e["id"] == "S")
    check("pool:shard-swallow-recover", s["shards"][0]["owner_since"]
          == "2026-09-28 02:33:18")

    # 6. gate_attrition full-volume union (47 consumers need every row)
    a = {"schema": "v1", "entries": [{"batch": "B", "ts": "01"}],
         "history": []}
    b = {"schema": "v1", "entries": [{"batch": "B", "ts": "01"},
                                      {"batch": "C", "ts": "02"}],
         "history": [{"batch": "X", "ts": "03"}]}
    m, _ = merge_gate_attrition([("bm-a", a), ("bm-b", b)])
    check("gate:full-volume", len(m["entries"]) == 2
          and len(m["history"]) == 1)

    # 7. post_review: id union + newer _reconciled wins collisions
    a = {"_law": "frozen", "_reconciled": "2026-09-24 21:43:10 r71",
         "items": [{"id": "P-1", "status": "OLD"}]}
    b = {"_law": "frozen", "_reconciled": "2026-09-26 10:00:00 r90",
         "items": [{"id": "P-1", "status": "NEW"},
                   {"id": "P-2", "status": "YES"}]}
    m, _ = merge_post_review_criteria([("bm-a", a), ("bm-b", b)])
    p1 = next(i for i in m["items"] if i["id"] == "P-1")
    check("postreview:id-union+newer-wins", len(m["items"]) == 2
          and p1["status"] == "NEW")

    # 7b. lane source strips lane_machine on load -> merged == shared
    # (reconcile must stay zero-drift the moment real lanes exist;
    # writer dual-track D-20260928-03(1) batch-1).
    a = {"latest": {"ts": "01:00:00", "py_cpu_pct": 1.0},
         "history": [{"ts": "01:00:00"}]}
    lane = dict(a, lane_machine="bm-a")
    m, _ = merge_compute_audit([("legacy", a), ("bm-a", lane)])
    check("audit:lane-strip-zero-drift", m == a)
    mr, _ = merge_regime_state([("legacy", shared["regime_state"]),
                                ("bm-a", dict(shared["regime_state"],
                                              lane_machine="bm-a"))])
    check("regime:lane-strip-zero-drift", mr == shared["regime_state"])

    # 8. lane_machine self-signature fail-closed
    try:
        tmp = (_lane_path("compute_audit", "bm-a"), )
        saved = None
        os.makedirs(PATHS.results_dir, exist_ok=True)
        if os.path.exists(tmp[0]):
            saved = open(tmp[0], encoding="utf-8").read()
        with open(tmp[0], "w", encoding="utf-8") as fh:
            json.dump({"lane_machine": "bm-c", "history": []}, fh)
        try:
            load_sources("compute_audit")
            ok = False
        except SystemExit:
            ok = True
        finally:
            if saved is None:
                os.remove(tmp[0])
            else:
                with open(tmp[0], "w", encoding="utf-8") as fh:
                    fh.write(saved)
        check("lane_machine-fail-closed", ok)
    except OSError:
        check("lane_machine-fail-closed", False)

    # 9. B-family bootstrap identity: single legacy source -> unchanged
    # (all eight census B faces; reconcile zero-drift baseline law).
    b_shared = {
        "update_status": {"updated": "2026-09-28 03:02:47",
                          "data_cutoff": "2026-09-24",
                          "total_new_rows": 48},
        "heat_update_status": {"updated": "2026-09-28 03:03:11",
                               "snapshots": 3, "verdict": "no-op"},
        "lhb_update_status": {"updated": "2026-09-28 03:03:10",
                             "cutoff": "2026-09-24", "new_rows": 0},
        "futures_update_status": {"ts": "2026-09-28T03:03:11",
                                  "mode": "no-op",
                                  "data_cutoff": "2026-09-24"},
        "fundamental_status": {"updated": "2026-09-27 22:39:37",
                              "ok": True},
        "token_usage": {"generated": "2026-09-28 03:03:58",
                        "machines": {"bm-a": 1}},
        "crash_fuse": {"sigs": {"scripts/x.py|run": {
            "count": 1, "refusals": 1,
            "last_crash_ts": "2026-09-27 03:30:03",
            "last_refusal_ts": "2026-09-27 03:30:03"}}},
        "market_clock/call_latest": {"asof": "2026-09-24",
                                     "clock_cell": "C7"},
    }
    for face in B_FACES:
        merged, _ = merge_face(face, [("legacy", b_shared[face])])
        check(f"b-bootstrap-identity:{face}", merged == b_shared[face])

    # 10. B max-cutoff (census recipe): freshest probe wins wholesale
    a = {"updated": "2026-09-28 03:00:00", "data_cutoff": "2026-09-23"}
    b = {"updated": "2026-09-28 03:10:00", "data_cutoff": "2026-09-24"}
    m, _ = merge_face("update_status", [("legacy", a), ("bm-a", b)])
    check("b-take-new-freshness", m == b)

    # 11. heat host-lane priority (R31 authority law): a fresher clobbered
    # legacy (non-host no-op, snapshots=0) must LOSE to the host lane.
    clobber = {"updated": "2026-09-28 03:30:00", "snapshots": 0,
               "verdict": "no-op: non-host local dir absent"}
    host_lane = {"updated": "2026-09-28 03:03:11", "snapshots": 3,
                 "verdict": "no-op: before 15:30:00"}
    m, _ = merge_face("heat_update_status",
                      [("legacy", clobber), ("bm-a", host_lane)])
    check("b-heat-host-priority", m == host_lane)
    # fallback: no host lane in sources -> plain max-cutoff (pre-wiring
    # rounds keep today's last-writer semantics, disclosed honestly)
    other = {"updated": "2026-09-28 02:00:00", "snapshots": 3}
    m, _ = merge_face("heat_update_status",
                      [("legacy", clobber), ("bm-b", other)])
    check("b-heat-fallback-take-new", m == clobber)

    # 12. crash_fuse: sig key union + same-key newer-event-wins
    fa = {"sigs": {"r|run": {"count": 1, "refusals": 1,
                             "last_crash_ts": "2026-09-27 03:30:03",
                             "last_refusal_ts": "2026-09-27 03:30:03"}}}
    fb = {"sigs": {"r|run": {"count": 2, "refusals": 0,
                             "last_crash_ts": "2026-09-28 03:00:08"},
                   "r2|run": {"count": 1, "refusals": 0,
                              "last_crash_ts": "2026-09-26 01:00:00"}}}
    m, _ = merge_face("crash_fuse", [("legacy", fa), ("bm-b", fb)])
    check("b-crashfuse-union+newer-event",
          set(m["sigs"]) == {"r|run", "r2|run"}
          and m["sigs"]["r|run"]["count"] == 2
          and m["sigs"]["r|run"]["last_crash_ts"] == "2026-09-28 03:00:08"
          and m["sigs"]["r2|run"]["count"] == 1)

    # 13. call_latest: asof-probe take-new (deterministic same-day regen
    # -> byte-identical sides; a fresher panel cutoff wins the view)
    ca = {"asof": "2026-09-23", "clock_cell": "C7"}
    cb = {"asof": "2026-09-24", "clock_cell": "C7"}
    m, _ = merge_face("market_clock/call_latest",
                      [("legacy", ca), ("bm-b", cb)])
    check("b-calllatest-asof-take-new", m == cb)

    print(f"selftest: {len(fails)} FAIL" + ("s" if fails else "")
          + (f" -> {fails}" if fails else " (all PASS)"))
    return 1 if fails else 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ("merge", "reconcile", "selftest"):
        print(__doc__)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    faces = ALL_FACES
    if "--face" in argv:
        i = argv.index("--face")
        faces = tuple(argv[i + 1:i + 2]) or ALL_FACES
        for f in faces:
            if f not in ALL_FACES:
                print(f"unknown face {f!r}; ALL_FACES={ALL_FACES}")
                return 2
    if argv[1] == "merge":
        return _cmd_merge(faces)
    return _cmd_reconcile(faces)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
