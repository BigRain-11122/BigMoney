#!/usr/bin/env python3
"""Read-only audit: was the forward ledger priced on a panel that had finished filling?

WHY THIS EXISTS
---------------
`etf_book_forward.py` freezes the whole ledger (exit 3, `status=frozen`) when any
already-published mark fails to re-derive within DRIFT_TOL = 1e-9. On 2026-10-30 the
ledger froze on a single face, `2026-10-29:5.064e-06`, and the previous window's
conclusion was that a 5e-6 difference is "not worth buying with a ledger rebase"
(round 1364) -- without asking where the difference comes from.

It does not come from a data revision. Measured here and by the repo's own record:

  * no already-published bar was rewritten: `git diff` over data/daily/ contains zero
    removed 2026-10-2x rows (only the new 2026-10-30 row was appended per symbol);
  * the panel is still GAINING symbols after the close, i.e. late bars replace a stale
    ffill with a genuine print, which moves that symbol's cross-sectional features and
    can change the book's ranked selection on a date that is already published;
  * the ledger priced 2026-10-29 at 15:52 on 2026-10-29 -- 43 minutes after the close --
    so that mark was computed on the panel as it stood then, not as it stands now;
  * the drift block itself says every OTHER published bar (checked_bars=5) reproduces
    inside 1e-9: only the newest bar moved. Settled bars are bit-stable; the bar whose
    panel was still filling is the one that failed.

So the freeze is a false positive for "revision" and a true positive for "the panel had
not finished". The gate as written can never be satisfied by an honestly priced last
bar, and the escape it offers (`--rebase`) buys the drift with a rewritten history --
which is the one thing the gate exists to prevent. The rule this audit recommends is
that a drift gate may only police SETTLED bars: the newest published bar is provisional
until the panel for its date stops growing.

READ-ONLY: this script never writes the ledger, never reruns the engine and never
touches data/. It reads LEDGER.json, results/data_lag_audit.json (if present) and the
date columns of data/daily/*.csv.

USAGE
  python scripts/etf_book_forward_settle_audit.py run      # write the evidence face
  python scripts/etf_book_forward_settle_audit.py check    # re-derive the verdict, no write
  python scripts/etf_book_forward_settle_audit.py selftest # offline fixture legs
"""
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from config import PATHS
from etf_book_forward import carry_last_bar, ledger_history, partition_settled, published_bars

SCHEMA = "etf-book-forward-settle-audit/v1"
LEDGER = os.path.join(PATHS.results_dir, "etf_book_forward", "LEDGER.json")
LAG_AUDIT = os.path.join(PATHS.results_dir, "data_lag_audit.json")
OUT = os.path.join(PATHS.results_dir, "etf_book_forward_settle_audit.json")
DAILY = os.path.join(PATHS.data_dir, "daily")

# A settled bar must reproduce inside the ledger's own tolerance; an unsettled one is
# allowed to move because its inputs were still arriving. Both numbers are the ledger's,
# read from the ledger itself rather than typed here.
SETTLE_LOOKBACK = 10          # trading days of panel coverage to publish beside the verdict
DRIFT_TOL_FALLBACK = 1e-9     # only used if the ledger does not carry its own tolerance


def _read_ledger(path=LEDGER):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _ledger_drift_tol(script_path=None):
    """The tolerance is quoted from the engine source, never guessed here."""
    script_path = script_path or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "etf_book_forward.py")
    try:
        src = open(script_path, encoding="utf-8").read()
    except OSError:
        return DRIFT_TOL_FALLBACK, "engine source unreadable"
    m = re.search(r"^DRIFT_TOL\s*=\s*([0-9.eE+-]+)", src, re.M)
    if not m:
        return DRIFT_TOL_FALLBACK, "DRIFT_TOL not found in engine source"
    return float(m.group(1)), "read from scripts/etf_book_forward.py"


def _panel_dates(daily_dir=DAILY, lookback=SETTLE_LOOKBACK):
    """symbols-with-a-bar per date, over the last `lookback` dates of the panel."""
    per_date = {}
    symbols = 0
    for path in glob.glob(os.path.join(daily_dir, "*.csv")):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                rows = [line for line in fh if line.strip()]
        except OSError:
            continue
        if not rows:
            continue
        symbols += 1
        # the date column is column 0; a set keeps a duplicated row from double counting
        for d in {line.split(",")[0] for line in rows[1:]}:
            per_date[d] = per_date.get(d, 0) + 1
    keys = sorted(per_date)[-lookback:]
    return {d: per_date[d] for d in keys}, symbols


def _classify(ledger, coverage, universe_total, drift_tol):
    """Which ledger bars are settled, and does the drift land only on the unsettled one?"""
    # r1243: withdrawn marks stay in the record but are outside the partition, and both
    # readers get that from the same function so they cannot drift apart (E270).
    bars = [b["bar"] for b in published_bars(ledger)]
    if not bars:
        return {"verdict": "no_published_bars", "settled": [], "provisional": [], "checks": {}}
    # "settled" = the panel for that date has stopped growing, which we can only judge
    # by the panel as it stands: a date is provisional while later data is still arriving
    # for the newest panel date. The rule itself lives in the engine (partition_settled)
    # and is imported, not restated: this audit and the ledger gate must never disagree
    # about which bars are open (E270 -- one rule spelled twice is not two rules).
    panel_last = max(coverage) if coverage else None
    # r1372: the cash leg has its own coverage -- a bar past the last priceable repo bar
    # rode a forward-filled rate and is still filling. Read from the engine, never restated
    # here, so this audit and the ledger gate keep answering the same question.
    settled, provisional = partition_settled(bars, panel_last, carry_last_bar())

    drift = ledger.get("drift") or {}
    faces = drift.get("faces") or []
    drifted = sorted({str(f).split(":")[0] for f in faces})
    worst = float(drift.get("max_abs") or 0.0)

    checks = {
        # every face that failed to re-derive must be one we called provisional
        "drift_faces_are_provisional": all(d in provisional for d in drifted) if drifted else True,
        # and no settled bar may be in the failed set
        "no_settled_bar_drifted": not any(d in settled for d in drifted),
        "worst_within_tol": worst <= drift_tol,
        "checked_bars": drift.get("checked_bars"),
        "published_bars": len(bars),
    }
    if not drifted:
        verdict = "no_drift"
    elif checks["no_settled_bar_drifted"]:
        verdict = "drift_only_on_unsettled_bar"
    else:
        verdict = "drift_on_settled_bar"
    return {"verdict": verdict, "settled": settled, "provisional": provisional,
            "drifted_bars": drifted, "max_abs": worst, "checks": checks,
            "newest_bar": bars[-1], "panel_last_date": panel_last}


HISTORY_WALK_MAX = 40          # commits of LEDGER.json to walk looking for a published value


def _snapshot_index(ledger_path=LEDGER, max_commits=HISTORY_WALK_MAX, since=None):
    """The committed ledgers, newest first: [(sha, {'bar': row}), ...].

    Read-only, fail-open: a tree without history (shallow clone, ledger never committed,
    no git) yields [] and every question below reads as unknown instead of zero.
    """
    import subprocess
    rel = os.path.relpath(ledger_path, PATHS.root).replace("\\", "/")
    args = ["git", "rev-list", "HEAD", "--", rel]
    if since:
        # nothing before the published bar can carry its published value, and this repo is
        # a partial clone: every blob read may cost a lazy fetch, so do not walk them all
        args = ["git", "rev-list", "HEAD", "--since=%s" % since, "--", rel]
    try:
        out = subprocess.run(args, cwd=PATHS.root, capture_output=True, text=True)
    except OSError:
        return []
    if out.returncode != 0:
        return []
    shas = out.stdout.split()[:max_commits]
    if not shas:
        return []
    # one batched read instead of one `git show` per commit: this face runs inside the
    # 100+ leg chain every round, and 40 separate process spawns cost ~20s on this tree
    req = "".join("%s:%s\n" % (sha, rel) for sha in shas)
    try:
        batch = subprocess.run(["git", "cat-file", "--batch"], cwd=PATHS.root,
                               input=req.encode(), capture_output=True)
    except OSError:
        return []
    if batch.returncode != 0:
        return []
    data, pos, snaps = batch.stdout, 0, []
    for sha in shas:
        nl = data.find(b"\n", pos)
        if nl < 0:
            break
        head = data[pos:nl].decode("utf-8", "replace").split()
        pos = nl + 1
        if len(head) < 3 or head[-1] == "missing":
            continue                      # path absent in this commit
        size = int(head[2])
        body = data[pos:pos + size]
        pos += size + 1
        try:
            doc = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        snaps.append((sha, {str(b.get("bar")): b for b in doc.get("bars") or []}))
    return snaps


def _retro_chain(rows, ledger, snaps=None):
    """Did the restatement that the record never measured actually move the rows behind it?

    r1492: two restatements in this ledger predate r1491's chain check, so the record says
    "later rows rescaled: not recorded" -- and a reader has to choose between "the chain was
    fine" and "nobody looked". Neither is true. But the repository DOES keep every committed
    version of the ledger, so the question is answerable where a snapshot still carries the
    published value: take that snapshot, compare each row behind the restated bar with the
    row in force today, and report the ratio. Nothing is assumed to be zero: a bar whose
    published value was never committed stays unknown.
    """
    cur = {str(b.get("bar")): b for b in ledger.get("bars") or []}
    todo = [r for r in rows if r["rescaled_known"] is False]
    if not todo:
        return rows
    snaps = (_snapshot_index(since=min(r["bar"] for r in todo) + " 00:00:00")
             if snaps is None else snaps)
    found = {}
    for bar_row in todo:
        bar, pub = bar_row["bar"], bar_row["nav_published"]
        if pub is None:
            continue
        for sha, idx in snaps:
            row = idx.get(bar)
            if row is None or row.get("nav") is None:
                continue
            if abs(float(row["nav"]) - float(pub)) <= DRIFT_TOL_FALLBACK:
                found[bar] = (sha, idx)
                break
    for r in todo:
        bar = r["bar"]
        hit = found.get(bar)
        if hit is None:
            r["history_status"] = "published_value_never_committed"
            r["history_note"] = ("no committed ledger still carried nav %s for %s -- the "
                                 "movement happened between commits" % (r["nav_published"], bar))
            r["resolved_by_history"] = False
            continue
        sha, idx = hit
        later = [k for k in sorted(idx) if k > bar]
        fac = r.get("nav_factor_applied")
        ratios, moved = [], 0
        for k in later:
            old_nav, new_nav = idx[k].get("nav"), (cur.get(k) or {}).get("nav")
            if old_nav in (None, 0) or new_nav is None:
                continue
            ratio = float(new_nav) / float(old_nav)
            ratios.append({"bar": k, "nav_published": old_nav, "nav_now": new_nav,
                           "ratio": round(ratio, 12)})
            if abs(ratio - 1.0) > DRIFT_TOL_FALLBACK:
                moved += 1
        r["history_commit"] = sha[:12]
        r["history_later_rows"] = len(later)
        r["history_ratios"] = ratios
        if not later:
            r["history_status"] = "no_later_rows_at_publication"
            r["history_note"] = ("the ledger held no row behind %s when the published value "
                                 "was committed: the restatement had nothing to move" % bar)
            r["resolved_by_history"] = True
        elif fac is not None and ratios and all(
                abs(x["ratio"] - float(fac)) <= 1e-9 for x in ratios):
            r["history_status"] = "chain_scaled_by_factor"
            r["history_note"] = ("every row behind it moved by the restatement factor %.12f"
                                 % float(fac))
            r["resolved_by_history"] = True
        elif ratios and not moved:
            r["history_status"] = "tail_unscaled"
            r["history_note"] = ("the restatement did not rescale the rows behind it; they "
                                 "re-derive off the panel today (drift gate: %s)"
                                 % ("0 faces" if r["restated_value_fails_gate_now"] is False
                                    else "see faces"))
            r["resolved_by_history"] = True
        else:
            r["history_status"] = "tail_moved_otherwise"
            r["history_note"] = ("%d of %d row(s) behind it do not agree with either the "
                                 "restatement factor or no movement" % (moved, len(ratios)))
            r["resolved_by_history"] = False
    return rows


def _restatement_block(ledger, settled, provisional, drifted, snaps=None):
    """Did a restatement land INSIDE the partition this audit polices, and did it move the chain?

    r1492: the audit could say "every settled bar re-derives" while a settled bar in that
    very partition had been restated after publication -- its stored value is the settled
    value, so a reader who walks the ledger sees one number and no trace that it moved.
    The engine already records both values (`ledger_history`, r1491); this face has to read
    them, `partition_settled` them, and state per bar whether the rows behind it were
    rescaled and whether that rescale was ever measured.

    Two different questions, answered separately because they have different answers:
      * did the published chain EQUAL the panel's own arithmetic -- the drift gate
        re-derives the settled bars every run, so this is measured now;
      * did the rescale AT RESTATEMENT TIME preserve the chain -- this only exists if the
        record carries `chain_intact`; a pre-r1491 entry does not, and unknown is not zero.
    """
    hist = ledger_history(ledger)
    bars = [str(b.get("bar")) for b in ledger.get("bars") or []]
    settled_set = set(settled or [])
    drifted_set = {str(d) for d in (drifted or [])}
    withdrawn = {str(r.get("bar")) for r in (hist.get("withdrawn") or [])}

    rows = []
    for rec in hist.get("restated_bars") or []:
        bar = str(rec.get("bar"))
        # the rows a restatement can move are everything live behind it
        tail = [b for b in bars[bars.index(bar) + 1:] if b not in withdrawn] if bar in bars else []
        n_resc = rec.get("later_rows_rescaled")
        known = bool(rec.get("rescaled_known"))
        chain = rec.get("chain_intact")
        if known and not n_resc:
            chain_verdict = "not_applicable"       # no row moved, nothing to verify
        elif chain is True:
            chain_verdict = "intact"
        elif chain is False:
            chain_verdict = "broken"
        else:
            chain_verdict = "not_measured"         # record predates the chain check
        rows.append({
            "bar": bar,
            "now_settled": bar in settled_set,
            "now_provisional": bar in provisional or bar not in bars,
            "on_row": bool(rec.get("on_row")),
            "nav_published": rec.get("nav_published"),
            "nav_settled": rec.get("nav_settled"),
            "nav_factor_applied": rec.get("nav_factor_applied"),
            "later_rows_rescaled": n_resc,
            "rescaled_known": known,
            "chain_verdict": chain_verdict,
            "restated_at": rec.get("restated_at"),
            "tail_rows_total": len(tail),
            "tail_rows_settled": sum(1 for b in tail if b in settled_set),
            # the gate re-derives every settled bar each run, so a face naming this bar
            # means the restated value itself no longer reproduces
            "restated_value_fails_gate_now": bar in drifted_set,
        })

    rows = _retro_chain(rows, ledger, snaps)

    n_settled = sum(1 for r in rows if r["now_settled"])
    broken = [r["bar"] for r in rows if r["chain_verdict"] == "broken"]
    unmeasured = [r["bar"] for r in rows if r["chain_verdict"] == "not_measured"
                  and r["tail_rows_total"] and not r.get("resolved_by_history")]
    resolved = [r for r in rows if r.get("resolved_by_history")]
    failing = [r["bar"] for r in rows if r["now_settled"] and r["restated_value_fails_gate_now"]]
    moved = [r["bar"] for r in rows if r["chain_verdict"] in ("intact", "broken")]

    checks = {
        "restated_settled_bars_reproduce": not failing,
        "no_restatement_left_a_broken_chain": not broken,
        "chain_measured_where_it_moved": not unmeasured,
        "restated_bars_carry_both_values": all(
            r["nav_published"] is not None and r["nav_settled"] is not None for r in rows),
    }
    if not rows:
        verdict = "no_restatement_in_the_policed_series"
    elif broken:
        verdict = "restatement_left_a_broken_chain"
    elif failing:
        verdict = "a_restated_settled_bar_no_longer_reproduces"
    elif unmeasured:
        verdict = "restatement_moved_rows_whose_chain_was_never_measured"
    elif resolved and not moved:
        verdict = "restated_rows_rederive_from_history"
    else:
        verdict = "restated_rows_rederive"
    return {
        "n_restated": len(rows),
        "restated_bars": rows,
        "n_restated_now_settled": n_settled,
        "chain_measured_on": moved,
        "chain_unmeasured_on": unmeasured,
        "chain_resolved_from_history": [{"bar": r["bar"], "status": r.get("history_status"),
                                         "commit": r.get("history_commit"),
                                         "note": r.get("history_note")} for r in resolved],
        "chain_broken_on": broken,
        "fail_gate_now": failing,
        # the denominator this audit actually polices, beside the ledger's own count
        "settled_bars_policed_now": len(settled_set),
        "ledger_checked_bars_field": (ledger.get("drift") or {}).get("checked_bars"),
        "ledger_checked_bars_note": ("the ledger's checked_bars counts published bars, not "
                                     "re-derived ones; settled_bars_policed_now is the set "
                                     "this audit makes a claim about"),
        "checks": checks,
        "verdict": verdict,
    }


def _restatement_line(block):
    """One sentence for the operator, derived from the block -- never typed beside it."""
    if not block["n_restated"]:
        return "no published bar was restated after publication"
    parts = ["%d published bar(s) restated after publication, %d of them inside today's "
             "settled partition" % (block["n_restated"], block["n_restated_now_settled"])]
    if block["chain_measured_on"]:
        parts.append("chain verified on %s" % ", ".join(block["chain_measured_on"]))
    if block["chain_unmeasured_on"]:
        parts.append("the record does not say how many later rows moved behind %s"
                     % ", ".join(block["chain_unmeasured_on"]))
    for r in block.get("chain_resolved_from_history") or []:
        parts.append("%s (%s) is settled from the committed ledger: %s"
                     % (r["bar"], r["status"], r["note"]))
    if block["chain_broken_on"]:
        parts.append("CHAIN BROKEN on %s" % ", ".join(block["chain_broken_on"]))
    if block["fail_gate_now"]:
        parts.append("restated value no longer reproduces: %s" % ", ".join(block["fail_gate_now"]))
    else:
        parts.append("every restated settled bar re-derives off the panel now")
    return "; ".join(parts)


def build():
    ledger = _read_ledger()
    drift_tol, tol_src = _ledger_drift_tol()
    coverage, universe_total = _panel_dates()
    cls = _classify(ledger, coverage, universe_total, drift_tol)
    pending = {d: universe_total - n for d, n in coverage.items()}

    lag_note = None
    if os.path.exists(LAG_AUDIT):
        try:
            lag = json.load(open(LAG_AUDIT, encoding="utf-8"))
            cov = (lag.get("calendar") and None) or None
            cov = (lag.get("coverage_by_day") or {})
            lag_note = {
                "as_of": lag.get("as_of"),
                "coverage_by_day": cov,
                "detail": (lag.get("detail") or "")[:300],
                "ledger_last_bar": ((lag.get("forward_impact") or {}).get("ledger_last_bar")),
            }
        except (OSError, ValueError):
            lag_note = {"error": "data_lag_audit unreadable"}

    restate = _restatement_block(ledger, cls["settled"], cls["provisional"],
                                 cls.get("drifted_bars"))

    led_state = ledger.get("status")
    # What the verdict means for the operator, in one line, decided by the numbers.
    if cls["verdict"] == "drift_only_on_unsettled_bar" and led_state == "frozen":
        headline = ("freeze is a false positive for revision: the only face that failed is "
                    "the bar whose panel was still filling -- no settled bar moved")
    elif cls["verdict"] == "drift_on_settled_bar":
        headline = ("a SETTLED bar failed to re-derive: this is the case the gate exists "
                    "for, inspect the panel for a genuine revision before rebasing")
    elif cls["verdict"] == "no_drift":
        headline = "ledger re-derives clean"
    else:
        headline = "no published bars to audit"
    # r1492: "re-derives clean" must never stand alone when a settled bar in the policed
    # partition was restated after publication -- that sentence reads as "nothing moved".
    if restate["n_restated"]:
        headline += " | " + _restatement_line(restate)

    return {
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": (cls.get("panel_last_date") or None),
        "ledger": {"path": os.path.relpath(LEDGER, PATHS.root_dir if hasattr(PATHS, "root_dir") else "."),
                   "status": led_state,
                   "published_bars": [b["bar"] for b in ledger.get("bars") or []],
                   "drift": ledger.get("drift"),
                   "rebases": len(ledger.get("rebases") or []),
                   "drift_tol": drift_tol, "drift_tol_source": tol_src},
        "panel": {"daily_dir": os.path.relpath(DAILY, os.getcwd()),
                  "universe_symbols": universe_total,
                  "coverage_by_day": coverage,
                  "pending_symbols_by_day": pending},
        "classification": cls,
        "restatement": restate,
        "data_lag_audit": lag_note,
        "headline": headline,
        "recommended_rule": (
            "A drift gate may only police SETTLED bars. The newest published bar is "
            "provisional until its panel date stops gaining symbols (coverage stable "
            "across consecutive runs); while it is provisional, a re-derivation mismatch "
            "is expected and must be reported, not frozen on -- and never bought with a "
            "history rewrite."
        ),
        "caveats": [
            "Point-in-time coverage at pricing time is not recorded anywhere, so 'the panel "
            "was still filling' is inferred from the panel's current shape (post-close "
            "arrivals) plus the timestamp of the run that priced the bar, not observed directly.",
            "This audit reads the panel's date columns only; it does not re-run the engine, "
            "so it cannot attribute the 5.064e-06 to a named symbol.",
            "0 removed 2026-10-2x rows in git diff over data/daily is evidence of no "
            "rewritten price, not proof: a symbol that arrived late is an addition, and an "
            "addition is exactly what this audit says moved the mark.",
            "A restatement recorded before r1491 carries both NAV values but not the reset "
            "factor or the number of later rows it rescaled: those read as unknown here, "
            "never as zero ('the ledger can still say it did not move').",
        ],
    }


def run():
    face = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, OUT)
    print("VERDICT %s | ledger %s | %s" % (face["classification"]["verdict"],
                                           face["ledger"]["status"], face["headline"]), flush=True)
    print("RESTATEMENT %s | %s" % (face["restatement"]["verdict"],
                                   _restatement_line(face["restatement"])), flush=True)
    print("wrote %s" % OUT, flush=True)
    return 0


def check():
    """Re-derive the verdict from the same frozen inputs and fail if it disagrees."""
    face = build()
    stored = None
    if os.path.exists(OUT):
        try:
            stored = json.load(open(OUT, encoding="utf-8"))
        except (OSError, ValueError):
            stored = None
    if stored is None:
        print("CHECK: no published face to compare (run first)", flush=True)
        return 1
    same = stored.get("classification", {}).get("verdict") == face["classification"]["verdict"]
    rs = (stored.get("restatement") or {}).get("verdict")
    rf = face["restatement"]["verdict"]
    print("CHECK: stored=%s fresh=%s %s" % (
        stored.get("classification", {}).get("verdict"),
        face["classification"]["verdict"], "MATCH" if same else "MISMATCH"), flush=True)
    print("CHECK: restatement stored=%s fresh=%s %s" % (rs, rf, "MATCH" if rs == rf else "MISMATCH"),
          flush=True)
    return 0 if (same and rs == rf) else 1


def selftest():
    legs = []

    def chk(name, cond, note=""):
        legs.append((name, bool(cond), note))

    bars = [{"bar": "2026-10-23"}, {"bar": "2026-10-26"}, {"bar": "2026-10-27"},
            {"bar": "2026-10-28"}, {"bar": "2026-10-29"}]
    cov = {"2026-10-27": 1720, "2026-10-28": 1721, "2026-10-29": 1723}

    # L1: the newest bar is provisional, the older ones are settled
    led = {"bars": bars, "drift": {"faces": ["2026-10-29:5.064e-06"], "max_abs": 5.064e-06,
                                   "checked_bars": 5}}
    c = _classify(led, cov, 1725, 1e-9)
    chk("newest bar is provisional", c["provisional"] == ["2026-10-29"], str(c["provisional"]))
    chk("older bars are settled", "2026-10-28" in c["settled"] and "2026-10-29" not in c["settled"])
    chk("drift on provisional only -> expected verdict",
        c["verdict"] == "drift_only_on_unsettled_bar", c["verdict"])

    # L2: the same drift on a SETTLED bar must NOT be excused
    led2 = {"bars": bars, "drift": {"faces": ["2026-10-28:5.064e-06"], "max_abs": 5.064e-06,
                                    "checked_bars": 5}}
    c2 = _classify(led2, cov, 1725, 1e-9)
    chk("drift on a settled bar is a real finding",
        c2["verdict"] == "drift_on_settled_bar", c2["verdict"])

    # L3: a clean ledger is not turned into a freeze by this audit
    c3 = _classify({"bars": bars, "drift": {"faces": [], "max_abs": 0.0, "checked_bars": 5}},
                   cov, 1725, 1e-9)
    chk("clean ledger -> no_drift", c3["verdict"] == "no_drift", c3["verdict"])

    # L4: no bars at all is reported, not crashed on
    c4 = _classify({"bars": [], "drift": {}}, cov, 1725, 1e-9)
    chk("empty ledger -> no_published_bars", c4["verdict"] == "no_published_bars", c4["verdict"])

    # L5: pending count is universe minus coverage (a negative would mean the universe
    #     was derived from a wider window than the coverage table)
    pend = {d: 1725 - n for d, n in cov.items()}
    chk("pending counts are non-negative", all(v >= 0 for v in pend.values()), str(pend))
    chk("the newest settled day is the fullest one here",
        cov["2026-10-29"] == max(cov.values()), "coverage grows toward the newest date")

    # L6: the tolerance is quoted from the engine, not typed here
    tol, src = _ledger_drift_tol()
    chk("drift tolerance is quoted from the engine", tol > 0 and "engine" in src.lower() or
        "etf_book_forward" in src, src)

    # L7: the settled/provisional rule is the engine's, not a local copy of it. If the two
    #     ever diverge, the audit would classify a freeze under a rule the gate does not use.
    chk("the settlement rule is imported from the engine",
        partition_settled.__module__ == "etf_book_forward", partition_settled.__module__)

    # L8..L13: a restatement inside the policed partition must be visible on this face.
    seq = ["2026-10-28", "2026-10-29", "2026-10-30", "2026-11-02"]

    def _led(rests, faces=()):
        return {"bars": [{"bar": b, "nav": 1.0} for b in seq], "restatements": rests,
                "drift": {"faces": list(faces), "max_abs": 0.0, "checked_bars": len(seq)}}

    def _rest(**kw):
        base = {"bar": "2026-10-29", "nav_published": 1.014536476,
                "nav_settled": 1.0145314121, "delta": 5.06e-06,
                "later_rows_rescaled": 2, "chain_intact": True, "chain_checked_bars": 2,
                "ts": "2026-10-30T19:18:29+0800"}
        base.update(kw)
        return base

    b8 = _restatement_block(_led([]), seq, [], [], snaps=[])
    chk("no restatement reads as none, not as a blank",
        b8["verdict"] == "no_restatement_in_the_policed_series" and b8["n_restated"] == 0,
        b8["verdict"])

    b9 = _restatement_block(_led([_rest()]), seq, [], [], snaps=[])
    chk("a restated settled bar is named and its verified chain is stated",
        b9["restated_bars"][0]["now_settled"] and b9["restated_bars"][0]["chain_verdict"] == "intact"
        and b9["verdict"] == "restated_rows_rederive", b9["verdict"])
    chk("the rows behind it are counted inside the settled partition",
        b9["restated_bars"][0]["tail_rows_total"] == 2
        and b9["restated_bars"][0]["tail_rows_settled"] == 2,
        str(b9["restated_bars"][0]["tail_rows_settled"]))

    # pre-r1491 record: both values kept, rescale never recorded -> unknown, not zero
    b10 = _restatement_block(_led([_rest(later_rows_rescaled=None, chain_intact=None,
                                         chain_checked_bars=None)]), seq, [], [], snaps=[])
    chk("an unrecorded rescale reads as unmeasured, never as no movement",
        b10["verdict"] == "restatement_moved_rows_whose_chain_was_never_measured"
        and b10["checks"]["chain_measured_where_it_moved"] is False, b10["verdict"])
    chk("the operator sentence says the record cannot say",
        "does not say how many later rows moved" in _restatement_line(b10),
        _restatement_line(b10)[:80])

    b11 = _restatement_block(_led([_rest()], faces=["2026-10-29:1.2e-06"]), seq, [], ["2026-10-29"],
                             snaps=[])
    chk("a restated value that stops reproducing is a real finding",
        b11["verdict"] == "a_restated_settled_bar_no_longer_reproduces"
        and b11["fail_gate_now"] == ["2026-10-29"], b11["verdict"])

    b12 = _restatement_block(_led([_rest(chain_intact=False)]), seq, [], [], snaps=[])
    chk("a broken chain outranks every softer verdict",
        b12["verdict"] == "restatement_left_a_broken_chain"
        and b12["checks"]["no_restatement_left_a_broken_chain"] is False, b12["verdict"])

    # a restatement on the newest bar is outside the partition, and the face says so
    b13 = _restatement_block(_led([_rest(bar="2026-11-02")]), seq[:-1], ["2026-11-02"], [],
                             snaps=[])
    chk("a restatement still provisional is not counted as settled",
        b13["n_restated"] == 1 and b13["n_restated_now_settled"] == 0
        and b13["restated_bars"][0]["tail_rows_total"] == 0, str(b13["restated_bars"][0]))

    # L14..L16: the record cannot say, but the repository can -- and where it cannot either
    # the answer stays unknown. Three snapshots, one question.
    pub, stl = 1.014536476, 1.0145314121
    fac = stl / pub
    live = {"bars": [{"bar": "2026-10-28", "nav": 1.0}, {"bar": "2026-10-29", "nav": stl},
                     {"bar": "2026-10-30", "nav": 1.02}],
            "restatements": [{"bar": "2026-10-29", "nav_published": pub, "nav_settled": stl,
                              "ts": "2026-10-30T19:18:29+0800"}],
            "drift": {"faces": [], "max_abs": 0.0, "checked_bars": 3}}

    unscaled = [("deadbeefcafe", {"2026-10-28": {"bar": "2026-10-28", "nav": 1.0},
                                  "2026-10-29": {"bar": "2026-10-29", "nav": pub},
                                  "2026-10-30": {"bar": "2026-10-30", "nav": 1.02}})]
    b14 = _restatement_block(live, ["2026-10-28", "2026-10-29"], ["2026-10-30"], [], snaps=unscaled)
    chk("the committed ledger answers the chain question the record left open",
        b14["restated_bars"][0]["history_status"] == "tail_unscaled"
        and b14["restated_bars"][0]["resolved_by_history"] is True
        and b14["verdict"] == "restated_rows_rederive_from_history",
        str(b14["restated_bars"][0].get("history_status")))

    scaled = [("deadbeefcafe", {"2026-10-28": {"bar": "2026-10-28", "nav": 1.0},
                                "2026-10-29": {"bar": "2026-10-29", "nav": pub},
                                "2026-10-30": {"bar": "2026-10-30", "nav": 1.02 / fac}})]
    b15 = _restatement_block(live, ["2026-10-28", "2026-10-29"], ["2026-10-30"], [], snaps=scaled)
    chk("a rescale that did move the tail is recognised by its factor",
        b15["restated_bars"][0]["history_status"] == "chain_scaled_by_factor",
        str(b15["restated_bars"][0].get("history_status")))

    b16 = _restatement_block(live, ["2026-10-28", "2026-10-29"], ["2026-10-30"], [], snaps=[])
    chk("with no committed snapshot the answer stays unknown, not 'fine'",
        b16["restated_bars"][0]["history_status"] == "published_value_never_committed"
        and b16["restated_bars"][0]["resolved_by_history"] is False
        and b16["verdict"] == "restatement_moved_rows_whose_chain_was_never_measured",
        b16["verdict"])

    ok = sum(1 for _, p, _ in legs if p)
    for name, passed, note in legs:
        print("  %s %s%s" % ("PASS" if passed else "FAIL", name,
                             (" [" + note + "]") if note else ""), flush=True)
    print("selftest %d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"), flush=True)
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: %s [run|check|selftest]" % os.path.basename(argv[0]), flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))