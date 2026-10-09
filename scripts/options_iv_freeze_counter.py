"""OPTIONS IV panel prereg freeze-window counter -- P3 explore E2 companion.

E2 (state/queue/explore.md head): "Options IV panel prereg roadmap
(T-69 forward archive 12-month freeze-window counting; roadmap piece
first)". Roadmap piece = research/shortline/OPTIONS_IV_PREREG_ROADMAP.md;
this script is its runnable face.

T-67 s2 DEFINITIVE BATCH LAW: a new options prereg is gated on >=12
months of FORWARD history accumulated by the wave-2b lane (T-69,
scripts/update_options.py, bm-a lane owner). Retention-window backfill
rows inside each contract file predate the lane and do NOT count toward
the window -- the gate metric is elapsed calendar months from the pinned
lane-start anchor to the archive's latest collected bar date.

Pinned anchor (frozen):
  FORWARD_LANE_START = "2026-09-24"  (first completed pass target bar date)
  Evidence: first commit of scripts/update_options.py 2026-09-25 23:23:04
  +0800, round 195 bm-a, message "FIRST LIVE SMOKE ... last_pass=2026-09-24".

This script MEASURES ONLY: reads the local forward archive, counts the
freeze window, writes evidence. Zero network, zero panel writes, zero
backtest, no engine touch. Read-only on any machine (no lane-ownership
gate needed -- it never writes data/ faces).

Faces (local only):
  data/options/daily/*.csv          per-contract forward archive
                                    (date,open,high,low,close,volume)
  data/options/forward_meta.json    expiry face (descriptive only)
  results/options_update_status.json lane last-pass disclosure (optional)

Evidence: results/options_iv_freeze_counter.json

Usage:
    python scripts/options_iv_freeze_counter.py             # count + evidence
    python scripts/options_iv_freeze_counter.py selftest    # offline guards

Exit codes: 0 = counted (gate open/passed is a reading, not an error) |
            2 = machinery fault (archive dir missing / unreadable).
"""
import datetime as dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "options", "daily")
META_JSON = os.path.join(ROOT, "data", "options", "forward_meta.json")
LANE_STATUS = os.path.join(ROOT, "results", "options_update_status.json")
OUT = os.path.join(ROOT, "results", "options_iv_freeze_counter.json")

FORWARD_LANE_START = "2026-09-24"   # pinned anchor, see module docstring
FREEZE_MONTHS = 12                  # T-67 s2 law constant
# O-20261009-1105 CEO direct order ("no options"): the T-69 forward
# collection lane is RETIRED (anti-waste law, zero forward consumers,
# re-enable only via a new CEO order). The archive below is therefore
# as-collected FROZEN -- this counter measures that frozen archive; the
# freeze gate can never pass while the lane stays retired.
LANE_STATE = ("retired per O-20261009-1105 (anti-waste law; no options "
              "per CEO direct order, no approval channel; re-enable only "
              "via a new CEO order; archive as-collected frozen at "
              "2026-09-30, 254 contracts, 16812 rows)")


def _ym_add(ym, k):
    """'2026-09' + 12 -> '2027-09' (calendar month add, day-preserving)."""
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) + k
    return "%04d-%02d" % (t // 12, t % 12 + 1)


def _months_between(d1, d2):
    """Complete elapsed calendar months d1 -> d2 (anniversary semantics:
    2026-09-24 -> 2026-10-23 = 0, -> 2026-10-24 = 1). d2 < d1 -> 0."""
    a, b = d1.split("-"), d2.split("-")
    months = (int(b[0]) - int(a[0])) * 12 + (int(b[1]) - int(a[1]))
    if int(b[2]) < int(a[2]):
        months -= 1
    return max(0, months)


def _scan_archive(panel_dir, anchor=FORWARD_LANE_START):
    """Single pass over per-contract CSVs. Returns (stats, unreadable).

    Rows are counted per calendar month; min/max bar dates tracked across
    files. Rows dated < anchor are retention-window backfill (counted
    separately as rows_pre_anchor, excluded from the forward face size).
    """
    if not os.path.isdir(panel_dir):
        raise FileNotFoundError("archive dir missing: %s" % panel_dir)
    names = sorted(fn for fn in os.listdir(panel_dir) if fn.endswith(".csv"))
    stats = {
        "contracts_on_disk": len(names),
        "rows_total": 0,
        "rows_pre_anchor": 0,
        "rows_on_or_after_anchor": 0,
        "per_month_rows": {},
        "min_bar_date": None,
        "max_bar_date": None,
        "contracts_with_rows": 0,
    }
    unreadable = []
    for fn in names:
        path = os.path.join(panel_dir, fn)
        try:
            with open(path, encoding="utf-8-sig") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            rows = 0
            for ln in lines:
                date = ln.split(",", 1)[0]
                if len(date) != 10 or date[4] != "-" or date[7] != "-":
                    continue  # header / malformed -> not a bar row
                rows += 1
                ym = date[:7].replace("-", "")
                stats["per_month_rows"][ym] = \
                    stats["per_month_rows"].get(ym, 0) + 1
                if stats["min_bar_date"] is None or date < stats["min_bar_date"]:
                    stats["min_bar_date"] = date
                if stats["max_bar_date"] is None or date > stats["max_bar_date"]:
                    stats["max_bar_date"] = date
                if date < anchor:
                    stats["rows_pre_anchor"] += 1
                else:
                    stats["rows_on_or_after_anchor"] += 1
            if rows:
                stats["contracts_with_rows"] += 1
            stats["rows_total"] += rows
        except Exception as e:
            unreadable.append({"file": fn, "error": "%s: %s" % (
                type(e).__name__, str(e)[:160])})
    return stats, unreadable


def count_freeze(panel_dir, anchor=FORWARD_LANE_START, freeze=FREEZE_MONTHS):
    """Full counting face. Pure local; raises only on machinery faults."""
    stats, unreadable = _scan_archive(panel_dir, anchor)
    if stats["contracts_on_disk"] == 0:
        raise FileNotFoundError("archive empty: %s" % panel_dir)
    if stats["max_bar_date"] is None:
        raise ValueError("archive has no bar rows: %s" % panel_dir)
    elapsed = _months_between(anchor, stats["max_bar_date"])
    remaining = max(0, freeze - elapsed)
    elig_date = "%s-%02d" % (_ym_add(anchor[:7], freeze), int(anchor[8:10]))
    out = {
        "lane_start_anchor": anchor,
        "lane_state": LANE_STATE,
        "anchor_evidence": ("first commit scripts/update_options.py "
                            "2026-09-25 23:23:04 +0800 round 195 bm-a "
                            "(FIRST LIVE SMOKE last_pass=2026-09-24)"),
        "freeze_months_required": freeze,
        "latest_collected": stats["max_bar_date"],
        "elapsed_months": elapsed,
        "months_remaining": remaining,
        "freeze_gate": "passed" if remaining == 0 else "open",
        "eligibility_date": elig_date,
        "law_ref": "T-67 s2 DEFINITIVE BATCH LAW (>=12 months forward "
                   "history before a new options prereg)",
        "counting_rule": ("elapsed calendar months anchor -> latest "
                          "collected bar; retention-window backfill rows "
                          "predate the lane and never count"),
        "contracts_on_disk": stats["contracts_on_disk"],
        "contracts_with_rows": stats["contracts_with_rows"],
        "rows_total": stats["rows_total"],
        "rows_pre_anchor": stats["rows_pre_anchor"],
        "rows_on_or_after_anchor": stats["rows_on_or_after_anchor"],
        "min_bar_date": stats["min_bar_date"],
        "per_month_rows": dict(sorted(stats["per_month_rows"].items())),
        "unreadable_files": unreadable,
    }
    return out


def _atomic_write(path, payload):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def _lane_status_face():
    """Optional lane freshness disclosure (bm-a-owned lane may lag)."""
    try:
        with open(LANE_STATUS, encoding="utf-8") as f:
            st = json.load(f)
        return {"lane_last_pass_date": st.get("panel", {}).get("last_pass_date"),
                "lane_owner": "bm-a (T-69 chain owner, R31)"}
    except Exception:
        return None


def _meta_face():
    """Optional expiry-face descriptive count."""
    try:
        with open(META_JSON, encoding="utf-8") as f:
            meta = json.load(f)
        exp = meta.get("expiry", {})
        return {u: sorted(exp.get(u, {})) for u in sorted(exp)}
    except Exception:
        return None


# ------------------------------------------------------------- selftest

def _mk_archive(tmp, rows_by_file):
    """rows_by_file: {filename: [date,...]} -> write minimal CSVs."""
    os.makedirs(tmp, exist_ok=True)
    for fn, dates in rows_by_file.items():
        with open(os.path.join(tmp, fn), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume\n")
            for d in dates:
                f.write("%s,1.0,1.1,0.9,1.0,100.0\n" % d)


def selftest():
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    # T1 elapsed-months anniversary math
    check("months 2026-09-24->2026-10-23 = 0",
          _months_between("2026-09-24", "2026-10-23") == 0)
    check("months 2026-09-24->2026-10-24 = 1",
          _months_between("2026-09-24", "2026-10-24") == 1)
    check("months 2026-09-24->2027-09-23 = 11",
          _months_between("2026-09-24", "2027-09-23") == 11)
    check("months 2026-09-24->2027-09-24 = 12",
          _months_between("2026-09-24", "2027-09-24") == 12)
    check("months reversed -> 0", _months_between("2027-01-01", "2026-01-01") == 0)
    check("ym_add 2026-09+12 = 2027-09", _ym_add("2026-09", 12) == "2027-09")
    check("ym_add 2026-11+3 = 2027-02", _ym_add("2026-11", 3) == "2027-02")

    # T2 early archive: gate open, retention rows separated
    with tempfile.TemporaryDirectory() as tmp:
        _mk_archive(tmp, {
            "a.csv": ["2026-03-24", "2026-09-24", "2026-09-30"],
            "b.csv": ["2026-09-25", "2026-10-05"],
        })
        r = count_freeze(tmp)
        check("early elapsed=0", r["elapsed_months"] == 0)
        check("early remaining=12", r["months_remaining"] == 12)
        check("early gate open", r["freeze_gate"] == "open")
        check("early latest=2026-10-05", r["latest_collected"] == "2026-10-05")
        check("retention rows=1", r["rows_pre_anchor"] == 1)
        check("forward rows=4", r["rows_on_or_after_anchor"] == 4)
        check("eligibility=2027-09-24", r["eligibility_date"] == "2027-09-24")
        check("per-month keys", list(r["per_month_rows"]) ==
              ["202603", "202609", "202610"])

    # T3 boundary archive: exactly at eligibility -> passed, zero remaining
    with tempfile.TemporaryDirectory() as tmp:
        _mk_archive(tmp, {"a.csv": ["2026-09-24", "2027-09-24"]})
        r = count_freeze(tmp)
        check("boundary elapsed=12", r["elapsed_months"] == 12)
        check("boundary gate passed", r["freeze_gate"] == "passed")
        check("boundary remaining=0", r["months_remaining"] == 0)

    # T4 one day short of eligibility -> still open (11 months)
    with tempfile.TemporaryDirectory() as tmp:
        _mk_archive(tmp, {"a.csv": ["2026-09-24", "2027-09-23"]})
        r = count_freeze(tmp)
        check("short elapsed=11", r["elapsed_months"] == 11)
        check("short gate open", r["freeze_gate"] == "open")

    # T5 header-only / malformed rows are not bar rows
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "x.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume\n")
            f.write("garbage row without date\n")
            f.write("2026-09-24,1,1,1,1,1\n")
        r = count_freeze(tmp)
        check("malformed skipped rows_total=1", r["rows_total"] == 1)

    # T6 machinery faults raise (missing dir / empty / no bar rows)
    with tempfile.TemporaryDirectory() as tmp:
        for name, fn in (
                ("missing dir raises FileNotFoundError",
                 lambda: count_freeze(os.path.join(tmp, "nope"))),
                ("empty archive raises", lambda: count_freeze(tmp)),
        ):
            try:
                fn()
                check(name, False)
            except (FileNotFoundError, ValueError):
                check(name, True)
        with open(os.path.join(tmp, "h.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume\n")
        try:
            count_freeze(tmp)
            check("no-bar-rows raises ValueError", False)
        except ValueError:
            check("no-bar-rows raises ValueError", True)

    n_pass = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    print("selftest: %d/%d PASS" % (n_pass, len(checks)))
    return 0 if n_pass == len(checks) else 2


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    if len(argv) > 1:
        print("usage: options_iv_freeze_counter.py [selftest]")
        return 2
    try:
        payload = count_freeze(PANEL_DIR)
        payload["expiry_months_face"] = _meta_face()
        payload["lane_status_face"] = _lane_status_face()
        payload["ts"] = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        payload["counter"] = "scripts/options_iv_freeze_counter.py (E2 r822 bm-b)"
        _atomic_write(OUT, payload)
    except Exception as e:
        print("FREEZE-COUNTER FAULT: %s: %s" % (type(e).__name__, e))
        return 2
    flat = {k: payload[k] for k in (
        "lane_start_anchor", "latest_collected", "elapsed_months",
        "months_remaining", "freeze_gate", "eligibility_date",
        "contracts_on_disk", "rows_total", "rows_on_or_after_anchor")}
    print(json.dumps(flat, ensure_ascii=False))
    print("evidence: %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
