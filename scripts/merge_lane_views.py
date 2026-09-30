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
inputs -- no new shared writable face is created (merge/reconcile/resolve
print, never write repo files).  ONE exception landed with debt-③ slice-5
(r385): sync_face() is the switch-time library write path for the pool face
-- it settles shared AND the calling machine's lane to the merged view
(churn-free by parsed compare); the S6 audit leg imports it.

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
  python scripts/merge_lane_views.py resolve <path> [--stage1 F --stage2 F
      --stage3 F --out F --dry-run]  # push-storm UU resolve, same recipes
  python scripts/merge_lane_views.py selftest             # offline fixtures

Exit codes: 0 ok / 1 reconcile drift (or selftest fail) / 2 mechanism fault.
Zero network, zero engine, L1 deterministic; fail-closed on shape surprises.
"""
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS  # noqa: E402
from config.lane_io import machine_id as _own_machine_id  # noqa: E402

A_FACES = ("compute_audit", "regime_state", "autofill_state",
           "runnable_pool", "gate_attrition", "post_review_criteria")
MACHINES = ("bm-a", "bm-b", "bm-c")
# r370 pit-law: resolver/union may swallow the OTHER machine's in-tree fixes
# for governance fields -- non-empty-first with annotation, never blind-pick.
GOVERNANCE_FIELDS = ("lane_owner", "lane_note", "claimed_by", "claimed_at",
                     "claim_note", "yield_note", "defer_note")
_RECON_TS = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


def _row_id(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def _lane_path(face, machine, results_dir=None):
    base = results_dir if results_dir is not None else PATHS.results_dir
    return os.path.join(base, f"{face}.{machine}.json")


def _merge_shard_same_key(a, b):
    """Same-key shard rows: the row with the newer ``owner_since`` is
    the base (r311 latest.ts deep-probe law); fields missing on the
    base fill from the other side (r370 non-null-first family; ts ties
    resolve deterministically to the first side).

    r479 bm-b pit fix: owner_since keys PRESENT with a null value
    str()-compared as "None", which sorts AFTER every real timestamp
    string ("N" > "2") -- a null-timestamp lane row became the base and
    swallowed a done harvest flip (S1 live evidence: done reverted to
    ready by settle). None/"" normalize to "" so real timestamps win,
    restoring the r311 latest.ts law for null-valued keys."""
    ta, tb = (str(a.get("owner_since") or ""),
              str(b.get("owner_since") or ""))
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


def _shared_path(face, results_dir=None):
    base = results_dir if results_dir is not None else PATHS.results_dir
    return os.path.join(base, f"{face}.json")


def load_sources(face, results_dir=None):
    """Fixed-order sources: legacy shared blob first, then lane files.

    Each lane file may self-sign with a top-level ``lane_machine`` field;
    a signature contradicting the filename is fail-closed (r98 identity
    lesson: never guess machine identity from stale content).
    ``results_dir`` overrides the scan base ONLY for hermetic selftests
    that swap the results dir (D-20260928-03 batch-1 slice-2); production
    callers leave it None = PATHS truth."""
    sources = []
    shared = _shared_path(face, results_dir)
    if os.path.exists(shared):
        with open(shared, encoding="utf-8") as fh:
            sources.append(("legacy", json.load(fh)))
    for machine in MACHINES:
        p = _lane_path(face, machine, results_dir)
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


def _ts_parse(v):
    """Best-effort timestamp parse for cross-format comparison.

    Fleet writers emit two in-the-wild formats (MSG-0705): canonical
    autofill _now() 'YYYY-MM-DD HH:MM:SS' (naive local) and manual
    submit scripts' ISO-8601 with tz. Same-day mixed formats mis-rank
    lexicographically ('T' 0x54 > ' ' 0x20 -> space side always loses).
    Parse via fromisoformat, drop tzinfo (fleet clocks are uniform
    Asia/Shanghai; the tz only restates the same local offset), return
    None for unparseable values so the caller falls back to legacy.
    """
    try:
        dt = datetime.datetime.fromisoformat(str(v).strip())
    except (ValueError, TypeError):
        return None
    return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt


def _flat_winner(sources, probe):
    """Index of the source whose probe ts is newest; ties -> first-seen.

    Parse-first comparison (MSG-0705 cross-format law): incumbent and
    candidate both parse as timestamps -> datetime compare (equal
    instants in different formats stay first-seen, zero churn); any
    unparseable side falls back to the legacy lexicographic compare.
    """
    best, best_ts, best_dt, have = 0, "", None, False
    for i, (_label, data) in enumerate(sources):
        ts = probe(data)
        dt = _ts_parse(ts)
        if not have:
            take = True
        elif dt is not None and best_dt is not None:
            take = dt > best_dt
        else:
            take = ts > best_ts
        if take:
            best, best_ts, best_dt, have = i, ts, dt, True
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
    # launches: composite-key dedup FIRST (r322 law -- live catch r375: the
    # V2-P1 crash launch row carried crash_counted=true on the enriched
    # faces and not on the stale lane copies; whole-row identity union
    # silently double-stored the same key -> union 51 -> cap50 evicted a
    # row the shared file still held = reconcile DRIFT).  Same-key rows
    # merge by ADDITIVE field-union (field-set difference only -> union
    # fields, keep one row); a true value conflict on a common field is a
    # flag-upgrade face -- fail-closed here (R209 zero-silent-degradation),
    # never silently double-stored.
    key_fields = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    by_key, order = {}, []
    for _label, data in sources:
        for row in data.get("launches", []):
            k = tuple(str(row.get(f, "")) for f in key_fields)
            if k not in by_key:
                by_key[k] = dict(row)
                order.append(k)
                continue
            base = by_key[k]
            for f, v in row.items():
                if f not in base:
                    base[f] = v          # additive field-union
                elif base[f] != v:
                    raise SystemExit(
                        f"merge_lane_views: autofill launches key {k} true "
                        f"divergence on field {f!r} ({base[f]!r} vs {v!r}) "
                        f"-- flag upgrade, fail-closed (r322 law)")
    rows = [by_key[k] for k in order]
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
    notes.append(f"launches composite-key dedup+field-union -> {len(rows)} "
                 f"kept ({dropped} beyond cap50 dropped as newest-50 "
                 f"semantics); last_tick ts={best_ts!r}")
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
    # differing non-done statuses. r378 observation-window catch #4: a
    # deliberate session defer (status waiting + non-empty defer_note)
    # was resurrected to ready by a stale pre-defer lane mirror -- no
    # per-entry ts exists, so the note IS the deliberate-act marker.
    # Marker law (risk-asymmetric): marked-waiting beats bare-ready (a
    # swallowed defer = autofill relaunches a deliberately-held batch =
    # double burn); the un-defer convention clears defer_note on
    # flip-back, and a swallowed un-defer only delays a fill by <= one
    # round (mirror heals the lane) = low harm. Both sides marked (or
    # neither) -> legacy rank. This branch also merges governance and
    # shards across sides regardless of the winning side (the old
    # take-one-side-wholesale dropped the losing side's annotations).
    a_note, b_note = bool(a.get("defer_note")), bool(b.get("defer_note"))
    a_mw = a.get("status") == "waiting" and a_note
    b_mw = b.get("status") == "waiting" and b_note
    bare_ready = ((a.get("status") == "ready" and not a_note)
                  or (b.get("status") == "ready" and not b_note))
    if (a_mw or b_mw) and bare_ready:
        win, lose = (a, b) if a_mw else (b, a)
        notes.append(f"entry {a.get('id')}: deliberate defer marker "
                     f"(waiting+defer_note, r378 catch #4 law) beats "
                     f"bare ready from a stale mirror")
    else:
        rank = {"ready": 2, "waiting": 1}
        win = a if rank.get(a.get("status"), 0) >= \
            rank.get(b.get("status"), 0) else b
        lose = b if win is a else a
        notes.append(f"entry {a.get('id')}: status {a.get('status')!r} vs "
                     f"{b.get('status')!r} -> kept {win.get('status')!r}")
    out = dict(win)
    for f in GOVERNANCE_FIELDS:
        if not out.get(f) and lose.get(f):
            out[f] = lose[f]
            notes.append(f"entry {a.get('id')}: governance {f} "
                         f"non-null-first across status conflict "
                         f"(r378 gap fix)")
    sa, sb = win.get("shards"), lose.get("shards")
    if isinstance(sa, list) or isinstance(sb, list):
        rows = _union_shard_rows(sa or [], sb or [])
        out["shards"] = rows
        notes.append(f"entry {a.get('id')}: shards key-union "
                     f"-> {len(rows)}")
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
#     is an append/monotone-counter face, never a last-writer blob);
#     D-03(2) cleared-tombstones ("cleared" dict, cleared_ts key-union
#     newer-wins) suppress lane-resurrected older events (r389 family).
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

    def _tomb_ts(tomb):
        if not isinstance(tomb, dict):
            return ""
        return str(tomb.get("cleared_ts", ""))

    win = _flat_winner(sources, _max_sig_ts)
    out = dict(sources[win][1])
    sigs = {}
    cleared = {}
    for label, data in sources:
        for key, tomb in (data.get("cleared") or {}).items():
            if not isinstance(tomb, dict):
                continue
            if (key not in cleared
                    or _tomb_ts(tomb) > _tomb_ts(cleared[key])):
                cleared[key] = tomb
        for key, sig in data.get("sigs", {}).items():
            if key not in sigs:
                sigs[key] = sig
                continue
            if _sig_ts(sig) > _sig_ts(sigs[key]):
                sigs[key] = sig
                notes.append(f"sig {key!r}: newer event from {label}")
    # D-03(2) cleared-tombstone (r389 drift family): a deliberate clear
    # (code-change fix) recorded by ANY machine suppresses the same sig
    # resurrected from another machine's stale lane; a NEWER event
    # (re-crash on the new code) beats the tombstone and survives.
    for key in list(sigs):
        tomb = cleared.get(key)
        if tomb and _tomb_ts(tomb) > _sig_ts(sigs[key]):
            del sigs[key]
            notes.append(f"sig {key!r}: cleared-tombstone "
                         f"{_tomb_ts(tomb)} > last event -> suppressed")
    out["sigs"] = sigs
    if cleared:
        out["cleared"] = cleared
    notes.append(f"sigs key-union -> {len(sigs)} runner sig(s), same-key "
                 f"newer-event-wins (+{len(cleared)} tombstone(s)), flat "
                 f"from {sources[win][0]}")
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

# D-20260928-03(1) batch-1 writer retirement (r381): faces whose shared
# write is RETIRED -- the owning machine's writer is lane-primary and the
# shared file is the FROZEN legacy base (still merger source #0, so
# scattered/forensic rewrites of it stay absorbed).  Reconcile cannot
# demand merged == shared any more (the live lane legitimately advances
# past the frozen base every tick); for these faces the equality
# instrument is retired WITH the shared write and reconcile emits an
# honest RETIRED-SHARED status line instead (liveness is carried by the
# writer's strict lane save + the C8 watchdog, not by this instrument).
# Probe keys (deep ts path) exist purely for the status line.
RETIRED_SHARED_PROBES = {
    "autofill_state": ("last_tick", "ts"),
}


def _retired_status(face, sources):
    """RETIRED-SHARED status line for a lane-primary face (r381)."""
    if face not in RETIRED_SHARED_PROBES:
        raise SystemExit(f"merge_lane_views: {face!r} is not a "
                         "retired-shared face -- fail-closed")
    merged, _notes = merge_face(face, sources)
    shared = next(d for lbl, d in sources if lbl == "legacy")
    probe = "/".join(RETIRED_SHARED_PROBES[face])
    base_ts = _deep_ts(shared, *RETIRED_SHARED_PROBES[face])
    merged_ts = _deep_ts(merged, *RETIRED_SHARED_PROBES[face])
    return (f"[{face}] RETIRED-SHARED (lane-primary r381): frozen base "
            f"{probe}={base_ts!r}; merged view {probe}={merged_ts!r}; "
            f"sources={[s[0] for s in sources]} -- equality instrument "
            f"retired with the shared write (strict lane write + C8 "
            f"watchdog carry liveness)")


def merge_face(face, sources):
    if face not in MERGERS:
        raise SystemExit(f"merge_lane_views: unknown face {face!r} "
                         f"(ALL_FACES={ALL_FACES}) -- fail-closed")
    if not sources:
        raise SystemExit(f"merge_lane_views: face {face!r} has no sources")
    return MERGERS[face](sources)


def face_view(face, results_dir=None):
    """Consumer-side one-shot lane-merged view (D-20260928-03 batch-1
    slice-2): legacy shared blob + per-machine lane files merged under the
    same conflict-resolver recipes the resolve subcommand uses. No sources
    at all = {} (honest not-yet semantics for read-points that previously
    treated a missing shared file as empty); identity contradictions and
    shape surprises fail closed (r98 / R209 zero-silent-degradation)."""
    sources = load_sources(face, results_dir)
    if not sources:
        return {}
    merged, _notes = merge_face(face, sources)
    return merged


def sync_face(face, results_dir=None, machine=None):
    """Debt-③ (r381 audit) slice-5: merger-recipe TWO-WAY settle for the
    pool face (runnable_pool) -- the ONE shared-coordination face with
    BOTH a tick dual-track writer (claim/keepalive/done write shared +
    own lane together, D-20260928-03 batch-1) and free-form session
    writers (defer/flip one-off scripts touch ONLY the shared file,
    r378 catch #4).  The old S6 leg was a one-way byte mirror
    (mirror_shared_if_changed, shared -> lane): it healed session-side
    shared edits into the lane with a one-tick lag, but the byte-restore
    shape is the r381 audit-③ hazard in waiting -- the day the tick goes
    lane-primary a stale shared blob rolls the lane back and swallows a
    lane-only keepalive (r288 double-burn family).  This sync derives
    the SAME merged view consumers read (marker law, done-absorption,
    id-union) and settles BOTH sides to it, parsed-compare churn-free:

      shared < merged (semantic compare)  -> atomic shared write
      own lane < merged (sans signature) -> atomic lane write

    Session edit on shared, tick edit on the lane, or both inside one
    window all converge losslessly to the union.

    Guards: RETIRED faces fail closed (merged != frozen shared on every
    call would resurrect the write treadmill the r381 retirement
    killed); corrupt/unreadable sources (mid push-storm) and identity
    contradictions (r98) = honest "unreadable"/fail-closed return,
    NEITHER side is written from a half-loaded union (recovery paths
    stay git history + the resolve subcommand).  Returns a status dict
    {status, wrote_shared, wrote_lane, notes}; never raises into the
    calling S6 leg (exit contracts frozen)."""
    if face in RETIRED_SHARED_PROBES:
        return {"status": "refused", "wrote_shared": False,
                "wrote_lane": False,
                "notes": [f"retired face {face!r}: shared write retired, "
                          "sync refused (fail-closed)"]}
    try:
        sources = load_sources(face, results_dir)
    except (Exception, SystemExit) as ex:
        return {"status": "unreadable", "wrote_shared": False,
                "wrote_lane": False,
                "notes": [f"source load fault: {ex} -- neither side "
                          "written (resolve is the recovery path)"]}
    if not sources:
        return {"status": "no_sources", "wrote_shared": False,
                "wrote_lane": False, "notes": []}
    try:
        merged, notes = merge_face(face, sources)
    except (Exception, SystemExit) as ex:
        return {"status": "unreadable", "wrote_shared": False,
                "wrote_lane": False,
                "notes": [f"merge fault: {ex} -- neither side written"]}
    res = {"status": "unchanged", "wrote_shared": False,
           "wrote_lane": False, "notes": list(notes)}
    shared = _shared_path(face, results_dir)
    try:
        with open(shared, encoding="utf-8") as fh:
            cur_shared = json.load(fh)
    except FileNotFoundError:
        cur_shared = None
    except Exception as ex:
        res["status"] = "unreadable"
        res["notes"].append(f"shared face unreadable: {ex} -- neither "
                            "side written")
        return res
    if cur_shared != merged:
        tmp = shared + ".sync.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(merged, fh, ensure_ascii=False, indent=2,
                          default=str)
            os.replace(tmp, shared)
            res["wrote_shared"] = True
            res["status"] = "settled"
        except Exception as ex:
            res["notes"].append(f"shared settle fault: {ex}")
            try:
                os.remove(tmp)
            except OSError:
                pass
    mid = machine if machine is not None else _own_machine_id()
    if not mid:
        res["notes"].append("machine_id unreadable (r98) -- lane side "
                            "skipped, shared side unaffected")
        return res
    lane = _lane_path(face, mid, results_dir)
    try:
        with open(lane, encoding="utf-8") as fh:
            cur_lane = json.load(fh)
        if isinstance(cur_lane, dict):
            cur_lane.pop("lane_machine", None)
    except FileNotFoundError:
        cur_lane = None
    except Exception:
        cur_lane = None  # corrupt lane -> rewrite from merged (lane is
        #                  non-authoritative, union is a superset)
    if cur_lane != merged:
        payload = dict(merged)
        payload["lane_machine"] = mid
        tmp = lane + ".sync.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2,
                          default=str)
            os.replace(tmp, lane)
            res["wrote_lane"] = True
            res["status"] = "settled"
        except Exception as ex:
            res["notes"].append(f"lane settle fault: {ex}")
            try:
                os.remove(tmp)
            except OSError:
                pass
    return res


# ---------------------------------------------------------------------------
# resolve subcommand (r377, r376 pit-law engineering debt): push-storm
# resolvers get ONE canonical entry point instead of hand-rolled unions.
# The r376 live catch proved a hand-rolled whole-row tie->HEAD take drops
# enriched field faces (crash_counted) the other machine's lane carries --
# canon: resolve scripts IMPORT the merger recipes.  This subcommand reads
# the rebase conflict stages straight from the git index (or --stageN
# files for forensic replay) and applies the SAME merge_face recipe the
# consumer merger uses.  Lane files and non-ALL_FACES paths fail closed:
# per-machine lanes resolve per R31 machine authority (take the owner's
# side, never a union) and snapshot/twin classes keep the
# bigmoney-conflict-resolve skill recipes (deep-ts probe take-new).
# ---------------------------------------------------------------------------

def detect_face(path):
    """Repo path -> face name; fail-closed on lane files / unknown faces."""
    rel = path.replace("\\", "/")
    if not rel.startswith("results/"):
        raise SystemExit(f"merge_lane_views resolve: {path!r} is not a "
                         f"results/ face -- fail-closed (union recipes "
                         f"live only for ALL_FACES)")
    stem = rel[len("results/"):]
    if stem.endswith(".json"):
        stem = stem[:-len(".json")]
    for m in MACHINES:
        if stem.endswith("." + m):
            raise SystemExit(
                f"merge_lane_views resolve: {path!r} is a per-machine "
                f"lane file -- lanes resolve per R31 machine authority "
                f"(take the owner machine's side), never a union; "
                f"fail-closed")
    if stem not in ALL_FACES:
        raise SystemExit(
            f"merge_lane_views resolve: unknown face {stem!r} -- union "
            f"recipes exist only for ALL_FACES={ALL_FACES}; snapshot/twin "
            f"classes follow the bigmoney-conflict-resolve skill (deep-ts "
            f"probe take-new); fail-closed (r376 pit-law)")
    return stem


def resolve_face_from_blobs(face, blobs):
    """Resolve one conflicted face from rebase stage blobs.

    Orientation per r351 stage-mapping law: during ``git pull --rebase``
    stage :2: is the NEW base = the ORIGIN side and :3: is the replayed
    commit = the LOCAL side.  Sources order = [:2:, :3:, :1:] -- a
    same-second take-new tie resolves to :2: = origin (r140 canon) and
    the merge-base can only win a take-new race by being strictly
    fresher than both descendants (normally never)."""
    if face not in ALL_FACES:
        raise SystemExit(f"merge_lane_views resolve: unknown face {face!r} "
                         f"-- fail-closed (ALL_FACES={ALL_FACES})")
    sources = []
    if blobs.get("base_side") is not None:
        sources.append((":2: base-side", blobs["base_side"]))
    if blobs.get("replay_side") is not None:
        sources.append((":3: replay-side", blobs["replay_side"]))
    if blobs.get("base") is not None:
        sources.append((":1: merge-base", blobs["base"]))
    if not sources:
        raise SystemExit("merge_lane_views resolve: no stage blobs "
                         "supplied -- fail-closed")
    return merge_face(face, sources)


def _read_stage(stage, rel):
    r = subprocess.run(["git", "show", f":{stage}:{rel}"],
                       capture_output=True)
    if r.returncode != 0:
        return None, None
    raw = r.stdout
    return json.loads(raw.decode("utf-8")), (b"\r\n" in raw)


def _cmd_resolve(argv):
    path = None
    opts = {"--stage1": None, "--stage2": None, "--stage3": None,
            "--out": None, "--dry-run": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--stage1", "--stage2", "--stage3", "--out"):
            if i + 1 >= len(argv):
                print(f"resolve: {a} needs a value")
                return 2
            opts[a] = argv[i + 1]
            i += 2
        elif a == "--dry-run":
            opts[a] = True
            i += 1
        elif path is None:
            path = a
            i += 1
        else:
            print(f"resolve: unexpected arg {a!r}")
            return 2
    if not path:
        print("resolve: usage: merge_lane_views.py resolve "
              "<results/path.json> [--stage1 F --stage2 F --stage3 F "
              "--out F --dry-run]")
        return 2
    face = detect_face(path)
    rel = path.replace("\\", "/")
    crlf = None
    blobs = {}

    def _load_file(p):
        nonlocal crlf
        raw = open(p, "rb").read()
        if crlf is None and b"\r\n" in raw:
            crlf = True
        return json.loads(raw.decode("utf-8"))

    if opts["--stage1"] or opts["--stage2"] or opts["--stage3"]:
        # forensic / replay mode: explicit stage files, no git index read
        if opts["--stage1"]:
            blobs["base"] = _load_file(opts["--stage1"])
        if opts["--stage2"]:
            blobs["base_side"] = _load_file(opts["--stage2"])
        if opts["--stage3"]:
            blobs["replay_side"] = _load_file(opts["--stage3"])
    else:
        for stage, key in ((2, "base_side"), (3, "replay_side"),
                           (1, "base")):
            data, c = _read_stage(stage, rel)
            if data is not None:
                blobs[key] = data
                if crlf is None:
                    crlf = c
    if "base_side" not in blobs and "replay_side" not in blobs:
        print(f"resolve: no conflict stages for {rel!r} -- is a "
              f"rebase/merge active for this path? (or pass explicit "
              f"--stage2/--stage3 files)")
        return 2
    merged, notes = resolve_face_from_blobs(face, blobs)
    print(f"[resolve:{face}] stage blobs present={sorted(blobs)}")
    for n in notes:
        print(f"  - {n}")
    payload = json.dumps(merged, ensure_ascii=False, indent=1)
    if crlf:
        payload = payload.replace("\n", "\r\n")
    out_path = opts["--out"] or path
    if opts["--dry-run"]:
        print(f"[resolve:{face}] DRY-RUN: would write {out_path} "
              f"({len(payload)}B)")
    else:
        with open(out_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(payload + ("\r\n" if crlf else "\n"))
        back = json.load(open(out_path, encoding="utf-8"))
        assert back == merged, "parse-verify failed (r185 law)"
        print(f"[resolve:{face}] wrote {out_path} (parse-verified)")
        print("next: git add <path> -> $env:GIT_EDITOR='true' + "
              "git rebase --continue (PS env law r356) -> python "
              "scripts/merge_lane_views.py reconcile --face "
              f"<{face}> (same-window law r376)")
    return 0


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
        if face in RETIRED_SHARED_PROBES:
            print(_retired_status(face, sources))
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

    # 1b. _flat_winner cross-format same-day ordering (MSG-0705: canonical
    # space format vs manual-script ISO-8601 must rank by instant, not by
    # lexicographic 'T' > ' '; equal instants keep first-seen zero churn)
    src_space_new = [{"updated_at": "2026-09-29 06:55:07"},
                     {"updated_at": "2026-09-29T06:00:54+08:00"}]
    src_iso_new = [{"updated_at": "2026-09-29T06:55:07+08:00"},
                   {"updated_at": "2026-09-29 06:00:54"}]
    src_eq_fmt = [{"updated_at": "2026-09-29 06:55:07"},
                  {"updated_at": "2026-09-29T06:55:07+08:00"}]
    src_rev = [src_space_new[1], src_space_new[0]]
    check("winner:space-newer-beats-same-day-iso",
          _flat_winner([("a", src_space_new[0]), ("b", src_space_new[1])],
                       lambda d: d["updated_at"]) == 0)
    check("winner:iso-newer-beats-same-day-space",
          _flat_winner([("a", src_iso_new[0]), ("b", src_iso_new[1])],
                       lambda d: d["updated_at"]) == 0)
    check("winner:equal-instant-first-seen",
          _flat_winner([("a", src_eq_fmt[0]), ("b", src_eq_fmt[1])],
                       lambda d: d["updated_at"]) == 0)
    check("winner:reversed-order-space-newer-wins",
          _flat_winner([("a", src_rev[0]), ("b", src_rev[1])],
                       lambda d: d["updated_at"]) == 1)

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

    # 4b. autofill composite-key dedup + additive field-union (r322 law,
    # r375 live catch: V2-P1 crash launch row carried crash_counted=true on
    # the enriched faces, absent on stale lane copies -> whole-row union
    # double-stored the key and cap50 evicted a live shared row).  Same-key
    # faces merge to ONE row carrying the enriched field; a true value
    # conflict on a common field fails closed (flag upgrade, r322).
    rich = {"ts": "2026-09-28 02:30:01", "machine": "bm-b", "pid": 24976,
            "runner_sha256": "8802", "entry": "V2", "shard": "v2-0of1",
            "verdict": "launched", "crash_counted": True}
    stale = {k: v for k, v in rich.items() if k != "crash_counted"}
    other = {"ts": "2026-09-28 01:00:02", "machine": "bm-a", "pid": 1,
             "runner_sha256": "x", "entry": "E", "shard": "s"}
    m, _ = merge_autofill_state(
        [("legacy", {"launches": [dict(rich), dict(other)]}),
         ("bm-a", {"launches": [dict(stale)]})])
    check("autofill:composite-dedup+field-union",
          len(m["launches"]) == 2
          and m["launches"][1].get("crash_counted") is True
          and m["launches"][0].get("entry") == "E")
    try:
        bad = dict(stale)
        bad["verdict"] = "conflicting-value"
        merge_autofill_state([("legacy", {"launches": [dict(rich)]}),
                              ("bm-a", {"launches": [bad]})])
        ok = False
    except SystemExit:
        ok = True
    check("autofill:composite-divergence-fail-closed", ok)

    # 4z. r381 writer retirement: a retired-shared face reconciles by
    # honest status line, not equality -- the live lane legitimately
    # advances past the frozen legacy base every tick; non-retired
    # faces on the helper fail closed.
    base = {"last_tick": {"ts": "2026-09-28 04:40:01",
                          "machine": "bm-a"},
            "launches": [{"ts": "2026-09-28 04:40:01"}]}
    lane_fresh = {"last_tick": {"ts": "2026-09-28 05:00:01",
                                "machine": "bm-a"},
                  "launches": base["launches"]}
    line = _retired_status(
        "autofill_state",
        [("legacy", json.loads(json.dumps(base))),
         ("bm-a", json.loads(json.dumps(lane_fresh)))])
    check("retired:status-line-fresh-lane",
          "RETIRED-SHARED" in line and "04:40:01" in line
          and "05:00:01" in line and "legacy" in line
          and "bm-a" in line)
    try:
        _retired_status("regime_state", [("legacy", {})])
        okz = False
    except SystemExit:
        okz = True
    check("retired:non-retired-face-fail-closed", okz)

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

    # 5c. runnable_pool deliberate-defer marker law (r378 catch #4): a
    # session defer (waiting + defer_note) must not be resurrected to
    # ready by a stale pre-defer lane mirror; governance fields survive
    # the status conflict from BOTH sides; both-marked falls to rank.
    deferred = {"updated_at": "03:00:00", "entries": [
        {"id": "V2", "status": "waiting", "defer_note": "r357 defer",
         "lane_owner": "bm-b", "shards": [
            {"key": "v2-0of1", "status": "ready", "owner": "bm-b",
             "owner_since": "2026-09-28 03:43:45"}]}]}
    stale_lane = {"updated_at": "02:00:00", "entries": [
        {"id": "V2", "status": "ready", "yield_note": "prior yield",
         "shards": [
            {"key": "v2-0of1", "status": "ready", "owner": "bm-b",
             "owner_since": "2026-09-28 03:43:08"}]}]}
    m, _ = merge_runnable_pool([("legacy", deferred), ("bm-a", stale_lane)])
    v2 = next(e for e in m["entries"] if e["id"] == "V2")
    check("pool:defer-marker-beats-stale-ready",
          v2["status"] == "waiting" and v2["defer_note"] == "r357 defer")
    check("pool:defer-conflict-gov-union",
          v2.get("yield_note") == "prior yield"
          and v2.get("lane_owner") == "bm-b"
          and v2["shards"][0]["owner_since"] == "2026-09-28 03:43:45")
    both = merge_runnable_pool([
        ("legacy", {"updated_at": "03:00:00", "entries": [
            {"id": "W", "status": "waiting", "defer_note": "old defer"}]}),
        ("bm-a", {"updated_at": "02:00:00", "entries": [
            {"id": "W", "status": "ready", "defer_note": "undefer?"}]})])
    w = next(e for e in both[0]["entries"] if e["id"] == "W")
    check("pool:both-marked-rank-fallback", w["status"] == "ready")

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

    # 12b. D-03(2) cleared-tombstone: r389 drift shape live replay --
    # shared post-clear lacks the sig, a foreign lane still carries it,
    # the clearing machine's lane carries the tombstone -> merged
    # suppresses the resurrection and CONVERGES to shared (zero-drift).
    fs = {"sigs": {"cn_trend|run": {"count": 2, "refusals": 0,
                                    "last_crash_ts": "2026-09-27 06:50:03"},
                   "v2|run": {"count": 1, "refusals": 0,
                              "last_crash_ts": "2026-09-27 02:30:01"}}}
    f_stale_lane = {"sigs": {"trial_w2|run": {"count": 1, "refusals": 1,
                             "last_crash_ts": "2026-09-28 06:20:04",
                             "last_refusal_ts": "2026-09-28 06:20:04"}}}
    f_clear_lane = {"sigs": {"cn_trend|run": {"count": 2, "refusals": 0,
                             "last_crash_ts": "2026-09-27 06:50:03"}},
                    "cleared": {"trial_w2|run": {
                        "cleared_ts": "2026-09-28 07:00:01",
                        "cleared_by": "bm-a", "reason": "code_changed"}}}
    m, _ = merge_face("crash_fuse", [("legacy", fs),
                                     ("bm-c", f_stale_lane),
                                     ("bm-a", f_clear_lane)])
    check("b-crashfuse-tombstone-suppress",
          "trial_w2|run" not in m["sigs"]
          and set(m["sigs"]) == {"cn_trend|run", "v2|run"}
          and m["cleared"]["trial_w2|run"]["cleared_by"] == "bm-a"
          and m == {"sigs": fs["sigs"],
                    "cleared": f_clear_lane["cleared"]})
    # 12c. a NEWER event (re-crash on the new code) beats the tombstone
    f_rec = {"sigs": {"trial_w2|run": {"count": 1, "refusals": 0,
                                      "last_crash_ts": "2026-09-28 09:10:00"}}}
    m, _ = merge_face("crash_fuse", [("legacy", {"sigs": {}}),
                                     ("bm-b", f_rec),
                                     ("bm-a", f_clear_lane)])
    check("b-crashfuse-tombstone-recrash-survives",
          "trial_w2|run" in m["sigs"]
          and m["sigs"]["trial_w2|run"]["last_crash_ts"]
          == "2026-09-28 09:10:00")
    # 12d. tombstone key-union: same key from two sources, newer wins
    f_clear2 = {"cleared": {"trial_w2|run": {
        "cleared_ts": "2026-09-28 08:00:00",
        "cleared_by": "bm-c", "reason": "code_changed"}}}
    m, _ = merge_face("crash_fuse", [("legacy", {"sigs": {}}),
                                     ("bm-a", f_clear_lane),
                                     ("bm-c", f_clear2)])
    check("b-crashfuse-tombstone-union-newer",
          m["cleared"]["trial_w2|run"]["cleared_ts"]
          == "2026-09-28 08:00:00"
          and m["cleared"]["trial_w2|run"]["cleared_by"] == "bm-c")
    # 12e. no tombstones anywhere -> NO "cleared" key attached
    # (additive-key drift vs shared faces is structurally impossible)
    m, _ = merge_face("crash_fuse", [("legacy", fa), ("bm-b", fb)])
    check("b-crashfuse-no-tombstone-no-key", "cleared" not in m)

    # 13. call_latest: asof-probe take-new (deterministic same-day regen
    # -> byte-identical sides; a fresher panel cutoff wins the view)
    ca = {"asof": "2026-09-23", "clock_cell": "C7"}
    cb = {"asof": "2026-09-24", "clock_cell": "C7"}
    m, _ = merge_face("market_clock/call_latest",
                      [("legacy", ca), ("bm-b", cb)])
    check("b-calllatest-asof-take-new", m == cb)

    # 14. resolve subcommand (r377, r376 pit-law debt): canonical
    # push-storm entry point.  Stage orientation per r351: :2: =
    # base-side (origin during rebase), :3: = replay-side (local).
    check("resolve:detect-faces",
          detect_face("results/autofill_state.json") == "autofill_state"
          and detect_face("results\\market_clock\\call_latest.json")
          == "market_clock/call_latest")
    try:
        detect_face("results/autofill_state.bm-a.json")
        ok = False
    except SystemExit:
        ok = True
    check("resolve:detect-lane-fail-closed", ok)
    try:
        detect_face("results/dashboard_status.json")
        ok = False
    except SystemExit:
        ok = True
    check("resolve:detect-unknown-fail-closed", ok)
    # r376 live shape: base-side double-stores the V2-P1 key (stale row
    # missing crash_counted + enriched row); replay-side holds the fixed
    # single row -> resolved = ONE enriched row (launcher authority),
    # last_tick by inner-ts max.
    rich = {"ts": "2026-09-28 02:30:01", "machine": "bm-b", "pid": 24976,
            "runner_sha256": "8802", "entry": "DECISION-CHAIN-V2-P1",
            "shard": "v2-0of1", "verdict": "launched",
            "crash_counted": True}
    stale = {k: v for k, v in rich.items() if k != "crash_counted"}
    side2 = {"last_tick": {"ts": "2026-09-28 03:30:02", "machine": "bm-b"},
             "launches": [dict(stale), dict(rich),
                          {"ts": "2026-09-28 03:10:01", "machine": "bm-a",
                           "pid": 1, "runner_sha256": "x", "entry": "E",
                           "shard": "s"}]}
    side3 = {"last_tick": {"ts": "2026-09-28 03:20:01", "machine": "bm-a"},
             "launches": [dict(rich)]}
    m, _ = resolve_face_from_blobs("autofill_state",
                                   {"base_side": side2,
                                    "replay_side": side3})
    v2 = [r for r in m["launches"]
          if r.get("entry") == "DECISION-CHAIN-V2-P1"]
    check("resolve:autofill-double-store-collapse",
          len(m["launches"]) == 2 and len(v2) == 1
          and v2[0].get("crash_counted") is True
          and m["last_tick"]["ts"] == "2026-09-28 03:30:02")
    # pool governance pin survives a null-field replay side (r370 law)
    p2 = {"updated_at": "03:00:00", "entries": [
        {"id": "P1", "status": "ready", "lane_owner": "bm-b",
         "lane_note": "pinned"}]}
    p3 = {"updated_at": "02:00:00", "entries": [
        {"id": "P1", "status": "ready", "lane_owner": None}]}
    m, _ = resolve_face_from_blobs("runnable_pool",
                                   {"base_side": p2, "replay_side": p3})
    check("resolve:pool-gov-pinned",
          m["entries"][0]["lane_owner"] == "bm-b"
          and m["entries"][0]["lane_note"] == "pinned")
    # take-new same-second tie -> :2: base-side (origin) first-seen win
    ta = {"updated": "2026-09-28 03:30:00", "who": "origin"}
    tb = {"updated": "2026-09-28 03:30:00", "who": "mine"}
    m, _ = resolve_face_from_blobs("update_status",
                                   {"base_side": ta, "replay_side": tb})
    check("resolve:take-new-tie-origin", m["who"] == "origin")
    try:
        resolve_face_from_blobs("autofill_state", {})
        ok = False
    except SystemExit:
        ok = True
    check("resolve:no-stages-fail-closed", ok)

    # face_view (batch-1 slice-2): results_dir override keeps hermetic
    # selftest fixtures working; no sources = honest {}; production-path
    # equivalence with load_sources+merge_face.
    import tempfile
    td = tempfile.mkdtemp(prefix="mvl_view_")
    try:
        check("faceview:no-sources-empty-dict",
              face_view("regime_state", results_dir=td) == {})
        with open(os.path.join(td, "regime_state.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"updated": "2026-09-28 04:00:00", "state": "ORANGE",
                       "history": [{"asof": "2026-09-27", "state": "ORANGE"}]},
                      fh)
        with open(os.path.join(td, "regime_state.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"lane_machine": "bm-a", "updated": "2026-09-28 04:10:00",
                       "state": "RED",
                       "history": [{"asof": "2026-09-28", "state": "RED"}]},
                      fh)
        v = face_view("regime_state", results_dir=td)
        check("faceview:tmp-dir-fixture-override",
              v.get("state") == "RED"  # updated take-new -> lane side
              and "lane_machine" not in v  # signature stripped on load
              and len(v.get("history", [])) == 2)  # whole-row union
        sources = load_sources("regime_state", results_dir=td)
        m2, _n = merge_face("regime_state", sources)
        check("faceview:production-path-equivalence", v == m2)
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)

    # sync_face (debt-③ slice-5, r385): two-way settle for the pool
    # face.  r378 live shape = session defer lands ONLY on shared
    # (bare-ready there, marked-waiting on a lane) -- marker law must
    # settle BOTH sides; corrupt sources must write NEITHER side.
    import tempfile
    td = tempfile.mkdtemp(prefix="mvl_sync_")
    try:
        check("sync:no-sources-noop",
              sync_face("runnable_pool", results_dir=td)["status"]
              == "no_sources")
        check("sync:retired-refused",
              sync_face("autofill_state", results_dir=td)["status"]
              == "refused")
        with open(os.path.join(td, "runnable_pool.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"updated_at": "2026-09-28 03:43:08",
                      "entries": [{"id": "V2P1", "status": "waiting",
                                   "defer_note": "panel source-blocked"}]},
                      fh)
        with open(os.path.join(td, "runnable_pool.bm-b.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"lane_machine": "bm-b",
                      "updated_at": "2026-09-28 03:43:08",
                      "entries": [{"id": "V2P1", "status": "ready"}]},
                      fh)
        r = sync_face("runnable_pool", results_dir=td, machine="bm-b")
        shared_after = json.load(open(os.path.join(
            td, "runnable_pool.json"), encoding="utf-8"))
        lane_after = json.load(open(os.path.join(
            td, "runnable_pool.bm-b.json"), encoding="utf-8"))
        e = lane_after["entries"][0]
        check("sync:session-defer-marker-law-settles-both",
              r["status"] == "settled" and r["wrote_lane"]
              and not r["wrote_shared"]   # shared already == merged
              and e.get("status") == "waiting"       # defer NOT swallowed
              and e.get("defer_note") == "panel source-blocked"
              and lane_after.get("entries") == shared_after["entries"])
        r2 = sync_face("runnable_pool", results_dir=td, machine="bm-b")
        check("sync:churn-free-second-pass-unchanged",
              r2["status"] == "unchanged" and not r2["wrote_shared"]
              and not r2["wrote_lane"])
        # tick-advances-shared shape: lane lags -> lane absorbs the
        # union, shared already == merged (no shared rewrite).
        with open(os.path.join(td, "runnable_pool.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"updated_at": "2026-09-28 03:50:01",
                      "entries": [{"id": "V2P1", "status": "waiting",
                                   "defer_note": "panel source-blocked"},
                                  {"id": "GEN1", "status": "running",
                                   "owner": "bm-a"}]},
                      fh)
        r3 = sync_face("runnable_pool", results_dir=td, machine="bm-b")
        lane_after3 = json.load(open(os.path.join(
            td, "runnable_pool.bm-b.json"), encoding="utf-8"))
        check("sync:shared-only-advance-lane-absorbs",
              r3["wrote_lane"] and not r3["wrote_shared"]
              and lane_after3.get("updated_at") == "2026-09-28 03:50:01"
              and {x["id"] for x in lane_after3["entries"]}
              == {"V2P1", "GEN1"})
        # corrupt shared = neither side written (recovery = resolve).
        with open(os.path.join(td, "runnable_pool.json"), "w",
                  encoding="utf-8") as fh:
            fh.write("{corrupt json")
        lane_bytes = open(os.path.join(td, "runnable_pool.bm-b.json"),
                          "rb").read()
        r4 = sync_face("runnable_pool", results_dir=td, machine="bm-b")
        check("sync:corrupt-shared-neither-side-written",
              r4["status"] == "unreadable" and not r4["wrote_shared"]
              and not r4["wrote_lane"]
              and open(os.path.join(td, "runnable_pool.bm-b.json"),
                      "rb").read() == lane_bytes)
        # identity contradiction (r98) = fail-closed, no writes.
        with open(os.path.join(td, "runnable_pool.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"updated_at": "2026-09-28 04:00:00",
                      "entries": [{"id": "Z", "status": "ready"}]}, fh)
        with open(os.path.join(td, "runnable_pool.bm-a.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"lane_machine": "bm-c",  # contradicts filename
                      "updated_at": "2026-09-28 04:00:00",
                      "entries": [{"id": "Z", "status": "ready"}]}, fh)
        shared_bytes = open(os.path.join(td, "runnable_pool.json"),
                            "rb").read()
        r5 = sync_face("runnable_pool", results_dir=td, machine="bm-a")
        check("sync:identity-contradiction-fail-closed",
              r5["status"] == "unreadable" and not r5["wrote_shared"]
              and not r5["wrote_lane"]
              and open(os.path.join(td, "runnable_pool.json"),
                      "rb").read() == shared_bytes)
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)

    print(f"selftest: {len(fails)} FAIL" + ("s" if fails else "")
          + (f" -> {fails}" if fails else " (all PASS)"))
    return 1 if fails else 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ("merge", "reconcile", "selftest",
                                        "resolve"):
        print(__doc__)
        return 2
    if argv[1] == "selftest":
        return _selftest()
    if argv[1] == "resolve":
        return _cmd_resolve(argv[2:])
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
