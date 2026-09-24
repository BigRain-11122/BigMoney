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

Gates (script-side, safe under any scheduler cadence):
  - non-workday OR before 09:30 OR after 15:10 -> legal no-op exit 0
  - 09:30 <= now < 15:00 -> intraday tick
  - 15:00 <= now <= 15:10 -> settle face (once per day; later ticks no-op)
  - --force bypasses the clock gate for pipeline validation ONLY (the
    run is stamped kind="forced" and never counts as trading evidence)

Usage:
    python scripts/update_intraday_marks.py            # gated run
    python scripts/update_intraday_marks.py --force    # validation run
    python scripts/update_intraday_marks.py --selftest
Exit codes: 0 = ok/no-op, 2 = source/mechanism failure (honest).
"""
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

PAPER_DIR = os.path.join(PATHS.results_dir, "paper")
MARKS_DIR = os.path.join(PAPER_DIR, "marks")
OPEN_T = dt.time(9, 30)
SETTLE_T = dt.time(15, 0)
CLOSE_GRACE_T = dt.time(15, 10)
ATTEMPTS = 3
BACKOFF_S = (5, 10)
SOURCE_ORDER = ("fund_etf_category_sina", "fund_etf_spot_ths")


def _now() -> dt.datetime:
    return dt.datetime.now()


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
             meta: dict) -> dict:
    traders_out = {}
    for tid, st in states.items():
        cap = st["capital"]
        cash = float((cap or {}).get("cash_cny") or 0.0)
        poss, mv_total = [], 0.0
        for p in st["positions"]:
            sym = p["symbol"]
            q = quotes.get(sym)
            mark = q["last"] if q else p.get("last_close")
            mv = round(p["quantity"] * mark, 2) if mark else None
            if mv:
                mv_total += mv
            poss.append({
                "symbol": sym, "quantity": p["quantity"],
                "cost_price": p["cost_price"],
                "session_open": (q or {}).get("open"),
                "mark": mark,
                "market_value_cny": mv,
                "unrealized_pnl_cny":
                    round((mark - p["cost_price"]) * p["quantity"], 2)
                    if mark else None,
                "marked": bool(q),
            })
        traders_out[tid] = {
            "cash_cny": round(cash, 2),
            "positions": poss,
            "equity_mark_cny": round(cash + mv_total, 2),
            "state_cutoff": st["cutoff"],
        }
    return {"ts": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "kind": kind, "source": meta["source"],
            "source_rows": meta["rows"], "traders": traders_out}


def run(force: bool = False) -> int:
    now = _now()
    kind = "forced" if force else _gate(now)
    if force:
        kind = "forced"
    elif kind == "noop":
        print(f"intraday_marks: no-op (outside trading window, {now:%H:%M})")
        return 0
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
    with open(marks_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    n_marked = sum(1 for t in states.values() for p in t["positions"])
    print(f"intraday_marks: {kind} tick appended ({n_marked} positions, "
          f"source {meta['source']}, {meta['latency_s']}s) -> {marks_path}")
    return 0


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
    # S4: unmarked symbol falls back to last close (never fabricated)
    states2 = {"T-X": {"positions": [
                   {"symbol": "999999", "quantity": 10.0,
                    "cost_price": 1.0, "hold_days": 1}],
               "capital": {"cash_cny": 0.0}, "cutoff": "2026-09-23"}}
    line2 = _compose(states2, quotes, dt.datetime(2026, 9, 24, 10, 0),
                     "intraday", {"source": "x", "rows": 1})
    ok &= line2["traders"]["T-X"]["positions"][0]["marked"] is False
    ok &= line2["traders"]["T-X"]["equity_mark_cny"] == 0.0
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
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = _selftest()
        print("update_intraday_marks selftest:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return run(force="--force" in argv)


if __name__ == "__main__":
    sys.exit(main())
