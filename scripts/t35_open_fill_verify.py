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
     internal, honest, NOT a breach); zero pendings = zero-case PASS;
     watch re-fires on positions filled an earlier session
     (hold_days >= 2) counted as ``refire_held`` info -- each fill is
     verified on its own fill day, cross-day cost compare of a re-fire
     watch is a phantom breach (r967 fix, live-fire 2026-10-13
     DROUGHT-CE-01 512400).

Evidence is append-only marks jsonl + overwritten state: the join can
only happen AFTER day D's evening engine run, for the day named by the
state cutoff. Never backdated, never fabricated.

Second evidence tier (r1131): when the marks lane missed the session
entirely (its hole is named by scripts/marks_coverage.py), the gate
falls back to the OFFICIAL DAILY BAR OPEN (data/daily/<code>.csv). The
bar open is the exchange's first-trade price -- the same quantity the
marks lane samples from the spot feed -- so it verifies the fill price
against an independent source rather than going blind. What the
fallback cannot see: pendings the engine dropped never reach
open_positions, so ``dropped`` is not observable on this tier
(``drops_observable=false``) and the report says so instead of
printing a zero. Every report carries ``evidence_tier``.

Exit codes: 0 = PASS (or zero-pending honest case), 1 = no-evidence
(marks file missing AND no bar-derived substitute for any filled name),
2 = BREACH (a filled pending deviates beyond REL_TOL from the real
session open -- fill-price correctness red flag, report honestly).

Usage:
    python scripts/t35_open_fill_verify.py             # verify today
    python scripts/t35_open_fill_verify.py --selftest
"""
import csv
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS
from config.lane_io import shared_derive_write_allowed

PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
MARKS_DIR = os.path.join(PAPER_DIR, "marks")
DAILY_DIR = os.path.join(PATHS.data_dir, "daily")
OUT_PATH = os.path.join(PATHS.results_dir, "t35_open_fill_verify.json")
HISTORY_PATH = os.path.join(PATHS.results_dir, "t35_evidence_history.jsonl")
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
            # r967 entry-day discriminator (false-BREACH fix, live-fire
            # 2026-10-13 DROUGHT-CE-01 512400: filled 10-12 at open
            # 1.646 == that day's watch 1.646 exact; 10-13 watch re-fire
            # @1.575 joined against the prior-day cost = 4.5% phantom
            # breach. hold_days >= 2 = filled an earlier session; each
            # fill is verified on its own fill day, cross-day compare
            # of a re-fire watch is meaningless.
            "held_since": {p["symbol"]: p.get("hold_days")
                           for p in st.get("open_positions", [])
                           if p.get("hold_days") is not None},
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


def _daily_open(day_iso: str, symbol: str) -> float | None:
    """Official daily bar open for ``symbol`` on ``day_iso``, else None.
    Tries the bare code file first, then the sh/sz twins (the panel holds
    both spellings). No network, no synthesis: a missing row returns None
    so the caller can count it honestly."""
    for nm in (symbol, f"sh{symbol}", f"sz{symbol}"):
        path = os.path.join(DAILY_DIR, f"{nm}.csv")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if row.get("date") != day_iso:
                        continue
                    try:
                        return float(row.get("open"))
                    except (TypeError, ValueError):
                        return None
        except OSError:
            continue
    return None


def _fallback_watch(states: dict, day_iso: str) -> tuple[dict, dict]:
    """Bar-derived stand-in for the marks ``pending_watch`` face.

    Only positions the states say were filled THIS session (hold_days
    <= 1, known) can be reconstructed without the engine's pending
    export, so the substitute set is exactly the same-day fills. Returns
    ({tid: {sym: bar_open}}, {tid: [sym]} where the second dict names the
    same-day fills whose bar is ABSENT -- a trader that has such a fill
    must never be reported as ``zero_pending``, which would read as a
    clean pass over evidence that simply was not there."""
    out, missing = {}, {}
    for tid, st in states.items():
        held = st.get("held_since") or {}
        got, gone = {}, []
        for sym in st["positions"]:
            hd = held.get(sym)
            if hd is None or hd > 1:
                continue        # filled an earlier session = not this day's fill
            px = _daily_open(day_iso, sym)
            if px is None:
                gone.append(sym)
                continue
            got[sym] = px
        if got:
            out[tid] = got
        if gone:
            missing[tid] = gone
    return out, missing


def verify(states: dict, marks_pw: dict | None,
           no_bar_map: dict | None = None) -> dict:
    """Join -> report dict. Per trader: matched/dropped/breached detail.
    marks_pw None = marks file missing for the day (no-evidence)."""
    per_trader, n_breach, n_matched, n_dropped, n_zero, n_nomarks = {}, 0, 0, 0, 0, 0
    n_refire = n_nobar = 0
    for tid, st in sorted(states.items()):
        pw = (marks_pw or {}).get(tid)
        gone = ((no_bar_map or {}).get(tid) or []) if not pw else []
        if marks_pw is None:
            status = "no_marks"
            n_nomarks += 1
        elif not pw and gone:
            # same-day fills exist but the fallback bar is absent for them:
            # never report this as zero_pending (that would read as a pass).
            status = "no_bar"
            n_nobar += 1
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
                hd = st.get("held_since", {}).get(sym)
                if hd is not None and hd >= 2:
                    detail.append({"symbol": sym, "outcome": "refire_held",
                                   "cost_price": cost,
                                   "session_open": session_open,
                                   "hold_days": hd})
                    n_refire += 1
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
        if status == "no_bar":
            row["detail"] = [{"symbol": s, "outcome": "no_bar"} for s in gone]
        per_trader[tid] = row
    verdict = ("BREACH" if n_breach else
               "NO_EVIDENCE" if (n_nomarks or (n_nobar and not n_matched))
               else "PASS")
    return {"verdict": verdict, "rel_tol": REL_TOL,
            "counters": {"matched": n_matched, "dropped": n_dropped,
                         "breach": n_breach, "zero_pending_traders": n_zero,
                         "no_marks_traders": n_nomarks,
                         "no_bar_traders": n_nobar,
                         "refire_held": n_refire},
            "per_trader": per_trader}


def _append_history(rep: dict) -> None:
    """Keep one line per (day, evidence_tier) in an append-only history.

    The gate's own face is overwritten every round, and a session's
    verification can only be computed while the paper states still mark its
    fills as same-day -- so an unrepeatable verdict must be captured the
    moment it exists, or the fact that a hole WAS still checked is lost.
    Idempotent: a second run for the same (day, tier) rewrites nothing.
    """
    path = HISTORY_PATH
    key = (rep.get("day"), rep.get("evidence_tier"))
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    if (row.get("day"), row.get("evidence_tier")) == key:
                        return
        except OSError:
            return
    row = {"day": rep.get("day"), "evidence_tier": rep.get("evidence_tier"),
           "verdict": rep.get("verdict"), "counters": rep.get("counters"),
           "drops_observable": rep.get("drops_observable"),
           "ts": rep.get("ts")}
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError:
        pass


def run() -> int:
    # D-20260928-03(1) batch-3 slice-2 C-family single-writer guard:
    # results/t35_open_fill_verify.json is a deterministic idempotent
    # re-derive -- non-host honest no-op exit 0, host derives,
    # stale-host takeover per lane_io law.
    if not shared_derive_write_allowed("results/t35_open_fill_verify.json"):
        return 0
    states = _load_states()
    if not states:
        print("open_fill_verify: no paper states (nothing to verify, exit 1)")
        return 1
    days = {st["cutoff"] for st in states.values()}
    day = max(days)
    marks_pw = _pending_watch_for_day(day)
    tier, no_bar_map = "marks", {}
    if marks_pw is None:
        marks_pw, no_bar_map = _fallback_watch(states, day)
        tier = "daily_bar_open" if marks_pw else "none"
        if tier == "none":
            marks_pw = None      # keep the NO_EVIDENCE semantics
    rep = verify(states, marks_pw, no_bar_map)
    rep["day"] = day
    rep["evidence_tier"] = tier
    # On the bar tier the engine's dropped pendings never enter
    # open_positions, so a zero there is "not observable", not "no drops".
    rep["drops_observable"] = tier == "marks"
    if tier == "daily_bar_open":
        rep["evidence_note"] = (
            "marks lane missed this session; fill prices were checked "
            "against the official daily bar open (same exchange first-trade "
            "price marks samples from spot). Dropped-pending counts are NOT "
            "observable on this tier.")
        rep["no_bar_fills"] = {k: sorted(v) for k, v in no_bar_map.items()}
    rep["ts"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    _append_history(rep)
    c = rep["counters"]
    print(f"open_fill_verify day={day}: {rep['verdict']} "
          f"(tier {rep['evidence_tier']}, matched {c['matched']}, "
          f"dropped {c['dropped']}, breach {c['breach']}, "
          f"zero-pending traders {c['zero_pending_traders']})"
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
        if rep["evidence_tier"] == "none":
            print("  no daily-bar substitute either: no same-day fill had a "
                  "reachable bar open, so nothing could be cross-checked")
        # Say whether this is recoverable: scripts/marks_coverage.py classifies
        # every session as captured / permanently missing / still pending, so a
        # reader does not treat a permanent hole as a retry-able miss.
        cov = os.path.join(PATHS.results_dir, "marks_coverage.json")
        try:
            with open(cov, encoding="utf-8") as fh:
                holes = (json.load(fh).get("holes") or [])
            if day in holes:
                print("  permanent hole (capture never happened; "
                      "see results/marks_coverage.json)")
        except (OSError, ValueError):
            pass
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
    # F7: watch re-fire on a position filled an earlier session
    # (hold_days >= 2) -> refire_held info, never a breach (r967 fix)
    st7 = {"T-X": {"cutoff": "2026-09-24", "positions": {"510300": 1.646},
                   "held_since": {"510300": 2}}}
    rep = verify(st7, {"T-X": {"510300": 1.575}})
    ok &= rep["verdict"] == "PASS" and rep["counters"]["refire_held"] == 1
    ok &= rep["counters"]["breach"] == 0 and rep["counters"]["matched"] == 0
    # F8: same-day fill (hold_days == 1) still compared normally
    st8 = {"T-X": {"cutoff": "2026-09-24", "positions": {"510300": 4.1001},
                   "held_since": {"510300": 1}}}
    rep = verify(st8, {"T-X": {"510300": 4.1}})
    ok &= rep["verdict"] == "PASS" and rep["counters"]["matched"] == 1
    ok &= rep["counters"]["refire_held"] == 0
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
    # F9-F11: bar-derived fallback tier (marks lane missed the session)
    tmp2 = tempfile.mkdtemp(prefix="ofv_bar_")
    try:
        import shutil
        with open(os.path.join(tmp2, "510300.csv"), "w", encoding="utf-8") as fh:
            fh.write("date,open,high,low,close,volume,amount\n")
            fh.write("2026-09-23,4.0000,4.1,3.9,4.05,1,1\n")
            fh.write("2026-09-24,4.1000,4.2,4.0,4.15,1,1\n")
        global DAILY_DIR
        orig_d = DAILY_DIR
        DAILY_DIR = tmp2
        st9 = {"T-X": {"cutoff": "2026-09-24", "positions": {"510300": 4.1001},
                       "held_since": {"510300": 1}}}
        fb, miss = _fallback_watch(st9, "2026-09-24")
        ok &= fb == {"T-X": {"510300": 4.1}} and miss == {}
        rep = verify(st9, fb, miss)
        ok &= rep["verdict"] == "PASS" and rep["counters"]["matched"] == 1
        # F10: a same-day fill whose bar row is absent must be no_bar, never
        # zero_pending (a silent clean pass over absent evidence)
        st10 = {"T-X": {"cutoff": "2026-09-24", "positions": {"159999": 1.0},
                        "held_since": {"159999": 1}}}
        fb, miss = _fallback_watch(st10, "2026-09-24")
        ok &= fb == {} and miss == {"T-X": ["159999"]}
        rep = verify(st10, fb, miss)
        ok &= rep["verdict"] == "NO_EVIDENCE"
        ok &= rep["per_trader"]["T-X"]["status"] == "no_bar"
        ok &= rep["counters"]["no_bar_traders"] == 1
        ok &= rep["counters"]["zero_pending_traders"] == 0
        # F11: the fallback tier still catches a wrong fill price
        st11 = {"T-X": {"cutoff": "2026-09-24", "positions": {"510300": 4.151},
                        "held_since": {"510300": 1}}}
        fb, miss = _fallback_watch(st11, "2026-09-24")
        rep = verify(st11, fb, miss)
        ok &= rep["verdict"] == "BREACH" and rep["counters"]["breach"] == 1
        # F12: an earlier-session hold is not a same-day fill -> not in the
        # fallback set at all (no bar lookup, no phantom row)
        st12 = {"T-X": {"cutoff": "2026-09-24", "positions": {"510300": 4.1},
                        "held_since": {"510300": 5}}}
        fb, miss = _fallback_watch(st12, "2026-09-24")
        ok &= fb == {} and miss == {}
        DAILY_DIR = orig_d
    finally:
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)
    # F13: the evidence history keeps one line per (day, tier) -- a verdict
    # that can only be computed while the states still call the fill
    # same-day must not be lost when the face is overwritten next round.
    tmp3 = tempfile.mkdtemp(prefix="ofv_hist_")
    try:
        import shutil
        global HISTORY_PATH
        orig_h = HISTORY_PATH
        HISTORY_PATH = os.path.join(tmp3, "h.jsonl")
        _append_history({"day": "2026-09-24", "evidence_tier": "daily_bar_open",
                         "verdict": "PASS", "counters": {"matched": 1},
                         "drops_observable": False, "ts": "t1"})
        _append_history({"day": "2026-09-24", "evidence_tier": "daily_bar_open",
                         "verdict": "PASS", "counters": {"matched": 1},
                         "drops_observable": False, "ts": "t2"})
        _append_history({"day": "2026-09-25", "evidence_tier": "marks",
                         "verdict": "PASS", "counters": {"matched": 0},
                         "drops_observable": True, "ts": "t3"})
        with open(HISTORY_PATH, encoding="utf-8") as fh:
            rows = [json.loads(x) for x in fh if x.strip()]
        ok &= len(rows) == 2 and rows[0]["ts"] == "t1"
        HISTORY_PATH = orig_h
    finally:
        import shutil
        shutil.rmtree(tmp3, ignore_errors=True)
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
