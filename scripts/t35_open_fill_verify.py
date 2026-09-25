"""T-35 d2-c: 09:30 open-fill verification (CEO order O-20260924-2045 s2.1).

Job: after the evening engine run lands day D's bar (signal T close ->
fill at T+1 open), verify that entries which were queued as pending at
D-1's close actually FILLED AT THE REAL SESSION OPEN of day D. Three
independent sources, joined:

  1. marks-D jsonl (captured 09:25-15:00 of day D by
     scripts/update_intraday_marks.py) -- per-trader ``pending_watch``:
     {symbol: real session open} recorded from the live spot source for
     the pending-entry set exported by the engine (state@D-1).
  2. state@D (results/paper/<TID>_paper.json after the evening run) --
     ``open_positions`` with ``cost_price`` = the engine's fill price.
  3. PASS iff every filled pending's cost_price matches the captured
     session open within REL_TOL; pendings absent from open_positions
     counted as ``dropped`` (guard drop / ADV cap / cash -- engine-
     internal, honest, NOT a breach); zero pendings = zero-case PASS.

Evidence is append-only marks jsonl + overwritten state: the join can
only happen AFTER day D's evening engine run, for the day named by the
state cutoff. Never backdated, never fabricated.

Exit codes: 0 = PASS (or zero-pending honest case), 1 = no-evidence
(marks file for the cutoff day missing -- e.g. marks lane down), 2 =
BREACH (a filled pending deviates beyond REL_TOL from the real session
open -- fill-price correctness red flag, report honestly).

Usage:
    python scripts/t35_open_fill_verify.py             # verify today
    python scripts/t35_open_fill_verify.py --selftest
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
MARKS_DIR = os.path.join(PAPER_DIR, "marks")
OUT_PATH = os.path.join(PATHS.results_dir, "t35_open_fill_verify.json")
# Frozen tolerance (engineering gate, not a science threshold): quote-side
# rounding is <= 1e-3 relative for the cheapest ETFs; any wrong-price
# fill (close/vwap instead of open) deviates by orders of magnitude more.
REL_TOL = 2e-3


def _load_states() -> dict:
    """Paper states -> {tid: {"cutoff": D, "positions": {sym: cost}}}.
    Legacy states without open_positions are skipped (nothing to join)."""
    out = {}
    if not os.path.isdir(PAPER_DIR):
        return out
    for fn in sorted(os.listdir(PAPER_DIR)):
        if not fn.endswith("_paper.json"):
            continue
        with open(os.path.join(PAPER_DIR, fn), encoding="utf-8") as fh:
            st = json.load(fh)
        tid = st.get("trader")
        cutoff = st.get("cutoff")
        if not tid or not cutoff:
            continue
        out[tid] = {
            "cutoff": cutoff,
            "positions": {p["symbol"]: p["cost_price"]
                          for p in st.get("open_positions", [])},
        }
    return out


def _pending_watch_for_day(day_iso: str) -> dict:
    """Earliest-tick pending_watch per trader from marks-<day>.jsonl.
    Returns {tid: {sym: session_open}}; {} when the file has no
    pending_watch faces (zero-pending or legacy ticks)."""
    day = day_iso.replace("-", "")
    path = os.path.join(MARKS_DIR, f"marks-{day}.jsonl")
    if not os.path.exists(path):
        return None
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("kind") not in ("intraday", "settle"):
                continue        # forced ticks never count as trading evidence
            for tid, tr in (rec.get("traders") or {}).items():
                pw = tr.get("pending_watch")
                if not pw:
                    continue
                if tid not in out:     # earliest tick wins (first capture)
                    out[tid] = dict(pw)
    return out


def verify(states: dict, marks_pw: dict | None) -> dict:
    """Join -> report dict. Per trader: matched/dropped/breached detail.
    marks_pw None = marks file missing for the day (no-evidence)."""
    per_trader, n_breach, n_matched, n_dropped, n_zero, n_nomarks = {}, 0, 0, 0, 0, 0
    for tid, st in sorted(states.items()):
        pw = (marks_pw or {}).get(tid)
        if marks_pw is None:
            status = "no_marks"
            n_nomarks += 1
        elif not pw:
            status = "zero_pending"
            n_zero += 1
        else:
            detail, breach = [], 0
            for sym, session_open in sorted(pw.items()):
                cost = st["positions"].get(sym)
                if cost is None:
                    detail.append({"symbol": sym, "outcome": "dropped"})
                    n_dropped += 1
                    continue
                rel = abs(cost - session_open) / session_open
                row = {"symbol": sym, "outcome": "filled",
                       "cost_price": cost, "session_open": session_open,
                       "rel_diff": round(rel, 6)}
                if rel > REL_TOL:
                    row["outcome"] = "BREACH"
                    breach += 1
                    n_breach += 1
                else:
                    n_matched += 1
                detail.append(row)
            status = "breach" if breach else "verified_pass"
        row = {"cutoff": st["cutoff"], "status": status, "detail": []}
        if status in ("verified_pass", "breach"):
            row["detail"] = detail
        per_trader[tid] = row
    verdict = ("BREACH" if n_breach else
               "NO_EVIDENCE" if n_nomarks else "PASS")
    return {"verdict": verdict, "rel_tol": REL_TOL,
            "counters": {"matched": n_matched, "dropped": n_dropped,
                         "breach": n_breach, "zero_pending_traders": n_zero,
                         "no_marks_traders": n_nomarks},
            "per_trader": per_trader}


def run() -> int:
    states = _load_states()
    if not states:
        print("open_fill_verify: no paper states (nothing to verify, exit 1)")
        return 1
    days = {st["cutoff"] for st in states.values()}
    day = max(days)
    marks_pw = _pending_watch_for_day(day)
    rep = verify(states, marks_pw)
    rep["day"] = day
    rep["ts"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    c = rep["counters"]
    print(f"open_fill_verify day={day}: {rep['verdict']} "
          f"(matched {c['matched']}, dropped {c['dropped']}, "
          f"breach {c['breach']}, zero-pending traders {c['zero_pending_traders']})"
          f" -> {OUT_PATH}")
    if rep["verdict"] == "BREACH":
        for tid, tr in rep["per_trader"].items():
            for r in tr["detail"]:
                if r.get("outcome") == "BREACH":
                    print(f"  BREACH {tid} {r['symbol']}: cost "
                          f"{r['cost_price']} vs session_open "
                          f"{r['session_open']} (rel {r['rel_diff']})")
        return 2
    if rep["verdict"] == "NO_EVIDENCE":
        print(f"  marks file for {day} missing -- marks lane evidence gap")
        return 1
    return 0


def _selftest() -> bool:
    import tempfile
    ok = True

    def states_fix(cost_map, cutoff="2026-09-24"):
        return {"T-X": {"cutoff": cutoff,
                        "positions": dict(cost_map)}}

    # F1: full PASS arc -- pending filled at the session open
    st = states_fix({"510300": 4.1001})
    pw = {"T-X": {"510300": 4.1}}
    rep = verify(st, pw)
    ok &= rep["verdict"] == "PASS"
    ok &= rep["counters"]["matched"] == 1 and rep["per_trader"]["T-X"]["status"] == "verified_pass"
    # F2: breach -- cost deviates 1% from the real open
    st = states_fix({"510300": 4.141})
    rep = verify(st, pw)
    ok &= rep["verdict"] == "BREACH" and rep["counters"]["breach"] == 1
    # F3: dropped pending (guard/ADV drop) = honest, PASS
    st = states_fix({})
    rep = verify(st, pw)
    ok &= rep["verdict"] == "PASS" and rep["counters"]["dropped"] == 1
    # F4: marks missing for the day -> NO_EVIDENCE
    rep = verify(states_fix({"510300": 4.1}), None)
    ok &= rep["verdict"] == "NO_EVIDENCE"
    # F5: zero-pending day (marks exist, no pending_watch) -> PASS zero-case
    rep = verify(states_fix({"510300": 4.1}), {})
    ok &= rep["verdict"] == "PASS" and rep["per_trader"]["T-X"]["status"] == "zero_pending"
    # F6: earliest-tick precedence in marks parsing (temp file)
    tmp = tempfile.mkdtemp(prefix="ofv_st_")
    try:
        mp = os.path.join(tmp, "marks-20260924.jsonl")
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"kind": "intraday", "ts": "2026-09-24T10:00:00",
                                 "traders": {"T-X": {"pending_watch": {"510300": 4.1}}}}) + "\n")
            fh.write(json.dumps({"kind": "intraday", "ts": "2026-09-24T11:00:00",
                                 "traders": {"T-X": {"pending_watch": {"510300": 4.9}}}}) + "\n")
            fh.write(json.dumps({"kind": "forced", "ts": "2026-09-24T12:00:00",
                                 "traders": {"T-X": {"pending_watch": {"999999": 1.0}}}}) + "\n")
        global MARKS_DIR
        orig = MARKS_DIR
        MARKS_DIR = tmp
        got = _pending_watch_for_day("2026-09-24")
        MARKS_DIR = orig
        ok &= got == {"T-X": {"510300": 4.1}}   # earliest tick; forced tick ignored
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = _selftest()
        print("t35_open_fill_verify selftest:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())
