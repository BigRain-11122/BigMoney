"""T-35 d2: intraday paper-plane marking lane (CEO order O-20260924-2045 s2).

Job: during real trading hours (workdays 09:30-15:00 Asia/Shanghai) fetch
live ETF spot quotes for the symbols HELD by the 6 registered paper
traders and append a timestamped mark snapshot; at 15:00+ (first tick)
append the settle face for the day. Marks are append-only evidence
(results/paper/marks/marks-YYYYMMDD.jsonl) -- never backdated, never
rewritten; the authoritative daily ledger stays the closed-bar paper
state (live/paper.py), this lane adds the intraday timestamped face
CEO O-2045 asked for.

Source discipline (probe-first DONE, results/shortline/
t35_intraday_spot_probe.json 2026-09-24): primary fund_etf_category_sina
(sina family -- reliable lineage per D-20260924-07), fallback
fund_etf_spot_ths; push2 family (fund_etf_spot_em) is day-blocked and
NEVER tried first. Conn failures -> 3 attempts, then exit 2 honest
(no partial write, no silent pop).

D-20260930-27 P0 fix (zero-price marking, 2026-09-30): a held symbol
whose live quote row exists but carries last<=0 (e.g. 513100 QDII face
glitch 09-30 09:35) used to write mark=0.00/market_value=null and was
SILENTLY wiped out of equity_mark. Forbidden: fallback chain
live>0 -> state last_close -> local daily panel close; only a symbol
with no price on ANY face is "unpriced" (explicit flag + equity
isolation + per-trader unpriced_symbols disclosure). Machine check
before write: a held symbol with a local daily close on disk carrying
mark<=0/None = mechanism violation -> exit 2, tick NOT written.

Gates (script-side, safe under any scheduler cadence):
  - non-workday OR before 09:30 OR after 15:10 -> legal no-op exit 0
  - 09:30 <= now < 15:00 -> intraday tick
  - 15:00 <= now <= 15:10 -> settle face (once per day; later ticks no-op)
  - --force bypasses the clock gate for pipeline validation ONLY (the
    run is stamped kind="forced" and never counts as trading evidence)

Stale-takeover exception (r1101 bm-a): this lane's scheduler lives on one
host, so that host going silent silently rots the ONLY intraday evidence
face (marks 2026-10-22/23 never existed; t35_open_fill_verify then exits 1
on a day that can never be reconstructed). A non-owner host may therefore
capture only with an explicit --takeover flag AND an owner heartbeat
>= TAKEOVER_STALE_MIN stale -- the same pure decision the ETF panel uses
(imported, not re-implemented), and the takeover is stamped into the marks
line itself so every mark carries its own provenance.

Usage:
    python scripts/update_intraday_marks.py            # gated run
    python scripts/update_intraday_marks.py --takeover # non-owner, stale owner only
    python scripts/update_intraday_marks.py --force    # validation run
    python scripts/update_intraday_marks.py --coverage # lane gap report
    python scripts/update_intraday_marks.py --selftest
Exit codes: 0 = ok/no-op, 2 = source/mechanism failure (honest), 3 = coverage gap.
"""
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update_etf_daily import (TAKEOVER_STALE_MIN, _owner_stale_min,
                              takeover_decision)          # noqa: E402

PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
MARKS_DIR = os.path.join(PAPER_DIR, "marks")
OPEN_T = dt.time(9, 30)
SETTLE_T = dt.time(15, 0)
CLOSE_GRACE_T = dt.time(15, 10)
ATTEMPTS = 3
BACKOFF_S = (5, 10)
SOURCE_ORDER = ("fund_etf_category_sina", "fund_etf_spot_ths")
LANE_OWNER = "bm-b"                 # host that carries the marks scheduler


def _now() -> dt.datetime:
    return dt.datetime.now()


def _machine_id(root: str | None = None) -> str:
    """This host's machine_id (fleet/machine.json), '' when unreadable."""
    p = os.path.join(root or os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "fleet", "machine.json")
    try:
        with open(p, encoding="utf-8-sig") as fh:
            return str(json.load(fh).get("machine_id") or "")
    except (OSError, ValueError):
        return ""


def _gate(now: dt.datetime) -> str:
    """intraday | settle | noop (workday + clock gate)."""
    if now.weekday() >= 5:                     # Sat/Sun
        return "noop"
    t = now.time()
    if OPEN_T <= t < SETTLE_T:
        return "intraday"
    if SETTLE_T <= t <= CLOSE_GRACE_T:
        return "settle"
    return "noop"


def _norm_code(raw: str) -> str:
    """'sz159998'/'sh510300' -> '159998'/'510300' (daily-CSV convention)."""
    s = str(raw).strip().lower()
    for p in ("sz", "sh", "of", "bj"):
        if s.startswith(p):
            return s[len(p):]
    return s


DAILY_DIR = os.path.join(PATHS.data_dir, "daily")


def _local_last_close(sym: str, daily_dir: str | None = None) -> float | None:
    """Last valid close from the local daily panel (second source face,
    D-20260930-27). Reads data/daily/<code>.csv bottom-up; returns None
    when the file is missing or holds no positive close."""
    path = os.path.join(daily_dir or DAILY_DIR, f"{sym}.csv")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        for ln in reversed(lines):
            cells = ln.split(",")
            if len(cells) < 5:
                continue
            try:
                c = float(cells[4])
            except ValueError:
                continue
            if c > 0:
                return c
        return None
    except OSError:
        return None


def _fetch_spot() -> tuple[dict, dict]:
    """Try sources in frozen order; return (records, meta) or raise."""
    import akshare as ak
    last_err = None
    for name in SOURCE_ORDER:
        for i in range(ATTEMPTS):
            t0 = time.time()
            try:
                if name == "fund_etf_category_sina":
                    df = ak.fund_etf_category_sina("ETF基金")
                    # cols (GBK-named): 代码/名称/最新价/.../今开/昨收...
                    recs = {}
                    cols = list(df.columns)
                    code_c = "代码" if "代码" in cols else cols[0]
                    for c in ("最新价", "今开", "昨收", "最高", "最低"):
                        if c not in cols:
                            raise ValueError(f"sina face missing col {c!r}")
                    for _, r in df.iterrows():
                        code = _norm_code(r[code_c])
                        try:
                            recs[code] = {
                                "last": float(r["最新价"]),
                                "open": float(r["今开"]),
                                "prev_close": float(r["昨收"]),
                                "high": float(r["最高"]),
                                "low": float(r["最低"]),
                            }
                        except (TypeError, ValueError):
                            continue        # suspended/empty quote rows
                    return recs, {"source": name, "rows": len(recs),
                                  "latency_s": round(time.time() - t0, 2),
                                  "attempt": i}
                elif name == "fund_etf_spot_ths":
                    df = ak.fund_etf_spot_ths()
                    cols = list(df.columns)
                    code_c = next((c for c in cols if "代码" in c), cols[0])

                    def _find(*keys):
                        for c in cols:
                            if any(k in c for k in keys):
                                return c
                        return None
                    lc = _find("最新", "现价") or cols[2]
                    oc = _find("今开", "开盘")
                    pc = _find("昨收", "昨结")
                    recs = {}
                    for _, r in df.iterrows():
                        code = _norm_code(r[code_c])
                        try:
                            recs[code] = {
                                "last": float(r[lc]),
                                "open": float(r[oc]) if oc else None,
                                "prev_close": float(r[pc]) if pc else None,
                                "high": None, "low": None,
                            }
                        except (TypeError, ValueError):
                            continue
                    return recs, {"source": name, "rows": len(recs),
                                  "latency_s": round(time.time() - t0, 2),
                                  "attempt": i}
            except Exception as exc:
                last_err = f"{name}#{i}: {type(exc).__name__}: {exc}"[:200]
                if i < ATTEMPTS - 1:
                    time.sleep(BACKOFF_S[min(i, len(BACKOFF_S) - 1)])
    raise RuntimeError(f"all spot sources failed: {last_err}")


def _load_states() -> dict:
    """Registered paper states -> per-trader positions + capital."""
    out = {}
    if not os.path.isdir(PAPER_DIR):
        return out
    for fn in sorted(os.listdir(PAPER_DIR)):
        if not fn.endswith("_paper.json"):
            continue                        # PROSPECT states live elsewhere
        p = os.path.join(PAPER_DIR, fn)
        with open(p, encoding="utf-8") as fh:
            st = json.load(fh)
        tid = st.get("trader")
        if not tid:
            continue
        out[tid] = {
            "positions": st.get("open_positions", []),
            "capital": st.get("capital", {}),
            "cutoff": st.get("cutoff"),
            # T-35 d2-c (O-2045 s2.1): entries queued at the final close
            # (fill at THIS session's 09:30 open) -- captured so the tick
            # records the real session open for symbols not yet in state
            # positions (the fill only lands in state after the evening
            # engine run). Missing key on legacy states = empty list.
            "pending": st.get("pending_entries", []),
        }
    return out


def _settle_done(marks_path: str) -> bool:
    if not os.path.exists(marks_path):
        return False
    with open(marks_path, encoding="utf-8") as fh:
        for line in fh:
            try:
                if json.loads(line).get("kind") == "settle":
                    return True
            except ValueError:
                continue
    return False


def _compose(states: dict, quotes: dict, now: dt.datetime, kind: str,
             meta: dict, daily_dir: str | None = None) -> dict:
    traders_out = {}
    for tid, st in states.items():
        cap = st["capital"]
        cash = float((cap or {}).get("cash_cny") or 0.0)
        poss, mv_total, unpriced = [], 0.0, []
        for p in st["positions"]:
            sym = p["symbol"]
            q = quotes.get(sym)
            # D-20260930-27 P0: a zero/missing live price must NEVER
            # silently zero the position out of equity. Fallback chain:
            # valid live quote -> state last_close -> local daily panel
            # close; only a symbol priced on NO face is unpriced
            # (explicit flag + isolation + disclosure, never a fake 0).
            live = float((q or {}).get("last") or 0.0)
            if live > 0:
                mark, src = live, "live"
            elif (p.get("last_close") or 0) > 0:
                mark, src = float(p["last_close"]), "last_close"
            else:
                lc = _local_last_close(sym, daily_dir)
                if lc:
                    mark, src = lc, "local_daily"
                else:
                    mark, src = None, "unpriced"
            mv = round(p["quantity"] * mark, 2) if mark else None
            if mv:
                mv_total += mv
            else:
                unpriced.append(sym)
            poss.append({
                "symbol": sym, "quantity": p["quantity"],
                "cost_price": p["cost_price"],
                "session_open": (q or {}).get("open"),
                "mark": mark,
                "mark_source": src,
                "market_value_cny": mv,
                "unrealized_pnl_cny":
                    round((mark - p["cost_price"]) * p["quantity"], 2)
                    if mark else None,
                "marked": live > 0,
            })
        traders_out[tid] = {
            "cash_cny": round(cash, 2),
            "positions": poss,
            "equity_mark_cny": round(cash + mv_total, 2),
            "state_cutoff": st["cutoff"],
        }
        # D-20260930-27: unpriced positions are isolated from equity AND
        # disclosed -- an equity face that silently excludes a held
        # position's market value is forbidden.
        if unpriced:
            traders_out[tid]["unpriced_symbols"] = unpriced
        # T-35 d2-c (O-2045 s2.1): pending entries queued at the prior
        # close fill at THIS session's 09:30 open; the position is not in
        # state yet, so record the real session open per pending symbol
        # (open-fill verification evidence). ADDITIVE per-trader key,
        # emitted only when a pending symbol has a live open quote.
        pw = {}
        for pe in st.get("pending", []):
            sym = pe.get("symbol")
            q = quotes.get(sym)
            if q and q.get("open") is not None:
                pw[sym] = q["open"]
        if pw:
            traders_out[tid]["pending_watch"] = pw
    return {"ts": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "kind": kind, "source": meta["source"],
            "source_rows": meta["rows"], "traders": traders_out}


def _check_no_silent_zero(line: dict, daily_dir: str | None = None) -> list:
    """D-20260930-27 machine check: a held symbol with a local daily
    close on disk must never carry mark<=0/None in a written tick.
    Returns the violation list (empty = clean)."""
    viol = []
    for tid, t in (line.get("traders") or {}).items():
        for pos in t.get("positions") or []:
            m = pos.get("mark")
            if m is None or float(m) <= 0:
                if _local_last_close(str(pos.get("symbol", "")), daily_dir):
                    viol.append(f"{tid}:{pos.get('symbol')}")
    return viol


def _tick_redundant(cur: dict, prev: dict, bp: float = 5.0) -> tuple[bool, str]:
    """D-20260930-27 Q4 marks slimming (r480): an intraday tick is
    REDUNDANT when, vs the last WRITTEN tick: no trader's equity moved
    >=bp AND no state change (cash / symbol / quantity / cost_price /
    pending_watch) AND nothing is unpriced. First tick of the day and the
    settle face are never suppressed (callers enforce). Audit Q4 measured
    93.9% of ticks redundant (62/66) on the 09-28..09-30 files; the
    suppressed tick adds audit noise, not evidence. Returns
    (redundant, reason)."""
    tr_cur, tr_prev = cur.get("traders") or {}, prev.get("traders") or {}
    if set(tr_cur) != set(tr_prev):
        return False, "trader-set change"
    for tid, t in tr_cur.items():
        p = tr_prev[tid]
        if (t.get("unpriced_symbols") or p.get("unpriced_symbols")):
            return False, f"{tid}: unpriced face -- keep evidence"
        pw_c, pw_p = t.get("pending_watch") or {}, p.get("pending_watch") or {}
        if set(pw_c) != set(pw_p) or any(
                pw_c[k] != pw_p[k] for k in pw_c):
            return False, f"{tid}: pending_watch change"
        st_c = ";".join(f"{x.get('symbol')}|{x.get('quantity')}|"
                        f"{x.get('cost_price')}"
                        for x in (t.get("positions") or []))
        st_p = ";".join(f"{x.get('symbol')}|{x.get('quantity')}|"
                        f"{x.get('cost_price')}"
                        for x in (p.get("positions") or []))
        if st_c != st_p or t.get("cash_cny") != p.get("cash_cny"):
            return False, f"{tid}: state change"
        e_c, e_p = t.get("equity_mark_cny"), p.get("equity_mark_cny")
        if not e_c or not e_p:
            return False, f"{tid}: unpriced equity anchor"
        if abs(e_c - e_p) / e_p * 1e4 >= bp:
            return False, (f"{tid}: move "
                           f"{abs(e_c - e_p) / e_p * 1e4:.1f}bp >= {bp}bp")
    return True, f"all traders <{bp}bp, no state change"


def _last_written_tick(marks_path: str) -> dict | None:
    """Last line of today's marks file (suppressed ticks never land, so
    this is the retention base). None when the day has no ticks yet."""
    if not os.path.exists(marks_path):
        return None
    last = None
    with open(marks_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    last = json.loads(line)
                except ValueError:
                    continue
    return last


def run(force: bool = False, takeover_flag: bool = False) -> int:
    now = _now()
    kind = "forced" if force else _gate(now)
    if force:
        kind = "forced"
    elif kind == "noop":
        print(f"intraday_marks: no-op (outside trading window, {now:%H:%M})")
        return 0
    takeover = None
    if not force and _machine_id() != LANE_OWNER:
        ok, why = takeover_decision(takeover_flag, _owner_stale_min(LANE_OWNER))
        if not ok:
            print(f"intraday_marks: no-op: marks lane owned by {LANE_OWNER}, "
                  f"not this machine ({_machine_id() or '?'}); takeover "
                  f"refused: {why}")
            return 0
        takeover = {"owner": LANE_OWNER, "by": _machine_id(), "reason": why,
                    "ts": now.isoformat(timespec="seconds")}
        print(f"TAKEOVER: declared stale takeover of {LANE_OWNER} marks lane "
              f"by {_machine_id()} -- {why}")
    if kind == "settle":
        marks_path = os.path.join(
            MARKS_DIR, f"marks-{now:%Y%m%d}.jsonl")
        if _settle_done(marks_path):
            print("intraday_marks: settle already recorded today (no-op)")
            return 0
    states = _load_states()
    if not states:
        print("intraday_marks: no paper states with positions (no-op)")
        return 0
    try:
        quotes, meta = _fetch_spot()
    except Exception as exc:
        print(f"intraday_marks: SOURCE FAILURE -- {exc}")
        return 2
    os.makedirs(MARKS_DIR, exist_ok=True)
    marks_path = os.path.join(MARKS_DIR, f"marks-{now:%Y%m%d}.jsonl")
    line = _compose(states, quotes, now, kind, meta)
    if takeover:
        line["takeover"] = takeover
    viol = _check_no_silent_zero(line)
    if viol:
        print(f"intraday_marks: MACHINE-CHECK VIOLATION (local daily quote "
              f"on disk but zero/None mark, D-20260930-27): {viol} -- "
              "tick NOT written")
        return 2
    if kind == "intraday" and not force:
        # D-20260930-27 Q4 slimming (r480): redundant intraday ticks are
        # audit noise (93.9% measured) -- first-tick/settle/state-change/
        # >=5bp-move faces always land, suppressed ones never do.
        prev = _last_written_tick(marks_path)
        if prev is not None:
            redundant, why = _tick_redundant(line, prev)
            if redundant:
                print(f"intraday_marks: tick suppressed (Q4 slimming, "
                      f"{why}) -- no evidence value lost")
                return 0
    with open(marks_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    n_marked = sum(1 for t in states.values() for p in t["positions"])
    print(f"intraday_marks: {kind} tick appended ({n_marked} positions, "
          f"source {meta['source']}, {meta['latency_s']}s) -> {marks_path}")
    return 0


def coverage_report(cal_dates, marks_dir, days, today):
    """Which of the last ``days`` trading days have a marks file on disk?

    Purpose (r1099 bm-a): a dead marks lane used to be discovered only
    downstream, when t35_open_fill_verify exits 1 on the day it needs the
    evidence -- by then the day is unrecoverable (marks are append-only and
    intraday-only). This turns that late surprise into one line at the lane
    itself: every trading day without a file is named up front.
    """
    exp = [d for d in sorted(cal_dates) if d <= today][-int(days):]
    present, missing = [], []
    for d in exp:
        path = os.path.join(marks_dir, f"marks-{d.replace('-', '')}.jsonl")
        (present if os.path.exists(path) else missing).append(d)
    return {"expected": exp, "present": present, "missing": missing,
            "last_present": present[-1] if present else None,
            "coverage_share": round(len(present) / len(exp), 4) if exp else None}


def _calendar_dates(daily_dir=None):
    """Union of dated rows across the local daily panel (the repo's
    established ETF trading-calendar main source; sh510300.csv first)."""
    daily_dir = daily_dir or os.path.join(PATHS.data_dir, "daily")
    cands = [os.path.join(daily_dir, "sh510300.csv"),
             os.path.join(daily_dir, "510300.csv")]
    try:
        cands += sorted(os.path.join(daily_dir, n)
                        for n in os.listdir(daily_dir) if n.endswith(".csv"))
    except OSError:
        pass
    for path in cands:
        try:
            dates = []
            with open(path, encoding="utf-8-sig") as fh:
                next(fh, None)
                for line in fh:
                    head = line.split(",", 1)[0].strip().strip('"')
                    if len(head) == 10 and head[4] == "-" and head[7] == "-":
                        dates.append(head)
            if dates:
                return sorted(set(dates))
        except Exception:                                    # noqa: BLE001
            continue
    return []


def _selftest() -> bool:
    ok = True
    # S1: clock gate
    ok &= _gate(dt.datetime(2026, 9, 24, 10, 0)) == "intraday"
    ok &= _gate(dt.datetime(2026, 9, 24, 9, 29)) == "noop"
    ok &= _gate(dt.datetime(2026, 9, 24, 15, 5)) == "settle"
    ok &= _gate(dt.datetime(2026, 9, 24, 15, 11)) == "noop"
    ok &= _gate(dt.datetime(2026, 9, 26, 10, 0)) == "noop"    # Saturday
    # S2: code normalization
    ok &= _norm_code("sz159998") == "159998" and _norm_code("sh510300") == "510300"
    ok &= _norm_code("159998") == "159998"
    # S3: mark math + composition (fixture)
    states = {"T-X": {"positions": [
                  {"symbol": "510300", "quantity": 1000.0,
                   "cost_price": 4.0, "hold_days": 3}],
              "capital": {"cash_cny": 960000.0}, "cutoff": "2026-09-23"}}
    quotes = {"510300": {"last": 4.2, "open": 4.1, "prev_close": 4.15,
                         "high": 4.3, "low": 4.05}}
    line = _compose(states, quotes, dt.datetime(2026, 9, 24, 10, 0),
                    "intraday", {"source": "x", "rows": 1})
    tx = line["traders"]["T-X"]
    ok &= tx["positions"][0]["market_value_cny"] == 4200.0
    ok &= tx["positions"][0]["unrealized_pnl_cny"] == 200.0
    ok &= tx["equity_mark_cny"] == 964200.0
    ok &= tx["positions"][0]["session_open"] == 4.1
    # S4: symbol priced on NO face -> unpriced isolation + disclosure
    # (never fabricated; D-20260930-27 forbids silent equity wipe)
    states2 = {"T-X": {"positions": [
                   {"symbol": "999999", "quantity": 10.0,
                    "cost_price": 1.0, "hold_days": 1}],
               "capital": {"cash_cny": 0.0}, "cutoff": "2026-09-23"}}
    line2 = _compose(states2, quotes, dt.datetime(2026, 9, 24, 10, 0),
                     "intraday", {"source": "x", "rows": 1})
    ok &= line2["traders"]["T-X"]["positions"][0]["marked"] is False
    ok &= line2["traders"]["T-X"]["equity_mark_cny"] == 0.0
    ok &= line2["traders"]["T-X"].get("unpriced_symbols") == ["999999"]
    # S7 (D-20260930-27 P0 regression): live row present but last==0
    # (the 09-30 09:35 513100 face) must fall back to state last_close,
    # never write mark=0 and never wipe the position out of equity.
    states4 = {"T-X": {"positions": [
                   {"symbol": "513100", "quantity": 1000.0,
                    "cost_price": 2.3, "last_close": 2.324, "hold_days": 1}],
               "capital": {"cash_cny": 100.0}, "cutoff": "2026-09-30"}}
    q0 = {"513100": {"last": 0.0, "open": 2.3, "prev_close": 2.324,
                     "high": 0.0, "low": 0.0}}
    line4 = _compose(states4, q0, dt.datetime(2026, 9, 30, 10, 0),
                     "intraday", {"source": "x", "rows": 1})
    p4 = line4["traders"]["T-X"]["positions"][0]
    ok &= p4["mark"] == 2.324 and p4["mark_source"] == "last_close"
    ok &= p4["marked"] is False
    ok &= p4["market_value_cny"] == 2324.0
    ok &= line4["traders"]["T-X"]["equity_mark_cny"] == 2424.0
    ok &= "unpriced_symbols" not in line4["traders"]["T-X"]
    # S8: no live quote, no state last_close -> local daily panel fallback
    import tempfile, shutil
    tmpd = tempfile.mkdtemp(prefix="marks_p0_")
    try:
        with open(os.path.join(tmpd, "777777.csv"), "w",
                  encoding="utf-8") as fh:
            fh.write("date,open,high,low,close,vol,amt\n")
            fh.write("2026-09-29,2.2,2.3,2.1,2.25,100,200\n")
        ok &= _local_last_close("777777", daily_dir=tmpd) == 2.25
        ok &= _local_last_close("000000", daily_dir=tmpd) is None
        states5 = {"T-X": {"positions": [
                       {"symbol": "777777", "quantity": 100.0,
                        "cost_price": 2.0, "hold_days": 1}],
                   "capital": {"cash_cny": 0.0}, "cutoff": "2026-09-30"}}
        line5 = _compose(states5, {}, dt.datetime(2026, 9, 30, 10, 0),
                         "intraday", {"source": "x", "rows": 1},
                         daily_dir=tmpd)
        p5 = line5["traders"]["T-X"]["positions"][0]
        ok &= p5["mark"] == 2.25 and p5["mark_source"] == "local_daily"
        ok &= p5["market_value_cny"] == 225.0
        # S9 (machine check): held symbol with a local daily close but a
        # zero/None mark = violation (tick must not be written).
        bad = {"traders": {"T-X": {"positions": [
            {"symbol": "777777", "mark": 0.0, "market_value_cny": None}]}}}
        ok &= _check_no_silent_zero(bad, daily_dir=tmpd) == ["T-X:777777"]
        ok &= _check_no_silent_zero(line5, daily_dir=tmpd) == []
        ok &= _check_no_silent_zero(line4, daily_dir=tmpd) == []
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    # S6 (T-35 d2-c): pending_watch -- pending-entry symbols capture the
    # session open even though the position is not in state yet; symbols
    # without a live open quote are omitted (never fabricated); no
    # pendings -> key absent (legacy byte-stability).
    states3 = {"T-X": {"positions": [],
               "capital": {"cash_cny": 1000000.0}, "cutoff": "2026-09-23",
               "pending": [{"symbol": "510300", "queued_date": "2026-09-23"},
                           {"symbol": "123456", "queued_date": "2026-09-23"}]}}
    line3 = _compose(states3, quotes, dt.datetime(2026, 9, 24, 10, 0),
                     "intraday", {"source": "x", "rows": 1})
    tx3 = line3["traders"]["T-X"]
    ok &= tx3.get("pending_watch") == {"510300": 4.1}
    line3b = _compose(states2, quotes, dt.datetime(2026, 9, 24, 10, 0),
                      "intraday", {"source": "x", "rows": 1})
    ok &= "pending_watch" not in line3b["traders"]["T-X"]
    # S5: settle-once idempotency on temp file
    import tempfile
    tmp = tempfile.mkdtemp(prefix="marks_st_")
    try:
        mp = os.path.join(tmp, "marks-20260924.jsonl")
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"kind": "settle"}) + "\n")
        ok &= _settle_done(mp) is True
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"kind": "intraday"}) + "\n")
        ok &= _settle_done(mp) is False
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    # S10-S13 (D-20260930-27 Q4 slimming, r480): redundancy gate -- a
    # tick is suppressible only when ALL traders moved <5bp with no
    # state/pending/unpriced change; every evidence face keeps the tick.
    base_tr = {"cash_cny": 1000000.0,
               "positions": [{"symbol": "510300", "quantity": 1000.0,
                               "cost_price": 4.0}],
               "equity_mark_cny": 1000000.0}
    def _mk(eq):
        return {"traders": {"T-X": {
            "cash_cny": base_tr["cash_cny"],
            "positions": [dict(p) for p in base_tr["positions"]],
            "equity_mark_cny": eq}}}
    prev = _mk(1000000.0)
    ok &= _tick_redundant(_mk(1000000.0), prev)[0] is True      # S10 flat
    ok &= _tick_redundant(_mk(1000002.0), prev)[0] is True      # S10 0.02bp
    ok &= _tick_redundant(_mk(1000600.0), prev)[0] is False     # S10 6bp
    cur_st = _mk(1000000.0)
    cur_st["traders"]["T-X"]["positions"][0]["quantity"] = 900.0
    ok &= _tick_redundant(cur_st, prev)[0] is False             # S11 state
    cur_pw = _mk(1000000.0)
    cur_pw["traders"]["T-X"]["pending_watch"] = {"510300": 4.1}
    ok &= _tick_redundant(cur_pw, prev)[0] is False             # S12 pending
    cur_un = _mk(1000000.0)
    cur_un["traders"]["T-X"]["unpriced_symbols"] = ["999999"]
    ok &= _tick_redundant(cur_un, prev)[0] is False             # S13 unpriced
    ok &= _tick_redundant({"traders": {"T-Y": dict(base_tr)}},
                          prev)[0] is False                      # trader-set
    ok &= _tick_redundant(_mk(None), _mk(1000000.0))[0] is False  # anchor
    # S14: coverage report names every trading day without a marks file
    import tempfile
    tmp = tempfile.mkdtemp(prefix="marks_cov_")
    for d in ("2026-10-20", "2026-10-21"):
        with open(os.path.join(tmp, f"marks-{d.replace('-', '')}.jsonl"),
                  "w", encoding="utf-8") as fh:
            fh.write("{}\n")
    cal = ["2026-10-16", "2026-10-19", "2026-10-20", "2026-10-21"]
    cov = coverage_report(cal, tmp, 4, "2026-10-21")
    ok &= cov["missing"] == ["2026-10-16", "2026-10-19"]
    ok &= cov["present"] == ["2026-10-20", "2026-10-21"]
    ok &= cov["last_present"] == "2026-10-21" and cov["coverage_share"] == 0.5
    # S15: future calendar rows are not expected yet; empty calendar is honest
    ok &= coverage_report(cal, tmp, 9, "2026-10-20")["missing"] == [
        "2026-10-16", "2026-10-19"]
    ok &= coverage_report([], tmp, 4, "2026-10-21")["coverage_share"] is None
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    # S16 (r1101): stale-takeover gate -- flag XOR stale never enough, and a
    # fresh owner heartbeat always wins (embedded lane must not double-write).
    ok &= takeover_decision(False, 10_000)[0] is False          # no flag
    ok &= takeover_decision(True, None)[0] is False             # unreadable
    ok &= takeover_decision(True, TAKEOVER_STALE_MIN - 1)[0] is False
    ok &= takeover_decision(False, TAKEOVER_STALE_MIN)[0] is False
    ok_t, why_t = takeover_decision(True, TAKEOVER_STALE_MIN)
    ok &= ok_t is True and "silent" in why_t
    ok &= _machine_id() != ""                                   # identity read
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = _selftest()
        print("update_intraday_marks selftest:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    if "--coverage" in argv:
        days = 15
        if "--days" in argv:
            days = int(argv[argv.index("--days") + 1])
        cal = _calendar_dates()
        if not cal:
            print("coverage: no local daily calendar found", file=sys.stderr)
            return 2
        cov = coverage_report(cal, MARKS_DIR, days,
                              dt.date.today().isoformat())
        print(f"marks coverage: {len(cov['present'])}/{len(cov['expected'])} "
              f"trading days present (last {days}), "
              f"last_present={cov['last_present']}, "
              f"missing={','.join(cov['missing']) or 'none'}")
        return 3 if cov["missing"] else 0
    return run(force="--force" in argv, takeover_flag="--takeover" in argv)


if __name__ == "__main__":
    sys.exit(main())
