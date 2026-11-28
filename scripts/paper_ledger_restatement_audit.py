"""A bar that has already been printed is being rewritten in place.

Why this face exists. The risk board shot `C5_paper_recon` red with one word,
"账面不可信" (the book cannot be trusted), and the recon face behind it said
`BREACH` on the strength of a single identity: `strategy_scorecard`'s equity
differs from the ledger's for five of six traders (+34,238.82 CNY in total).

That identity is real, but it is not an arithmetic error, and calling it one
points the next reader at the wrong file. The ledger for cutoff 2026-11-27 was
written twice on 2026-11-28:

    15:35:24  (committed)  equity 5,934,743.99   <- what everyone read that day
    22:20:04  (worktree)   equity 5,900,505.17   <- what the ledger says now

Same cutoff, same paper account, no bar advance. `strategy_scorecard` was
generated at 22:18:07, two minutes before the second write, so it carries the
*earlier* printing of a bar that had already been published. The 34,238.82 is
the size of that restatement, to the cent, for all five traders.

So the red is real but its cause is one level lower than the recon face looks:
**the paper ledger is not append-only**. Any reader that copied a bar while it
was still settlable now prints a number that silently stopped being true, and
nothing on the ledger says so -- no `provisional` flag, no `restated` field, no
revision row. This face measures the restatement itself instead of the gap it
leaves in one reader.

What it answers:
  1. which (trader, cutoff) pairs were printed with more than one capital
     signature, and by how much;
  2. which pocket the difference landed in -- cash only, or positions and cash
     (a fill booked late reads as positions up / cash down at constant marks);
  3. which reader faces are still holding the pre-restatement printing, with
     the wall-clock distance to the ledger's own `updated` stamp;
  4. whether each reader's gap closes against the restatement arithmetic
     (reader - ledger == -(ledger_new - ledger_old)), item by item.

Rows that cannot be attributed -- a reader face that is missing, a ledger file
with no history -- are reported as unmeasured, never as zero.

Usage:
    python scripts/paper_ledger_restatement_audit.py run
    python scripts/paper_ledger_restatement_audit.py check
    python scripts/paper_ledger_restatement_audit.py selftest

Read-only: reads the ledger through `git show` and the working tree, writes no
ledger, no marks, no registration file. Exploratory measurement, no booking.
"""
import argparse
import datetime
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

PAPER_DIR = os.path.join(ROOT, "results", "paper")
OUT_JSON = os.path.join(ROOT, "results", "paper_ledger_restatement.json")
OUT_MD = os.path.join(ROOT, "research", "PAPER_LEDGER_RESTATEMENT.md")

SCAN_COMMITS = 25          # per file; enough to cover the paper window's churn
CENT = 0.01                # capital fields are printed to the cent
SNAP_SLACK_SEC = 2         # reader/writer stamps within 2s are "same write"

# reader faces that copy the ledger's capital block, and where the block lives.
# The tolerance belongs to the reader, not to us: a face that prints whole yuan
# cannot be judged at the cent -- that would be a red about its rounding, not
# about its arithmetic (E685 family: judge a printed number at its own ruler).
READERS = (
    ("strategy_scorecard", "results/strategy_scorecard.json", "card", 0.01),
    ("paper_export", "results/paper_export/latest.json", "export", 0.01),
    ("ceo_live_page", "docs/live_usage/LIVE-latest.json", "page", 0.5),
)


# ------------------------------------------------------------------ git / io
def _git(args):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def _relpath(abs_path):
    return os.path.relpath(abs_path, ROOT).replace(os.sep, "/")


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _parse_iso(stamp):
    if not stamp or not isinstance(stamp, str):
        return None
    s = stamp.strip().replace(" ", "T")
    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        return None


# ------------------------------------------------------------------ ledger
def capital_of(doc):
    if not isinstance(doc, dict):
        return None
    cap = doc.get("capital")
    if not isinstance(cap, dict):
        return None
    try:
        return {
            "equity": float(cap["equity_cny"]),
            "positions": float(cap["positions_value_cny"]),
            "cash": float(cap["cash_cny"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def signature(cap):
    return (round(cap["equity"], 2), round(cap["positions"], 2),
            round(cap["cash"], 2))


def load_versions(abs_path, limit=SCAN_COMMITS):
    """Capital the ledger carried for each commit that touched it, oldest first,
    with the working-tree copy appended as the newest version when it differs."""
    rel = _relpath(abs_path)
    versions = []
    shas = _git(["log", "--format=%H", "-n", str(limit), "--", rel])
    if shas:
        for sha in reversed(shas.decode("ascii", "replace").split()):
            body = _git(["show", "%s:%s" % (sha, rel)])
            if not body:
                continue
            try:
                doc = json.loads(body.decode("utf-8"))
            except ValueError:
                continue
            cap = capital_of(doc)
            if cap is None:
                continue
            versions.append({"source": "commit", "commit": sha[:10],
                             "updated": doc.get("updated"),
                             "cutoff": doc.get("cutoff"), "capital": cap})
    doc = _load_json(abs_path)
    cap = capital_of(doc)
    if cap is not None:
        versions.append({"source": "worktree", "commit": "worktree",
                         "updated": doc.get("updated"),
                         "cutoff": doc.get("cutoff"), "capital": cap})
    return _dedupe_consecutive(versions)


def _dedupe_consecutive(versions):
    """Two versions with the same capital signature are one printing; keep the
    newer (the worktree wins over a commit when nothing changed)."""
    out = []
    for v in versions:
        if out and signature(out[-1]["capital"]) == signature(v["capital"]) \
                and out[-1]["cutoff"] == v["cutoff"]:
            out[-1] = v
            continue
        out.append(v)
    return out


def classify(delta):
    if abs(delta["positions"]) < CENT and abs(delta["cash"]) >= CENT:
        return "CASH_ONLY"
    if abs(delta["positions"]) >= CENT:
        return "POSITIONS_AND_CASH"
    return "NO_POCKET_MOVED"


def detect_restatements(versions):
    """A restatement = one cutoff carrying more than one capital signature."""
    by_cut = {}
    for v in versions:
        cut = v.get("cutoff")
        if not cut:
            continue
        by_cut.setdefault(cut, []).append(v)
    events = []
    for cut, vs in sorted(by_cut.items()):
        prints = []
        for v in vs:
            sig = signature(v["capital"])
            if prints and signature(prints[-1]["capital"]) == sig:
                continue
            prints.append(v)
        if len(prints) < 2:
            continue
        first, last = prints[0], prints[-1]
        delta = {k: round(last["capital"][k] - first["capital"][k], 2)
                 for k in ("equity", "positions", "cash")}
        residual = round(delta["equity"]
                         - (delta["positions"] + delta["cash"]), 2)
        events.append({
            "cutoff": cut,
            "n_printings": len(prints),
            "first": {"commit": first["commit"], "updated": first["updated"],
                      "capital": {k: round(v, 2) for k, v in first["capital"].items()}},
            "last": {"commit": last["commit"], "updated": last["updated"],
                     "capital": {k: round(v, 2) for k, v in last["capital"].items()}},
            "delta": delta,
            "pocket": classify(delta),
            "identity_residual_cny": residual,
        })
    return events


# ------------------------------------------------------------------ readers
def reader_equity(kind, doc, tid):
    try:
        if kind == "card":
            cap = ((doc["trader_cards"] or {})[tid] or {}).get("live_paper", {}).get("capital") or {}
            return float(cap["equity_cny"])
        if kind == "export":
            for row in doc["traders"]:
                if row.get("trader") == tid:
                    return float(row["capital_cny"]["equity"])
            return None
        if kind == "page":
            for row in doc["members"]:
                if row.get("trader") == tid:
                    return float(row["equity_cny"])
            return None
    except (KeyError, TypeError, ValueError):
        return None
    return None


def reader_stamp(kind, doc):
    if kind == "card":
        return doc.get("generated")
    if kind == "export":
        return doc.get("generated_from_state_updated")
    if kind == "page":
        return doc.get("generated")
    return None


def load_readers():
    out = []
    for name, rel, kind, tol in READERS:
        path = os.path.join(ROOT, rel)
        doc = _load_json(path)
        stamp = reader_stamp(kind, doc) if doc else None
        out.append({"name": name, "path": rel, "kind": kind, "doc": doc,
                    "stamp": stamp, "tol": tol,
                    "missing": doc is None,
                    "stamp_missing": bool(doc) and not stamp})
    return out


def judge_readers(readers, ledger_now, events_by_tid):
    """Per reader, per trader: does its gap close against the restatement?"""
    at = datetime.datetime.now().astimezone()     # only used for age display
    rows = []
    for r in readers:
        if r["missing"]:
            rows.append({"reader": r["name"], "status": "FACE_MISSING"})
            continue
        lstamp = _parse_iso(r["stamp"])
        tol = r.get("tol", CENT)
        behind = []
        closed = 0
        checked = 0
        for tid, led in ledger_now.items():
            got = reader_equity(r["kind"], r["doc"], tid)
            if got is None:
                continue
            checked += 1
            gap = round(got - led["equity"], 2)
            ev = events_by_tid.get(tid)
            if abs(gap) < tol:
                continue
            expect = None
            if ev is not None:
                expect = round(-ev["delta"]["equity"], 2)
            if expect is not None and abs(gap - expect) < tol:
                closed += 1
            behind.append({"trader": tid, "reader_equity": got,
                           "ledger_equity": round(led["equity"], 2),
                           "gap_cny": gap, "restatement_delta_cny": expect,
                           "tol_cny": tol,
                           "gap_equals_restatement": bool(
                               expect is not None and abs(gap - expect) < tol)})
        led_stamp = _parse_iso(max((v["updated"] or "") for v in ledger_now.values()))
        lag_s = None
        if lstamp and led_stamp:
            # positive = the reader was written BEFORE the ledger bar, so it can
            # only be holding the earlier printing; negative = it was written after
            lag_s = round((led_stamp - lstamp).total_seconds(), 1)
        rows.append({
            "reader": r["name"], "path": r["path"], "status": "OK",
            "stamp": r["stamp"], "stamp_parsed": bool(lstamp),
            "ledger_stamp_max": led_stamp.isoformat() if led_stamp else None,
            "ledger_stamp_minus_reader_sec": lag_s,
            "equity_tol_cny": tol,
            "n_traders_compared": checked,
            "n_behind": len(behind),
            "n_gap_closed_by_restatement": closed,
            "behind": behind,
            "checked_at": at.isoformat(timespec="seconds"),
        })
    return rows


# ------------------------------------------------------------------- build
def load_ledger():
    """tid -> latest capital + updated stamp, plus the per-trader version tape."""
    ledger_now = {}
    tapes = {}
    for path in sorted(glob.glob(os.path.join(PAPER_DIR, "*_paper.json"))):
        doc = _load_json(path)
        tid = (doc or {}).get("trader") or os.path.basename(path).replace("_paper.json", "")
        cap = capital_of(doc)
        if cap is None:
            continue
        ledger_now[tid] = {"equity": cap["equity"], "positions": cap["positions"],
                           "cash": cap["cash"], "cutoff": doc.get("cutoff"),
                           "updated": doc.get("updated"),
                           "path": _relpath(path)}
        versions = load_versions(path)
        for v in versions:
            v["trader"] = tid
        tapes[tid] = versions
    return ledger_now, tapes


def build():
    ledger_now, tapes = load_ledger()
    if not ledger_now:
        return {"verdict": "NOT_MEASURED",
                "why": "no paper ledger readable under results/paper/*_paper.json",
                "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                "traders": [], "events": [], "readers": [], "summary": {}}

    per_trader = []
    events_by_tid = {}
    for tid, versions in tapes.items():
        events = detect_restatements(versions)
        if events:
            events_by_tid[tid] = events[-1]      # latest cutoff that moved
        per_trader.append({
            "trader": tid,
            "cutoff": ledger_now[tid]["cutoff"],
            "updated": ledger_now[tid]["updated"],
            "n_printings_scanned": len(versions),
            "version_tape": [{"commit": v["commit"], "updated": v["updated"],
                              "cutoff": v["cutoff"],
                              "capital": {k: round(x, 2) for k, x in v["capital"].items()}}
                             for v in versions],
            "restatements": events,
        })

    flat_events = [{"trader": t, **e} for t, evs in
                   ((t, d["restatements"]) for t, d in
                    ((p["trader"], p) for p in per_trader))
                   for e in evs]

    readers = judge_readers(load_readers(), ledger_now, events_by_tid)

    n_restated = sum(1 for p in per_trader if p["restatements"])
    total_delta = round(sum(e["delta"]["equity"] for e in flat_events), 2)
    n_pockets = {}
    for e in flat_events:
        n_pockets[e["pocket"]] = n_pockets.get(e["pocket"], 0) + 1
    behind_readers = [r["reader"] for r in readers
                      if r.get("status") == "OK" and r.get("n_behind")]
    closed = sum(r.get("n_gap_closed_by_restatement", 0) for r in readers
                 if r.get("status") == "OK")
    behind_total = sum(r.get("n_behind", 0) for r in readers
                       if r.get("status") == "OK")

    cutoff = max((p["cutoff"] or "") for p in per_trader)
    verdict = "LEDGER_RESTATES_SAME_BAR" if flat_events else "APPEND_ONLY"
    summary = {
        "n_traders": len(per_trader),
        "n_traders_restated": n_restated,
        "n_restatement_events": len(flat_events),
        "total_restated_equity_cny": total_delta,
        "pockets": n_pockets,
        "readers_behind": behind_readers,
        "n_reader_trader_gaps": behind_total,
        "n_gaps_closed_by_restatement": closed,
        "cutoff": cutoff,
    }
    statement = compose_statement(verdict, summary)
    return {
        "face": "paper_ledger_restatement_audit",
        "why": "the risk board says the book cannot be trusted; this face says "
               "which pocket of which bar moved after it was printed, and which "
               "reader is still holding the earlier printing",
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "verdict": verdict,
        "statement": statement,
        "summary": summary,
        "traders": per_trader,
        "events": flat_events,
        "readers": readers,
        "notes": [
            "Only (trader, cutoff) pairs printed with more than one capital "
            "signature count as a restatement; a normal bar advance is a new cutoff.",
            "POSITIONS_AND_CASH means marks stayed put while quantities moved -- "
            "the shape of a fill booked after the bar was published. CASH_ONLY "
            "moves the equity line without touching holdings.",
            "Cause is not determinable from the ledger alone: the paper books carry "
            "no trade tape, so this face reports the pocket, never the reason.",
            "A reader whose gap equals the restatement to the cent was reading the "
            "pre-restatement printing; one whose gap does not is a separate defect.",
        ],
    }


def compose_statement(verdict, summary):
    if verdict == "APPEND_ONLY":
        return ("No paper bar was printed with two different capital signatures in "
                "the scanned history: the ledger behaves append-only over these "
                "%d traders." % summary["n_traders"])
    return ("%d of %d paper traders restated a bar they had already printed "
            "(%d events, %+.2f CNY of equity rewritten). %d reader/trader gaps "
            "are open and %d of them close against the restatement arithmetic to "
            "the cent -- the gap is the restatement, not an arithmetic error."
            % (summary["n_traders_restated"], summary["n_traders"],
               summary["n_restatement_events"], summary["total_restated_equity_cny"],
               summary["n_reader_trader_gaps"],
               summary["n_gaps_closed_by_restatement"]))


# -------------------------------------------------------------------- write
def write_faces(face):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")

    s = face["summary"]
    lines = ["# Did the paper ledger rewrite a bar it had already printed?", "",
             "GENERATED-PROBE `%s` | evidence cutoff `%s`"
             % (face["generated"], face["evidence_cutoff"]), "",
             "**verdict: `%s`**" % face["verdict"], "", face["statement"], "",
             "| traders | restated | events | equity rewritten | reader gaps | "
             "gaps closed by restatement |", "|---|---|---|---|---|---|",
             "| %d | %d | %d | %+.2f CNY | %d | %d |" % (
                 s.get("n_traders", 0), s.get("n_traders_restated", 0),
                 s.get("n_restatement_events", 0),
                 s.get("total_restated_equity_cny", 0.0),
                 s.get("n_reader_trader_gaps", 0),
                 s.get("n_gaps_closed_by_restatement", 0)), ""]

    if face["events"]:
        lines += ["## Bars printed twice", "",
                  "| trader | cutoff | first printed | last printed | equity | "
                  "positions | cash | pocket |",
                  "|---|---|---|---|---|---|---|---|"]
        for e in face["events"]:
            lines.append("| %s | %s | %s | %s | %+.2f | %+.2f | %+.2f | %s |" % (
                e["trader"], e["cutoff"], e["first"]["updated"], e["last"]["updated"],
                e["delta"]["equity"], e["delta"]["positions"], e["delta"]["cash"],
                e["pocket"]))
        lines += ["", "The two stamps are the ledger's own `updated` field, so a "
                  "reader can date the rewrites without this face.", ""]

    lines += ["## Reader faces against the ledger as it stands today", "",
              "| reader | stamp | ledger minus reader (s, + = reader first) | "
              "tolerance (CNY) | traders compared | behind | gap closed by restatement |",
              "|---|---|---|---|---|---|---|"]
    for r in face["readers"]:
        if r.get("status") != "OK":
            lines.append("| %s | — | — | — | — | — | %s |"
                         % (r["reader"], r.get("status")))
            continue
        lines.append("| %s | %s | %s | %.2f | %d | %d | %d |" % (
            r["reader"], r["stamp"], r["ledger_stamp_minus_reader_sec"],
            r["equity_tol_cny"], r["n_traders_compared"], r["n_behind"],
            r["n_gap_closed_by_restatement"]))

    for r in face["readers"]:
        if r.get("status") == "OK" and r.get("behind"):
            lines += ["", "### %s, item by item" % r["reader"], "",
                      "| trader | reader | ledger | gap | restatement | matches |",
                      "|---|---|---|---|---|---|"]
            for b in r["behind"]:
                lines.append("| %s | %.2f | %.2f | %+.2f | %s | %s |" % (
                    b["trader"], b["reader_equity"], b["ledger_equity"], b["gap_cny"],
                    "—" if b["restatement_delta_cny"] is None
                    else "%+.2f" % b["restatement_delta_cny"],
                    "yes" if b["gap_equals_restatement"] else "**no**"))

    lines += ["", "## Notes", ""] + ["- " + n for n in face["notes"]] + [""]
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


# -------------------------------------------------------------------- check
_STABLE_KEYS = ("evidence_cutoff", "verdict", "summary", "events", "readers",
                "traders")


def _stable(face):
    """Everything judged, with volatile stamps (commits, clocks) removed, so a
    check right after a commit does not read a new commit sha as drift."""
    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items()
                    if k not in ("commit", "updated", "checked_at", "generated",
                                 "n_printings_scanned", "version_tape",
                                 "stamp", "ledger_stamp_max")}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    return strip({k: face.get(v) for k, v in zip(_STABLE_KEYS, _STABLE_KEYS)})


def run_check():
    if not os.path.exists(OUT_JSON):
        print("CHECK FAILED: face missing at %s. Rerun `run`." % OUT_JSON)
        return 3
    on_disk = json.load(open(OUT_JSON, encoding="utf-8"))
    fresh = build()
    if _stable(on_disk) != _stable(fresh):
        diff = [k for k in _STABLE_KEYS
                if _stable({"x": on_disk.get(k)})["x"] != _stable({"x": fresh.get(k)})["x"]]
        print("STALE: %s drifted from a fresh derive (%s). Rerun `run`."
              % (os.path.basename(OUT_JSON), ", ".join(diff)))
        return 3
    print("CHECK OK: %s matches a fresh derive from the same ledger and readers"
          % os.path.basename(OUT_JSON))
    return 0


# ----------------------------------------------------------------- selftest
def selftest():
    legs = 0
    fails = []

    def leg(name, ok, detail=""):
        nonlocal legs
        legs += 1
        if not ok:
            fails.append("%s %s" % (name, detail))

    def v(cutoff, eq, pos, cash, commit="c1", updated="2026-11-27 15:35:24"):
        return {"commit": commit, "updated": updated, "cutoff": cutoff,
                "capital": {"equity": eq, "positions": pos, "cash": cash}}

    # 1. a bar advance is not a restatement
    leg("new-cutoff-is-not-restatement",
        detect_restatements([v("2026-11-26", 100, 60, 40),
                             v("2026-11-27", 101, 61, 40)]) == [])
    # 2. same cutoff, same printing -> nothing
    leg("same-cutoff-same-capital-is-not-restatement",
        detect_restatements([v("2026-11-27", 100, 60, 40),
                             v("2026-11-27", 100, 60, 40, "c2")]) == [])
    # 3. same cutoff, cash moved -> one event, CASH_ONLY
    ev = detect_restatements([v("2026-11-27", 100, 60, 40),
                              v("2026-11-27", 90, 60, 30, "c2")])
    leg("same-cutoff-different-capital-is-restatement", len(ev) == 1, len(ev))
    leg("cash-only-pocket", ev and ev[0]["pocket"] == "CASH_ONLY",
        ev and ev[0]["pocket"])
    # 4. positions moved with cash -> POSITIONS_AND_CASH, delta closes
    ev2 = detect_restatements([v("2026-11-27", 100, 60, 40),
                               v("2026-11-27", 130, 160, -30, "c2")])
    leg("positions-and-cash-pocket",
        ev2 and ev2[0]["pocket"] == "POSITIONS_AND_CASH",
        ev2 and ev2[0]["pocket"])
    leg("delta-closes",
        ev2 and ev2[0]["identity_residual_cny"] == 0.0,
        ev2 and ev2[0]["identity_residual_cny"])
    leg("delta-values", ev2 and ev2[0]["delta"] == {"equity": 30.0,
                                                    "positions": 100.0,
                                                    "cash": -70.0},
        ev2 and ev2[0]["delta"])
    # 5. three printings: first and last, not the neighbour pair
    ev3 = detect_restatements([v("2026-11-27", 100, 60, 40),
                               v("2026-11-27", 95, 60, 35, "c2"),
                               v("2026-11-27", 90, 60, 30, "c3")])
    leg("first-and-last-not-neighbours",
        ev3 and ev3[0]["first"]["capital"]["equity"] == 100.0
        and ev3[0]["last"]["capital"]["equity"] == 90.0
        and ev3[0]["n_printings"] == 3, ev3 and ev3[0]["n_printings"])
    # 6. two different cutoffs that both restated -> two events
    leg("two-cutoffs-two-events",
        len(detect_restatements([v("2026-11-26", 100, 60, 40),
                                 v("2026-11-26", 99, 60, 39, "c2"),
                                 v("2026-11-27", 101, 61, 40, "c3"),
                                 v("2026-11-27", 100, 61, 39, "c4")])) == 2)
    # 7. dedupe: a worktree copy of the same printing does not double-count
    leg("dedupe-same-signature",
        len(_dedupe_consecutive([v("2026-11-27", 100, 60, 40, "c1"),
                                 v("2026-11-27", 100, 60, 40, "worktree")])) == 1)
    # 8. classify guards
    leg("classify-tiny-noise",
        classify({"positions": 0.004, "cash": 0.004}) == "NO_POCKET_MOVED")
    leg("classify-positions-only",
        classify({"positions": 5.0, "cash": 0.0}) == "POSITIONS_AND_CASH")
    # 9. reader gap closes against the restatement, with the right sign
    led = {"FIX-01": {"equity": 90.0, "positions": 60.0, "cash": 30.0,
                      "cutoff": "2026-11-27", "updated": "2026-11-28 22:20:04"}}
    ev_by = {"FIX-01": {"delta": {"equity": -10.0, "positions": 0.0, "cash": -10.0}}}
    card = {"generated": "2026-11-28T22:18:07",
            "trader_cards": {"FIX-01": {"live_paper": {"capital": {"equity_cny": 100.0}}}}}
    rows = judge_readers([{"name": "strategy_scorecard", "path": "x", "kind": "card",
                           "doc": card, "stamp": card["generated"], "tol": 0.01,
                           "missing": False, "stamp_missing": False}], led, ev_by)
    leg("reader-gap-closed", rows[0]["n_gap_closed_by_restatement"] == 1, rows[0])
    # positive lag = the reader was written BEFORE the ledger bar, i.e. it holds
    # the earlier printing (22:18:07 vs 22:20:04 = 117 s)
    leg("reader-lag-is-reader-written-first",
        rows[0]["ledger_stamp_minus_reader_sec"] == 117.0,
        rows[0]["ledger_stamp_minus_reader_sec"])
    # 10. a reader that drifted for another reason is NOT closed
    card2 = {"generated": "2026-11-28T23:00:00",
             "trader_cards": {"FIX-01": {"live_paper": {"capital": {"equity_cny": 95.0}}}}}
    rows2 = judge_readers([{"name": "strategy_scorecard", "path": "x", "kind": "card",
                            "doc": card2, "stamp": card2["generated"], "tol": 0.01,
                            "missing": False, "stamp_missing": False}], led, ev_by)
    leg("unrelated-drift-not-closed",
        rows2[0]["n_behind"] == 1 and rows2[0]["n_gap_closed_by_restatement"] == 0,
        rows2[0])
    # 10b. a reader that prints whole yuan is not a gap at 0.40 CNY (its own ruler)
    card3 = {"generated": "2026-11-28T23:00:00",
             "trader_cards": {"FIX-01": {"live_paper": {"capital": {"equity_cny": 90.4}}}}}
    rows3b = judge_readers([{"name": "ceo_live_page", "path": "x", "kind": "card",
                             "doc": card3, "stamp": card3["generated"], "tol": 0.5,
                             "missing": False, "stamp_missing": False}], led, ev_by)
    leg("whole-yuan-reader-not-a-gap", rows3b[0]["n_behind"] == 0, rows3b[0]["behind"])
    # 11. a missing reader face is unmeasured, never zero gaps
    rows3 = judge_readers([{"name": "paper_export", "path": "x", "kind": "export",
                            "doc": None, "stamp": None, "tol": 0.01,
                            "missing": True, "stamp_missing": False}], led, ev_by)
    leg("missing-reader-is-unmeasured", rows3[0]["status"] == "FACE_MISSING", rows3[0])
    # 12. no capital block -> not counted as a zero-capital trader
    leg("no-capital-block-is-none", capital_of({"capital": {}}) is None)
    leg("bad-floats-are-none",
        capital_of({"capital": {"equity_cny": "x", "positions_value_cny": 1,
                                "cash_cny": 1}}) is None)
    # 13. statement flips with the verdict
    leg("statement-append-only",
        "append-only" in compose_statement("APPEND_ONLY",
                                           {"n_traders": 6}).lower())
    leg("statement-restated",
        "restated" in compose_statement(
            "LEDGER_RESTATES_SAME_BAR",
            {"n_traders_restated": 4, "n_traders": 6, "n_restatement_events": 4,
             "total_restated_equity_cny": -34238.82, "n_reader_trader_gaps": 5,
             "n_gaps_closed_by_restatement": 5}))

    print("paper_ledger_restatement_audit selftest: %d/%d PASS"
          % (legs - len(fails), legs))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


# ---------------------------------------------------------------------- run
def run():
    face = build()
    write_faces(face)
    s = face["summary"]
    print("PAPER-LEDGER-RESTATEMENT %s" % face["verdict"])
    if face["verdict"] != "NOT_MEASURED":
        print("  traders=%d restated=%d events=%d equity_rewritten=%+.2f CNY"
              % (s["n_traders"], s["n_traders_restated"], s["n_restatement_events"],
                 s["total_restated_equity_cny"]))
        print("  reader gaps=%d closed_by_restatement=%d"
              % (s["n_reader_trader_gaps"], s["n_gaps_closed_by_restatement"]))
        for e in face["events"]:
            print("  %s %s %+.2f (%s)" % (e["trader"], e["cutoff"],
                                          e["delta"]["equity"], e["pocket"]))
    print("  -> %s" % os.path.relpath(OUT_JSON, ROOT))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return run_check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
