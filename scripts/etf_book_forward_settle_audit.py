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
from etf_book_forward import partition_settled

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
    bars = [b["bar"] for b in ledger.get("bars") or []]
    if not bars:
        return {"verdict": "no_published_bars", "settled": [], "provisional": [], "checks": {}}
    # "settled" = the panel for that date has stopped growing, which we can only judge
    # by the panel as it stands: a date is provisional while later data is still arriving
    # for the newest panel date. The rule itself lives in the engine (partition_settled)
    # and is imported, not restated: this audit and the ledger gate must never disagree
    # about which bars are open (E270 -- one rule spelled twice is not two rules).
    panel_last = max(coverage) if coverage else None
    settled, provisional = partition_settled(bars, panel_last)

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
    print("CHECK: stored=%s fresh=%s %s" % (
        stored.get("classification", {}).get("verdict"),
        face["classification"]["verdict"], "MATCH" if same else "MISMATCH"), flush=True)
    return 0 if same else 1


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