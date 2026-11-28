# -*- coding: utf-8 -*-
"""block_red_ownership.py -- whose red is it, and can this machine clear it?

Why this exists
---------------
The block board is the page that tells the line what to fix next, and a red
row is an instruction.  Two things the page cannot say today:

  1. **Who may write the artefact.**  `config/lane_io.C_SINGLE_WRITER_HOSTS`
     names a designated host for eleven figures (dashboard, both scorecards,
     the whole paper family).  On every other machine the writer exits 0
     having written nothing -- the row can be re-derived forever and never
     move.  r1789 already ruled that a row this machine cannot write must be
     annotated, not counted as a red; the board never learned that rule.
  2. **Whether the row is red about the money or about a copy.**  C5 reads
     `paper_equity_recheck.json`, which compares four reader faces against
     the ledger.  When a reader was printed *before* the ledger restated a
     bar, the row goes red although nothing is wrong with the book -- and the
     reader keeps the old printing until someone refreshes it.

This face answers both, per row, with the writer's own admission rule (r1789:
the guard answers, not the reader's opinion), the owner machine's heartbeat
(local + origin, the two signals lane_io itself uses), and -- for rows red
because of a stale upstream copy -- the closure arithmetic of the restatement
face that already measured it (reused, never recomputed here).

Classes
-------
  FIXABLE_HERE            artefact writable here and a re-derive clears it
  STALE_UPSTREAM_COPY     red only because an upstream reader face printed
                          before the ledger moved; names the face, the size of
                          the copy, and what the row reads once refreshed
  FOREIGN_WRITER_FRESH    the designated writer is alive: not this machine's
                          to clear (admission rule says skip)
  HUMAN_GAP               no command clears it -- supply / handover / queue work
  PRODUCER_DEFECT         the artefact's own verdict cannot be trusted (a
                          contract must change, not a re-derive)
  UNMEASURED              missing artefact or unreadable ownership -- never
                          silently promoted to FIXABLE

Read-only over every other face.  Writes `results/block_red_ownership.json`
and the rendered block of `research/BLOCK-RED-OWNERSHIP.md`.

    python scripts/block_red_ownership.py              # write face + doc block
    python scripts/block_red_ownership.py --check      # re-derive and compare
    python scripts/block_red_ownership.py --selftest   # offline legs
"""
from __future__ import annotations

import ast
import datetime as dt
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPECS = "research/QUANT-BLOCKS.json"
BOARD = "results/quant_block_board.json"
RESTATEMENT = "results/paper_ledger_restatement.json"
OUT = "results/block_red_ownership.json"
DOC = "research/BLOCK-RED-OWNERSHIP.md"

BEGIN = "<!-- BEGIN BLOCK-RED-OWNERSHIP (generated) -->"
END = "<!-- END BLOCK-RED-OWNERSHIP (generated) -->"

# Upstream reader faces each probe artefact compares itself against.  Declared
# here rather than discovered by grepping producers: a wrong guess would
# classify a row from the wrong face, and a declared list is auditable.
READS_OF = {
    "results/paper_equity_recheck.json": [
        "results/strategy_scorecard.json",
        "results/paper_export/latest.json",
    ],
}

# Rows whose clearing needs a specific sequence (the first command refreshes a
# stale reader copy the row compares against, the second re-derives the row).
CLEAR_COMMANDS = {
    "C5_paper_recon": ["python scripts/strategy_scorecard.py",
                       "python scripts/paper_equity_recheck.py"],
}

# Probe types whose remedy is not a re-derive at all.
HUMAN_PROBE_TYPES = {
    "supply": "write new pre-registered questions into WORK-BANK (bank=cards "
              "that already carry verdicts; 0 unconsumed)",
    "duty": "enqueue CPU work -- a re-derive cannot raise duty",
    "ingest_diff": None,  # handled as PRODUCER_DEFECT
}
PRODUCER_DEFECT_PROBE_TYPES = {"ingest_diff"}


# --------------------------------------------------------------------------
# io helpers (root-relative, so selftest can point at a temp tree)
# --------------------------------------------------------------------------
def _p(root, rel):
    return os.path.join(root, rel.replace("/", os.sep))


def load_json(root, rel):
    path = _p(root, rel)
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _parse_stamp(value):
    """ISO stamp -> datetime, or None.  Accepts 'YYYY-MM-DDTHH:MM:SS' with an
    optional offset and the ledger's space-separated form."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace(" ", "T", 1)
    try:
        return dt.datetime.fromisoformat(text)
    except Exception:
        return None


def _age_min(parsed, now=None):
    if parsed is None:
        return None
    ref = now or dt.datetime.now(parsed.tzinfo) if parsed.tzinfo else (now or dt.datetime.now())
    try:
        return (ref - parsed).total_seconds() / 60.0
    except Exception:
        return None


def heartbeat_age_min(hb, now=None):
    """Age of a machine heartbeat in minutes.  Epoch int preferred (smoke F7),
    `last_seen` ISO as fallback; None when nothing parses (dead-host face)."""
    if not isinstance(hb, dict):
        return None
    epoch = hb.get("heartbeat_epoch_utc")
    if isinstance(epoch, (int, float)) and not isinstance(epoch, bool):
        try:
            ref = now.timestamp() if now else None
            if ref is None:
                return max(0.0, (dt.datetime.now().timestamp() - float(epoch)) / 60.0)
            return max(0.0, (ref - float(epoch)) / 60.0)
        except Exception:
            pass
    return _age_min(_parse_stamp(hb.get("last_seen")), now)


def _git_blob(root, rel):
    """origin/main:<rel> as bytes, or None.  Native redirection is avoided on
    purpose (r2048: a PowerShell string round-trip is not the blob)."""
    try:
        r = subprocess.run(["git", "show", "origin/main:%s" % rel],
                           capture_output=True, cwd=root, timeout=15,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def host_age_origin(root, mid):
    raw = _git_blob(root, "fleet/machines/%s.json" % mid)
    if raw is None:
        return None
    try:
        return heartbeat_age_min(json.loads(raw.decode("utf-8", "replace")))
    except Exception:
        return None


def host_age_local(root, mid):
    return heartbeat_age_min(load_json(root, "fleet/machines/%s.json" % mid))


def machine_id(root):
    d = load_json(root, "fleet/machine.json")
    return str((d or {}).get("machine_id") or "")


# --------------------------------------------------------------------------
# writer admission (lane_io registry, read without importing it)
# --------------------------------------------------------------------------
def load_registry(root):
    """(registry, stale_min) parsed from config/lane_io.py.  Parsed with ast so
    selftest can point at a temp copy and so this face never triggers an
    import-side effect on a live tree."""
    path = _p(root, "config/lane_io.py")
    registry, stale = {}, 20.0
    if not os.path.exists(path):
        return registry, stale
    with io.open(path, encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return registry, stale
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == "C_SINGLE_WRITER_HOSTS":
                try:
                    registry = dict(ast.literal_eval(node.value))
                except Exception:
                    registry = {}
            elif target.id == "C_HOST_STALE_MIN":
                try:
                    stale = float(ast.literal_eval(node.value))
                except Exception:
                    pass
    return registry, stale


def registry_owner(registry, face_rel):
    """Designated owner for a face: exact path first, then the longest
    trailing-`/*` family token that prefixes it (lane_io semantics)."""
    if face_rel in registry:
        return registry[face_rel]
    best, best_len = None, -1
    for key, owner in registry.items():
        if key.endswith("/*"):
            prefix = key[:-1]
            if face_rel.startswith(prefix) and len(prefix) > best_len:
                best, best_len = owner, len(prefix)
    return best


def ownership_of(face_rel, mid, registry, stale_min, ages, guard_answer=None):
    """Classify who may write `face_rel` from this machine.

    ages: {machine_id: age_minutes_or_None}
    guard_answer: the real `shared_derive_write_allowed` verdict when available;
    recorded alongside so a disagreement between this replication and the real
    guard is visible instead of silent.

    Returns dict(status, owner, owner_age_local, owner_age_origin, note,
                 guard_agrees)
    """
    owner = registry_owner(registry, face_rel)
    if owner is None:
        return {"status": "UNREGISTERED", "owner": None, "note":
                "no designated writer -- legacy write behaviour (fail-open by design)",
                "owner_age_local": None, "owner_age_origin": None,
                "guard_agrees": None}
    if not mid:
        return {"status": "UNKNOWN", "owner": owner,
                "note": "this machine's id is unreadable -- ownership cannot be proved",
                "owner_age_local": ages.get(owner), "owner_age_origin": None,
                "guard_agrees": None}
    if owner == mid:
        return {"status": "LOCAL_OWNED", "owner": owner,
                "note": "designated writer is this machine",
                "owner_age_local": ages.get(owner),
                "owner_age_origin": ages.get(owner), "guard_agrees": None}
    a_local = ages.get(owner)
    a_origin = None if a_local is not None and a_local < stale_min else ages.get(owner + "#origin")
    fresh = [(a_local is not None and a_local < stale_min),
             (a_origin is not None and a_origin < stale_min)]
    if any(fresh):
        status = "FOREIGN_BLOCKED"
        note = ("designated writer %s is alive (local %s / origin %s min) -- a "
                "re-derive here exits without writing"
                % (owner, _fmt(a_local), _fmt(a_origin)))
    elif (a_local is not None and a_local >= stale_min) and \
            (a_origin is not None and a_origin >= stale_min):
        status = "WINDOW_OPEN"
        note = ("designated writer %s silent %.0f min (local) / %.0f min "
                "(origin) >= %.0f -- stale-takeover is open on this machine"
                % (owner, a_local, a_origin, stale_min))
    elif a_local is not None and a_local >= stale_min:
        status = "UNKNOWN"
        note = ("designated writer %s looks stale locally (%.0f min) but the "
                "origin heartbeat is unreadable -- r371: never take over on "
                "one signal" % (owner, a_local))
    else:
        status = "UNKNOWN"
        note = "heartbeat unreadable for %s -- ownership cannot be proved" % owner
    return {"status": status, "owner": owner, "note": note,
            "owner_age_local": a_local, "owner_age_origin": a_origin,
            "guard_agrees": _agrees(status, guard_answer)}


def _agrees(status, guard_answer):
    if guard_answer is None:
        return None
    allowed = status in ("UNREGISTERED", "LOCAL_OWNED", "WINDOW_OPEN")
    return bool(allowed) == bool(guard_answer)


def _fmt(v):
    return "n/a" if v is None else "%.0f" % v


# --------------------------------------------------------------------------
# stale upstream copies
# --------------------------------------------------------------------------
def upstream_copies(root, artefact_rel, restatement):
    """Reader faces the probe artefact compares against, when the restatement
    face says that reader is holding a pre-restatement printing.

    Returns (list_of_rows, closure_summary).  Every number is read from
    results/paper_ledger_restatement.json (the face that measured it) -- this
    function never recomputes a restatement.
    """
    rows, consistent = [], []
    if not isinstance(restatement, dict):
        return rows, {"measured": False, "why": "restatement face missing"}
    wanted = set(READS_OF.get(artefact_rel, []))
    if not wanted:
        return rows, {"measured": False, "why": "no declared upstream readers for this artefact"}
    for reader in restatement.get("readers") or []:
        path = reader.get("path")
        if path not in wanted:
            continue
        behind = reader.get("behind") or []
        stamp = {"reader": reader.get("reader"), "path": path,
                 "stamp": reader.get("stamp"),
                 "n_traders_compared": reader.get("n_traders_compared")}
        if not behind:
            # A reader with no trader behind is *consistent* with the ledger --
            # it is not a copy of an older printing (r2260-era defect: counting
            # it as one turns a clean reader into a phantom gap).
            consistent.append(stamp)
            continue
        n_closed = int(sum(1 for b in behind if b.get("gap_equals_restatement")))
        gap_sum = float(sum(float(b.get("gap_cny") or 0.0) for b in behind))
        closed_sum = float(sum(float(b.get("restatement_delta_cny") or 0.0)
                               for b in behind if b.get("gap_equals_restatement")))
        stamp.update({
            "ledger_stamp_max": reader.get("ledger_stamp_max"),
            "reader_older_sec": reader.get("ledger_stamp_minus_reader_sec"),
            "n_behind": reader.get("n_behind") or len(behind),
            "n_gap_closed_by_restatement": n_closed,
            # per-reader sums; a running total across readers would print one
            # reader's gap under another reader's name
            "gap_sum_cny": round(gap_sum, 2),
            "closed_sum_cny": round(closed_sum, 2),
            "all_closed": n_closed == len(behind),
        })
        rows.append(stamp)
    return rows, {
        "measured": bool(rows),
        "n_readers_behind": len(rows),
        "n_readers_consistent": len(consistent),
        "consistent_readers": consistent,
        "gap_sum_cny": round(sum(r["gap_sum_cny"] for r in rows), 2),
        "closed_sum_cny": round(sum(r["closed_sum_cny"] for r in rows), 2),
        "all_closed": bool(rows) and all(r["all_closed"] for r in rows),
    }


# --------------------------------------------------------------------------
# row classification
# --------------------------------------------------------------------------
def classify_row(row, spec, own, copies, closure, clear_cmd):
    """One red row -> a class with the evidence that decided it.

    Pure: every input is data, so the negative controls run without a tree.
    """
    probe_type = str((spec or {}).get("probe", {}).get("type") or "")
    artefact = (spec or {}).get("artifact")
    out = {"id": (spec or {}).get("id") or row.get("id"),
           "group": (spec or {}).get("group"),
           "seat": (spec or {}).get("seat"),
           "artefact": artefact,
           "board_detail": row.get("detail"),
           "probe_type": probe_type,
           "writer_status": own.get("status"),
           "writer_owner": own.get("owner"),
           "writer_note": own.get("note"),
           "clear_command": clear_cmd,
           "would_read": None}

    if probe_type in PRODUCER_DEFECT_PROBE_TYPES:
        out["class"] = "PRODUCER_DEFECT"
        out["why"] = ("the probe compares the producer's output with itself, so "
                      "its verdict cannot be trusted -- a re-derive cannot clear it")
        return out

    if probe_type in HUMAN_PROBE_TYPES:
        out["class"] = "HUMAN_GAP"
        out["why"] = HUMAN_PROBE_TYPES[probe_type] or "no command clears this row"
        return out

    if artefact and not own.get("status"):
        out["class"] = "UNMEASURED"
        out["why"] = "artefact not found on this machine"
        return out

    if own.get("status") == "FOREIGN_BLOCKED":
        out["class"] = "FOREIGN_WRITER_FRESH"
        out["why"] = own.get("note")
        return out

    if own.get("status") in ("UNKNOWN", None):
        out["class"] = "UNMEASURED"
        out["why"] = own.get("note") or "ownership unreadable"
        return out

    # Writable here.  Is the row red about a copy instead of the book?
    if copies:
        all_closed = bool(closure.get("all_closed"))
        out["class"] = "STALE_UPSTREAM_COPY"
        out["copies"] = copies
        out["closure"] = closure
        out["would_read"] = "PASS" if all_closed else "BREACH_STANDS"
        out["why"] = (
            "%d reader face%s hold%s a pre-restatement printing (%s CNY of gaps, "
            "%s CNY of it closes to the cent against the restatement arithmetic "
            "-- %s); refreshing the reader clears the row"
            % (closure.get("n_readers_behind") or 0,
               "" if (closure.get("n_readers_behind") or 0) == 1 else "s",
               "s" if (closure.get("n_readers_behind") or 0) == 1 else "",
               _money(closure.get("gap_sum_cny")),
               _money(closure.get("closed_sum_cny")),
               "all gaps closed" if all_closed else "NOT all gaps closed, a real "
               "arithmetic gap remains"))
        return out

    out["class"] = "FIXABLE_HERE"
    out["why"] = "artefact writable here and no stale upstream copy was found"
    out["would_read"] = "PASS" if clear_cmd else "UNMEASURED"
    return out


def _money(v):
    try:
        return "{:,.2f}".format(float(v))
    except (TypeError, ValueError):
        return "n/a"


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def _real_guard(root, face_rel):
    """The writer's own verdict when the package is importable; None offline."""
    try:
        if root not in sys.path:
            sys.path.insert(0, root)
        from config.lane_io import shared_derive_write_allowed  # noqa
        return bool(shared_derive_write_allowed(face_rel, verbose=False))
    except Exception:
        return None


def build(root=ROOT, now=None):
    specs = load_json(root, SPECS) or {}
    board = load_json(root, BOARD) or {}
    restatement = load_json(root, RESTATEMENT)
    registry, stale_min = load_registry(root)
    mid = machine_id(root)

    board_rows = {r.get("id"): r for r in (board.get("rows") or [])}
    machines = {}
    for name in os.listdir(_p(root, "fleet/machines")) if os.path.isdir(_p(root, "fleet/machines")) else []:
        if not name.endswith(".json"):
            continue
        m = name[:-5]
        machines[m] = host_age_local(root, m)

    ages = dict(machines)
    for owner in sorted({o for o in registry.values()} | {mid}):
        if owner in ages:
            continue
        ages[owner] = host_age_local(root, owner)

    def own(face_rel):
        o = ownership_of(face_rel, mid, registry, stale_min,
                         _ages_with_origin(root, ages, face_rel, registry, stale_min),
                         _real_guard(root, face_rel))
        return o

    # --- every block: who may write its artefact ---
    blocks = []
    for spec in specs.get("blocks") or []:
        rel = spec.get("artifact")
        b = {"id": spec.get("id"), "group": spec.get("group"),
             "name": spec.get("name"), "artefact": rel,
             "board_status": (board_rows.get(spec.get("id")) or {}).get("status"),
             "probe_type": (spec.get("probe") or {}).get("type"),
             "exists": bool(rel and os.path.exists(_p(root, rel))),
             "registered_owner": registry_owner(registry, rel) if rel else None}
        if rel and b["exists"]:
            o = own(rel)
            b["writer_status"] = o["status"]
            b["writer_note"] = o["note"]
            b["guard_agrees"] = o["guard_agrees"]
            b["owner_age_local_min"] = _round1(o.get("owner_age_local"))
            b["owner_age_origin_min"] = _round1(o.get("owner_age_origin"))
            try:
                b["artefact_mtime"] = dt.datetime.fromtimestamp(
                    os.path.getmtime(_p(root, rel))).strftime("%Y-%m-%dT%H:%M:%S")
            except OSError:
                b["artefact_mtime"] = None
        else:
            b["writer_status"] = None if rel else "NO_ARTEFACT"
            b["writer_note"] = "artefact missing on disk"
        blocks.append(b)

    # --- red rows: whose red is it ---
    reds = []
    for spec in specs.get("blocks") or []:
        row = board_rows.get(spec.get("id")) or {}
        if str(row.get("status")) != "RED":
            continue
        gent = (spec.get("probe") or {}).get("type")
        reds.append({"id": spec.get("id"), "group": spec.get("group"),
                     "name": spec.get("name"),
                     "detail": row.get("detail"), "probe_type": gent,
                     "artifact": spec.get("artifact")})
    # drop the intermediate list; the classification needs the per-row data
    classified = []
    for entry in reds:
        spec = next((s for s in specs.get("blocks") or [] if s.get("id") == entry["id"]), {})
        row = board_rows.get(entry["id"]) or {}
        rel = spec.get("artifact")
        if rel and not os.path.exists(_p(root, rel)):
            own_d = {"status": None, "owner": None, "note": "artefact missing on disk"}
        else:
            own_d = own(rel) if rel else {"status": None, "owner": None,
                                          "note": "no artefact declared"}
        copies, closure = ([], {"measured": False, "why": "not applicable"})
        if rel:
            copies, closure = upstream_copies(root, rel, restatement)
        cmd = CLEAR_COMMANDS.get(entry["id"])
        if cmd is None and spec.get("auto_fix"):
            cmd = [spec.get("auto_fix")]
        c = classify_row(row, spec, own_d, copies, closure,
                         cmd[0] if isinstance(cmd, list) and len(cmd) == 1 else cmd)
        if not spec.get("auto_fix") and not CLEAR_COMMANDS.get(entry["id"]) \
                and c.get("class") in ("FIXABLE_HERE", "STALE_UPSTREAM_COPY"):
            c["clear_command"] = "python scripts/%s.py" % (
                rel.rsplit("/", 1)[-1].replace(".json", "") if rel else "unknown")
        classified.append(c)

    # --- the registry itself: eleven faces that name another machine ---
    registry_faces = []
    for face, owner in sorted(registry.items()):
        entry = {"face": face, "owner": owner,
                 "owner_age_local_min": _round1(host_age_local(root, owner)),
                 "owner_age_origin_min": _round1(host_age_origin(root, owner))}
        if face.endswith("/*"):
            entry["kind"] = "family"
            entry["files_on_disk"] = _family_files(root, face)
        else:
            entry["kind"] = "exact"
            entry["on_disk"] = os.path.exists(_p(root, face))
            entry["age_min"] = None
            if entry["on_disk"]:
                try:
                    mt = os.path.getmtime(_p(root, face))
                except OSError:
                    mt = None
                if mt:
                    entry["mtime"] = dt.datetime.fromtimestamp(
                        mt).strftime("%Y-%m-%dT%H:%M:%S")
                    entry["age_min"] = round(
                        (dt.datetime.now().timestamp() - mt) / 60.0, 1)
        entry["verdict_from_here"] = own(face)["status"] if not face.endswith("/*") else None
        registry_faces.append(entry)

    counts = {}
    for c in classified:
        counts[c["class"]] = counts.get(c["class"], 0) + 1

    live = [f for f in registry_faces if f.get("owner_age_local_min") is not None]
    silent_owners = sorted({f["owner"] for f in live
                            if f["owner_age_local_min"] >= stale_min})
    stale_files = [f for f in registry_faces
                   if f.get("kind") == "exact" and f.get("age_min") is not None
                   and f["age_min"] > 60.0]
    headline = _headline(len(classified), counts, registry_faces, silent_owners,
                         stale_files, mid, stale_min)
    return {
        "face": "block_red_ownership",
        "why": ("a red row is an instruction; this face says whether the "
                "instruction can be carried out on this machine, and whether it "
                "is about the money or about a copy printed before the ledger moved"),
        "generated": dt.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "machine_id": mid,
        "stale_min": stale_min,
        "board_generated": board.get("generated"),
        "board_line_state": board.get("line_state"),
        "class_counts": counts,
        "n_red": len(classified),
        "n_clearable_here": sum(1 for c in classified
                                if c["class"] in ("FIXABLE_HERE", "STALE_UPSTREAM_COPY")),
        "verdict": _verdict(counts, registry_faces, silent_owners, stale_min),
        "statement": headline,
        "reds": classified,
        "registry_faces": registry_faces,
        "blocks": blocks,
    }


def _ages_with_origin(root, ages, face_rel, registry, stale_min):
    """Fill in `owner#origin` only when the local heartbeat is stale -- the
    origin cross-check exists for exactly that case (r366/r371)."""
    out = dict(ages)
    owner = registry_owner(registry, face_rel)
    if owner and (out.get(owner) is None or out.get(owner) >= stale_min):
        out[owner + "#origin"] = host_age_origin(root, owner)
    return out


def _family_files(root, token):
    prefix = token[:-1]
    base = _p(root, prefix.rstrip("/"))
    d = os.path.dirname(base) if not os.path.isdir(base) else base
    if not os.path.isdir(d):
        return 0
    return len([n for n in os.listdir(d) if os.path.isfile(os.path.join(d, n))])


def _round1(v):
    return None if v is None else round(float(v), 1)


def _verdict(counts, registry_faces, silent_owners, stale_min):
    clearable = counts.get("FIXABLE_HERE", 0) + counts.get("STALE_UPSTREAM_COPY", 0)
    total = sum(counts.values())
    if total == 0:
        return "NO_RED_ROWS"
    if clearable == total:
        return "ALL_REDS_CLEARABLE_HERE"
    if clearable == 0:
        return "NO_RED_ROW_IS_THIS_MACHINES_TO_CLEAR"
    return "PARTLY_CLEARABLE_HERE"


def _headline(n_red, counts, registry_faces, silent_owners, stale_files, mid, stale_min):
    clearable = counts.get("FIXABLE_HERE", 0) + counts.get("STALE_UPSTREAM_COPY", 0)
    parts = ["%d of %d red row(s) clearable from %s" % (clearable, n_red, mid or "?")]
    if counts.get("STALE_UPSTREAM_COPY"):
        parts.append("%d because an upstream reader printed before the ledger moved"
                     % counts["STALE_UPSTREAM_COPY"])
    look = [c for c in counts.items() if c[0] in
            ("FOREIGN_WRITER_FRESH", "HUMAN_GAP", "PRODUCER_DEFECT", "UNMEASURED")]
    if look:
        parts.append("the rest: " + ", ".join("%s=%d" % (k, v) for k, v in sorted(look)))
    if silent_owners:
        ages = sorted({(f["owner"], f.get("owner_age_local_min")) for f in registry_faces
                       if f["owner"] in silent_owners})
        parts.append("designated writers silent >= %.0f min (%s), so the "
                     "stale-takeover window is open on all %d registered face(s)"
                     % (stale_min,
                        ", ".join("%s %.0f min" % (o, a) for o, a in ages
                                  if a is not None),
                        len(registry_faces)))
        if stale_files:
            parts.append("%d of the registry's files on disk have not been "
                         "refreshed in over an hour" % len(stale_files))
    return "; ".join(parts)


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------
def render_block(face):
    L = []
    A = L.append
    A("### Block red ownership -- %s" % face["generated"])
    A("")
    A("machine **%s** | board %s (%s) | verdict **%s**"
      % (face["machine_id"], face["board_generated"], face["board_line_state"],
         face["verdict"]))
    A("")
    A(face["statement"])
    A("")
    A("| row | group | seat | class | what decides it | clear |")
    A("|---|---|---|---|---|---|")
    for c in face["reds"]:
        cmd = c.get("clear_command")
        if isinstance(cmd, list):
            cmd = " -> ".join(cmd)
        A("| %s | %s | %s | **%s** | %s | %s |"
          % (c["id"], c.get("group") or "", c.get("seat") or "", c["class"],
             (c.get("why") or "").replace("|", "/"), cmd or "--"))
    A("")
    sc = [c for c in face["reds"] if c["class"] == "STALE_UPSTREAM_COPY"]
    for c in sc:
        A("**%s** -- %s would read **%s** once the reader is refreshed."
          % (c["id"], c["artefact"], c["would_read"]))
        for cp in c.get("copies") or []:
            A("- reader `%s` printed %s, ledger stamp %s (%s s older), "
              "%s of %s traders behind, %s CNY of gap, %s CNY closes to the cent."
              % (cp["reader"], cp.get("stamp"), cp.get("ledger_stamp_max"),
                 _fmt_sec(cp.get("reader_older_sec")), cp["n_behind"],
                 cp["n_traders_compared"], _money(cp.get("gap_sum_cny")),
                 _money(cp.get("closed_sum_cny"))))
        if isinstance(c.get("clear_command"), list):
            A("")
            A("Sequence in a non-contention window: `%s`"
              % "` then `".join(c["clear_command"]))
        A("")
    A("")
    A("**Single-writer registry** (%d faces name another machine; a re-derive "
      "from anywhere else exits 0 without writing):" % len(face["registry_faces"]))
    A("")
    A("| face | owner | owner heartbeat (local / origin, min) | on disk | verdict from this machine |")
    A("|---|---|---|---|---|")
    for f in face["registry_faces"]:
        on_disk = "--"
        if f["kind"] == "family":
            on_disk = "%d file(s)" % f.get("files_on_disk")
        else:
            on_disk = "yes (%s)" % f.get("mtime") if f.get("on_disk") else "no"
        A("| `%s` | %s | %s / %s | %s | %s |"
          % (f["face"], f["owner"], _fmt(f.get("owner_age_local_min")),
             _fmt(f.get("owner_age_origin_min")), on_disk,
             f.get("verdict_from_here") or "--"))
    A("")
    A("Classes: FIXABLE_HERE | STALE_UPSTREAM_COPY | FOREIGN_WRITER_FRESH | "
      "HUMAN_GAP | PRODUCER_DEFECT | UNMEASURED. Read-only over every other face.")
    return "\n".join(L)


def _fmt_sec(v):
    try:
        return "%.0f" % float(v)
    except (TypeError, ValueError):
        return "n/a"


def write_doc(root, block):
    path = _p(root, DOC)
    head = ("# Block red ownership\n\n"
            "Whose red is it, and can this machine clear it?  Generated block "
            "below is re-derived by `scripts/block_red_ownership.py`; edit the "
            "script, not the numbers.\n\n")
    body = [(load_json(root, OUT) or {}).get("_doc_preamble") or ""]
    old = ""
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            old = fh.read()
    if BEGIN in old and END in old:
        head = old.split(BEGIN)[0]
        tail = old.split(END, 1)[1]
    else:
        tail = "\n"
    text = head + BEGIN + "\n" + block + "\n" + END + tail
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def strip_generated(face):
    out = dict(face)
    out.pop("generated", None)
    return out


def run(root=ROOT, write=True):
    face = build(root)
    if not write:
        return face
    path = _p(root, OUT)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    write_doc(root, render_block(face))
    print("block_red_ownership: %s" % face["verdict"])
    print("  " + face["statement"])
    for c in face["reds"]:
        print("  %-18s %-21s %s" % (c["id"], c["class"], (c.get("why") or "")[:110]))
    return face


VOLATILE = ("generated", "statement", "age_min", "owner_age_local_min",
            "owner_age_origin_min", "artefact_mtime", "mtime")


def stable_payload(face):
    """The part of the face that must be identical on a re-derive.  Heartbeat
    ages, wall-clock stamps and the sentence rendered from them move every
    minute while the classification does not, so they are excluded; everything
    that decides a row's class stays in."""
    def scrub(obj):
        if isinstance(obj, dict):
            return {k: scrub(v) for k, v in obj.items() if k not in VOLATILE}
        if isinstance(obj, list):
            return [scrub(v) for v in obj]
        return obj
    return scrub(strip_generated(face))


def check(root=ROOT):
    old = load_json(root, OUT)
    if old is None:
        print("check: %s missing" % OUT)
        return 3
    face = build(root)
    pa, pb = stable_payload(old), stable_payload(face)
    if pa != pb:
        for key in sorted(set(pa) | set(pb)):
            if pa.get(key) != pb.get(key):
                print("check: field differs: %s" % key)
        return 3
    path = _p(root, DOC)
    if not os.path.exists(path):
        print("check: %s missing" % DOC)
        return 3
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    if BEGIN not in text or END not in text:
        print("check: generated markers missing from %s" % DOC)
        return 3
    rendered = text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")
    if rendered != render_block(old):
        print("check: rendered block differs from the stored face "
              "(edit the script, not the doc)")
        return 3
    print("check: ok (%d red rows, %d registered faces)"
          % (face["n_red"], len(face["registry_faces"])))
    return 0


# --------------------------------------------------------------------------
# selftest (offline: no tree, no git, no network)
# --------------------------------------------------------------------------
def _mkface(**kw):
    base = {"id": "X", "group": "g", "seat": "s", "artifact": "results/x.json",
            "probe": {"type": "file_fresh"}, "auto_fix": None}
    base.update(kw)
    return base


def selftest():
    reg = {"results/strategy_scorecard.json": "bm-a", "results/paper/*": "bm-a",
           "results/daily_scorecard.json": "bm-a"}
    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    # 1 exact registry hit names the owner
    leg("exact registry hit names the owner",
        registry_owner(reg, "results/strategy_scorecard.json") == "bm-a")

    # 2 family token matches a member file and nothing outside it
    leg("family token matches members only",
        registry_owner(reg, "results/paper/X_paper.json") == "bm-a"
        and registry_owner(reg, "results/paperX/Y.json") is None)

    # 3 unregistered face keeps legacy behaviour
    own = ownership_of("results/foo.json", "bm-c", reg, 20.0, {"bm-a": 5.0})
    leg("unregistered face -> UNREGISTERED (legacy write)", own["status"] == "UNREGISTERED")

    # 4 own face is writable even with a stale heartbeat
    own = ownership_of("results/daily_scorecard.json", "bm-a", reg, 20.0,
                       {"bm-a": 5000.0, "bm-a#origin": 5000.0}, guard_answer=True)
    leg("own face -> LOCAL_OWNED despite stale heartbeat",
        own["status"] == "LOCAL_OWNED")

    # 5 foreign face with a fresh heartbeat is blocked
    own = ownership_of("results/daily_scorecard.json", "bm-c", reg, 20.0,
                       {"bm-a": 3.0}, guard_answer=False)
    leg("foreign + fresh heartbeat -> FOREIGN_BLOCKED", own["status"] == "FOREIGN_BLOCKED")
    leg("and the real guard agrees", own["guard_agrees"] is True)

    # 6 foreign face with both signals stale opens takeover
    own = ownership_of("results/daily_scorecard.json", "bm-c", reg, 20.0,
                       {"bm-a": 500.0, "bm-a#origin": 480.0}, guard_answer=True)
    leg("foreign + both signals stale -> WINDOW_OPEN", own["status"] == "WINDOW_OPEN")

    # 7 one stale signal and no origin reading is not a takeover
    own = ownership_of("results/daily_scorecard.json", "bm-c", reg, 20.0,
                       {"bm-a": 500.0}, guard_answer=None)
    leg("stale local + unreadable origin -> UNKNOWN (never take over blind)",
        own["status"] == "UNKNOWN")

    # 8 unreadable heartbeat is UNKNOWN, never FIXABLE
    own = ownership_of("results/daily_scorecard.json", "bm-c", reg, 20.0,
                       {"bm-a": None, "bm-a#origin": None})
    leg("no heartbeat signal -> UNKNOWN", own["status"] == "UNKNOWN")

    # 9 unreadable machine id cannot claim ownership
    own = ownership_of("results/daily_scorecard.json", "", reg, 20.0, {"bm-a": 1.0})
    leg("no machine id -> UNKNOWN", own["status"] == "UNKNOWN")

    # 10 a fresh stale-copy row says PASS and prints the closure
    rest = {"readers": [{"reader": "strategy_scorecard",
                         "path": "results/strategy_scorecard.json",
                         "stamp": "2026-11-28T22:18:07",
                         "ledger_stamp_max": "2026-11-28T22:20:14",
                         "ledger_stamp_minus_reader_sec": 127.0,
                         "n_traders_compared": 6, "n_behind": 2,
                         "behind": [{"trader": "A", "gap_cny": 3196.39,
                                     "restatement_delta_cny": 3196.39,
                                     "gap_equals_restatement": True},
                                    {"trader": "B", "gap_cny": 11486.91,
                                     "restatement_delta_cny": 11486.91,
                                     "gap_equals_restatement": True}]}]}
    import tempfile
    tmp = tempfile.mkdtemp(prefix="bro-selftest-")
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    with io.open(os.path.join(tmp, RESTATEMENT), "w", encoding="utf-8") as fh:
        json.dump(rest, fh)
    copies, closure = upstream_copies(tmp, "results/paper_equity_recheck.json", rest)
    leg("stale copy arithmetic is summed from the restatement face",
        len(copies) == 1 and abs(closure["gap_sum_cny"] - 14683.30) < 0.005
        and closure["all_closed"] is True,
        "%s" % closure)
    c = classify_row({"detail": "verdict=BREACH"}, _mkface(
        id="C5_paper_recon", artifact="results/paper_equity_recheck.json",
        probe={"type": "json_predicate"}), {"status": "UNREGISTERED", "owner": None,
                                            "note": "legacy"}, copies, closure, None)
    leg("stale-copy row -> STALE_UPSTREAM_COPY and would read PASS",
        c["class"] == "STALE_UPSTREAM_COPY" and c["would_read"] == "PASS")

    # 11 negative control: one unexplained gap keeps the row BREACH
    rest2 = json.loads(json.dumps(rest))
    rest2["readers"][0]["behind"][1]["gap_equals_restatement"] = False
    _, closure2 = upstream_copies(tmp, "results/paper_equity_recheck.json", rest2)
    c2 = classify_row({"detail": "verdict=BREACH"}, _mkface(
        id="C5_paper_recon", artifact="results/paper_equity_recheck.json",
        probe={"type": "json_predicate"}), {"status": "UNREGISTERED", "owner": None,
                                            "note": "legacy"},
        copies, closure2, None)
    leg("one gap not explained by the restatement -> would still read BREACH",
        c2["would_read"] == "BREACH_STANDS")

    # 12 supply/duty/ingest rows are never called clearable
    for ptype, want in (("supply", "HUMAN_GAP"), ("duty", "HUMAN_GAP"),
                        ("ingest_diff", "PRODUCER_DEFECT")):
        cc = classify_row({"detail": "x"}, _mkface(probe={"type": ptype}),
                          {"status": "UNREGISTERED", "owner": None, "note": ""}, [], {},
                          None)
        leg("%s probe -> %s (a re-derive cannot clear it)" % (ptype, want),
            cc["class"] == want)

    # 13 foreign-fresh row is not clearable here even with a command on the spec
    cf = classify_row({"detail": "x"}, _mkface(
        probe={"type": "file_fresh"}, auto_fix="python scripts/x.py"),
        {"status": "FOREIGN_BLOCKED", "owner": "bm-a", "note": "alive"},
        [], {}, "python scripts/x.py")
    leg("foreign-fresh row -> FOREIGN_WRITER_FRESH", cf["class"] == "FOREIGN_WRITER_FRESH")

    # 14 missing artefact is UNMEASURED, never FIXABLE
    cm = classify_row({"detail": "x"}, _mkface(probe={"type": "file_fresh"}),
                      {"status": None, "owner": None, "note": "artefact missing"},
                      [], {}, "python scripts/x.py")
    leg("missing artefact -> UNMEASURED", cm["class"] == "UNMEASURED")

    # 15 headline/verdict arithmetic: zero clearable reads as nobody's job
    v = _verdict({"HUMAN_GAP": 2, "PRODUCER_DEFECT": 1}, [], ["bm-a"], 20.0)
    leg("verdict separates 'clearable here' from 'not ours'",
        v == "NO_RED_ROW_IS_THIS_MACHINES_TO_CLEAR")

    # 16 heartbeat parsing prefers the epoch int and rejects strings
    hb = {"heartbeat_epoch_utc": 1795889702, "last_seen": "1999-01-01T00:00:00+08:00"}
    now = dt.datetime.fromtimestamp(1795889702 + 3600)
    leg("epoch int preferred over last_seen",
        abs(heartbeat_age_min(hb, now=now) - 60.0) < 0.001)
    leg("string epoch is not a heartbeat (smoke F7 type law)",
        heartbeat_age_min({"heartbeat_epoch_utc": "1795889702"}) is None)

    # 17 a reader with zero traders behind is consistent, not a stale copy
    rest3 = {"readers": [
        {"reader": "strategy_scorecard", "path": "results/strategy_scorecard.json",
         "stamp": "2026-11-28T22:18:07", "n_traders_compared": 6, "n_behind": 2,
         "behind": [{"trader": "A", "gap_cny": 3196.39,
                     "restatement_delta_cny": 3196.39,
                     "gap_equals_restatement": True},
                    {"trader": "B", "gap_cny": 11486.91,
                     "restatement_delta_cny": 11486.91,
                     "gap_equals_restatement": True}]},
        {"reader": "paper_export", "path": "results/paper_export/latest.json",
         "stamp": "2026-11-28 22:20:14", "n_traders_compared": 6, "n_behind": 0,
         "behind": []}]}
    rows3, closure3 = upstream_copies(tmp, "results/paper_equity_recheck.json", rest3)
    leg("a reader with no trader behind is not a stale copy",
        len(rows3) == 1 and rows3[0]["reader"] == "strategy_scorecard"
        and closure3["n_readers_consistent"] == 1)
    leg("per-reader sums are independent (no running total across readers)",
        abs(rows3[0]["gap_sum_cny"] - 14683.30) < 0.005
        and abs(closure3["gap_sum_cny"] - 14683.30) < 0.005)
    leg("all copies closed -> closure reads PASS-able",
        closure3["all_closed"] is True)

    ok = sum(1 for _, passed, _ in legs if passed)
    for name, passed, detail in legs:
        print("%s  %s%s" % ("PASS" if passed else "FAIL", name,
                            "" if passed or not detail else "  [%s]" % detail))
    print("%d/%d legs pass" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
