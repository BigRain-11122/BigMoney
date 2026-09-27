"""REV-OSC live signal+bars export (T-91 s2 consumption face, bm-b lane).

Lane law (R31 family): the A-share per-stock daily panel (data/astock_daily,
gitignored, forward supply lane owner = bm-b per T-2026-09-26-87) lives only
on the lane machine. T-91 (SYSTEM-V1 live paper harness, bm-a) needs the
frozen REV-OSC stock signal forward face -- so the SIGNAL is exported on the
panel machine as small tracked artifacts (git = the transfer channel,
fleet/TRANSFER.md control-plane law), and the harness replays deterministically
from git-tracked faces on ANY machine. Zero full-panel duplication, zero
second puller: this script is the single bridge.

Frozen signal definition = REV_OSC_STOCK_PREREG s3 FY_BG_TP8 cell face,
mirrored verbatim via constants imported from scripts/rev_osc_stock_p1.py
(zero re-implementation): 20d-drop Top10 + first-bullish + bear-gate +
dynamic eligibility (b_layer ok_static & board!=other & close>=1 &
amount20>=5e7 & listed>=20 bars & fresh<=250td). Gate live face = 510300
ETF close < MA200 (clock trigger #10 same face, forward-refreshed; the judged
face used the frozen Money02 sse index -- proxy equivalence disclosed in every
SIG file).

Products (tracked, small, latest-wins per date = qfq adjusted truth):
  results/rev_osc_live/SIG-<date>.json   daily Top10 evidence snapshot
  results/rev_osc_live/BARS-<date>.json  recent-picks OHLC rows (~15 bars)

Idempotency: no-op while panel cutoff / panel bytes unchanged (max per-file
mtime stamp law); recompute is deterministic from panel bytes -> byte-stable
per (date, panel bytes). Marks/trials ledger +0, SEED_REGISTRY +0 (pure
measurement face).

Usage: python scripts/rev_osc_signal_export.py run | selftest
Exit codes: 0 = ok/no-op; 2 = machinery fault (honest, never masked).
Lane guard: acts only on bm-b (machine_id from fleet/machine.json); every
other machine = stdout-only honest no-op.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

from rev_osc_stock_p1 import (AMT20_MIN, FRESH_MAX, LISTED_MIN,  # noqa: F401
                              PRICE_MIN, THIN_MARKET_MIN)

MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
STATUS_JSON = os.path.join(ROOT, "results",
                           "astock_daily_update_status.json")
PER_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
MASK_CSV = os.path.join(ROOT, "data", "fundamental", "b_layer_mask.csv")
ETF = os.path.join(ROOT, "data", "daily", "510300.csv")
OUT_DIR = os.path.join(ROOT, "results", "rev_osc_live")
STATE = os.path.join(OUT_DIR, "_export_state.json")

LANE_OWNER = "bm-b"          # T-87 panel-lane owner (R31 precedent)
TOP_N = 10                   # prereg s3 frozen
BARS_ROWS = 15               # covers hold 7-10d + rolls + entry slack
RELEVANT_TD = 15             # picks within last 15 trading days stay hot
AMT20_MIN_COUNT = 10         # _roll_mean20 min-finite mirror (judged face)
GATE_DISCLOSURE = (
    "judged face gate = sse_close<MA200 (Money02 p1c index, frozen "
    "2026-09-22); live forward face = 510300 ETF close<MA200 (market-clock "
    "trigger #10 same face, forward-refreshed by update_daily; SYSTEM_V1 "
    "L1 clock authority) -- proxy equivalence disclosed per SIG file")


def _read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def load_mask(mask_csv=MASK_CSV):
    """ok_static universe + board map (b_layer face, judged s2 mirror)."""
    m = pd.read_csv(mask_csv, dtype={"code": str})
    ok = m[m["ok_static"] == True]                                  # noqa: E712
    ok = ok[ok["board"] != "other"]
    return ok.set_index("code")["board"].to_dict()


def etf_gate(etf_csv=ETF):
    """510300 close + MA200 series (forward-refreshed, git-tracked)."""
    df = pd.read_csv(etf_csv, parse_dates=["date"]).set_index("date")
    df = df.sort_index()
    ma = df["close"].rolling(200, min_periods=200).mean()
    return df["close"], ma


def compute_signal_day(frames, boards, signal_date, etf_close, etf_ma):
    """Pure frozen-face core. frames = {code: DataFrame(date,open,close,
    amount)} full history; boards = {code: board}. Returns the SIG dict
    WITHOUT wall-clock fields (caller adds 'updated')."""
    sd = pd.Timestamp(signal_date)
    if sd not in etf_close.index or sd not in etf_ma.index:
        raise ValueError(f"signal date {signal_date} missing from ETF face")
    gate_open = bool(np_isfinite(etf_ma[sd]) and etf_close[sd] < etf_ma[sd])
    gate = {"face": "510300_close<MA200", "signal_date": str(sd.date()),
            "close": round(float(etf_close[sd]), 4),
            "ma200": round(float(etf_ma[sd]), 4) if np_isfinite(etf_ma[sd])
            else None,
            "open": gate_open, "disclosure": GATE_DISCLOSURE}

    picks, seen = [], {}
    n_read = n_with_bar = 0
    for code in sorted(frames):                       # tie -> low code first
        if code not in boards:
            continue
        df = frames[code]
        n_read += 1
        if df.index[-1] != sd:
            continue                              # no bar on signal day
        n_with_bar += 1
        row = df.loc[sd]
        close, op, amt = row["close"], row["open"], row["amount"]
        if not (np_isfinite(close) and np_isfinite(op)):
            continue
        if close < PRICE_MIN or len(df) < LISTED_MIN:
            continue
        if not np_isfinite(amt):
            continue
        # first-bullish (prereg s3): close>open on signal day
        if not close > op:
            continue
        # amount20: mean of finite amounts over last 20 bars ending at sd
        tail = df["amount"].iloc[-20:]
        fin = tail[np.isfinite(tail.values)]
        if len(fin) < AMT20_MIN_COUNT or float(fin.mean()) < AMT20_MIN:
            continue
        # drop20 / drop60 positional (judged face: close[t]/close[t-20]-1)
        if len(df) < 21:
            continue
        prev20 = float(df["close"].iloc[-21])
        if not np_isfinite(prev20):
            continue
        drop20 = float(close) / prev20 - 1.0
        drop60 = None
        if len(df) >= 61:
            prev60 = float(df["close"].iloc[-61])
            if np_isfinite(prev60):
                drop60 = float(close) / prev60 - 1.0
        seen[code] = drop20
        picks.append({"code": code, "board": boards[code],
                      "drop20": round(drop20, 6),
                      "drop60": (round(drop60, 6)
                                 if drop60 is not None else None),
                      "close": round(float(close), 4),
                      "open": round(float(op), 4),
                      "amount20": round(float(fin.mean()), 0)})
    picks.sort(key=lambda p: (p["drop20"], p["code"]))   # deepest first
    picks = picks[:TOP_N]
    for i, p in enumerate(picks):
        p["rank"] = i
    thin = len(seen) < THIN_MARKET_MIN
    return {"schema": "rev_osc_live_sig_v1",
            "date": str(sd.date()),
            "gate": gate,
            "universe": {"ok_static_n": len(boards), "panel_read_n": n_read,
                         "with_bar_n": n_with_bar,
                         "qualified_n": len(seen)},
            "thin_market": thin,
            "picks": [] if thin else picks,
            "params": {"top_n": TOP_N, "drop_win": 20, "first_bullish": True,
                       "eligibility": "b_layer ok_static & board!=other & "
                         "close>=1 & amount20>=5e7 (min 10 finite) & "
                         "listed>=20 bars & bar on signal day",
                       "frozen_mirror":
                         "REV_OSC_STOCK_PREREG s3 FY_BG_TP8 signal face "
                         "(constants imported from rev_osc_stock_p1.py)"},
            "cost_ref": "P4_BATCH2 13.041bp/side x1 (judged face anchor)"}


def relevant_codes(sig_dir, signal_date, etf_close, today_picks):
    """today picks + picks from SIG files within the last RELEVANT_TD
    trading days (self-history face; covers in-flight cohorts)."""
    codes = set(today_picks)
    sd = pd.Timestamp(signal_date)
    pos = etf_close.index.get_loc(sd)
    lo = etf_close.index[max(pos - RELEVANT_TD, 0)]
    for fn in os.listdir(sig_dir):
        if not (fn.startswith("SIG-") and fn.endswith(".json")):
            continue
        d = fn[4:-5]
        if pd.Timestamp(d) < lo:
            continue
        try:
            sig = _read_json(os.path.join(sig_dir, fn))
        except Exception:                                          # noqa: BLE001
            continue                       # torn/foreign file -> skip honest
        for p in sig.get("picks", []):
            codes.add(p["code"])
    return codes


def bars_payload(frames, codes, signal_date):
    """Last BARS_ROWS rows per relevant code (qfq face, latest-wins truth)."""
    rows = {}
    for code in sorted(codes):
        df = frames.get(code)
        if df is None:
            continue
        df = df.loc[df.index <= pd.Timestamp(signal_date)]
        out = []
        for d, r in df.tail(BARS_ROWS).iterrows():
            out.append([str(pd.Timestamp(d).date()), round(float(r["open"]), 4),
                        round(float(r["high"]), 4), round(float(r["low"]), 4),
                        round(float(r["close"]), 4)])
        if out:
            rows[code] = out
    return rows


def np_isfinite(x):
    """Scalar finite check (None-safe for pandas row scalars)."""
    return x is not None and bool(np.isfinite(x))


# ------------------------------ the lane -----------------------------------

def run() -> int:
    try:
        with open(MACHINE_JSON, encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id", "")
        if mid != LANE_OWNER:
            print(f"rev_osc_signal_export: lane guard (owner={LANE_OWNER}, "
                  f"this={mid}) -- stdout-only honest no-op")
            return 0

        status = _read_json(STATUS_JSON)
        panel = status.get("panel", {})
        if not panel.get("complete"):
            print("rev_osc_signal_export: panel incomplete "
                  f"(cutoff={panel.get('cutoff')}) -- no-op, harness waits")
            return 0
        cutoff = panel["cutoff"]

        os.makedirs(OUT_DIR, exist_ok=True)
        sig_path = os.path.join(OUT_DIR, f"SIG-{cutoff}.json")
        bars_path = os.path.join(OUT_DIR, f"BARS-{cutoff}.json")
        mtime_max = 0.0
        if os.path.isdir(PER_DIR):
            for fn in os.listdir(PER_DIR):
                if fn.endswith(".csv"):
                    mtime_max = max(mtime_max,
                                   os.path.getmtime(
                                       os.path.join(PER_DIR, fn)))
        if os.path.exists(STATE):
            try:
                st = _read_json(STATE)
                if (st.get("last_date") == cutoff
                        and os.path.exists(sig_path)
                        and os.path.exists(bars_path)
                        and st.get("panel_mtime_max", -1.0) >= mtime_max):
                    print(f"rev_osc_signal_export: SIG/BARS already at "
                          f"cutoff {cutoff} & panel bytes unchanged "
                          "-- no-op (idempotent)")
                    return 0
            except Exception:                                      # noqa: BLE001
                pass                       # torn state -> full recompute

        # -- load faces
        boards = load_mask()
        etf_close, etf_ma = etf_gate()
        frames = {}
        for code in boards:
            p = os.path.join(PER_DIR, f"{code}.csv")
            if not os.path.exists(p):
                continue                    # code not in panel -> skip honest
            df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
            frames[code] = df.sort_index()[["open", "high", "low", "close",
                                            "amount"]]

        sig = compute_signal_day(frames, boards, cutoff, etf_close, etf_ma)
        today = [p["code"] for p in sig["picks"]]
        codes = relevant_codes(OUT_DIR, cutoff, etf_close, today)
        bars = bars_payload(frames, codes, cutoff)

        sig["panel_cutoff"] = cutoff
        sig["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _atomic_json(sig_path, sig)
        _atomic_json(bars_path, {"schema": "rev_osc_live_bars_v1",
                                 "date": cutoff, "rows": bars,
                                 "updated": sig["updated"]})
        _atomic_json(STATE, {"last_date": cutoff,
                             "panel_mtime_max": mtime_max})
        print(f"rev_osc_signal_export: SIG-{cutoff} picks={len(today)} "
              f"gate_open={sig['gate']['open']} thin={sig['thin_market']} "
              f"bars_codes={len(bars)} -> {OUT_DIR}")
        return 0
    except SystemExit as e:
        print(f"rev_osc_signal_export mechanism fault (gate): {e}")
        return 2
    except Exception as e:                                          # noqa: BLE001
        print(f"rev_osc_signal_export mechanism fault: {e}")
        return 2


# ------------------------------ selftest -----------------------------------

def selftest() -> int:
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_all &= bool(cond)
        return cond

    import numpy as np

    def mk_frame(rows):
        df = pd.DataFrame(rows, columns=["date", "open", "high", "low",
                                         "close", "amount"])
        df["date"] = pd.to_datetime(df["date"])
        return df.set_index("date").sort_index()

    cal = pd.bdate_range("2026-06-01", periods=90)   # 90 bar days
    d = lambda i: str(cal[i].date())                # noqa: E731

    def stock(code, base, drop, bull, amt=6e7, rows_n=90):
        """rows_n bars, last-bar close = base*(1+drop), bullish flag."""
        rows = []
        for i in range(rows_n):
            c = base * (1 + drop) if i == rows_n - 1 else base
            o = c * (0.99 if bull else 1.01)
            rows.append([d(i), o, c * 1.02, c * 0.98, c, amt])
        return mk_frame(rows)

    frames = {
        "600001": stock("600001", 10.0, -0.30, True),    # deepest, bullish
        "600002": stock("600002", 10.0, -0.25, True),
        "600003": stock("600003", 10.0, -0.25, True),    # tie w/ 600002
        "600004": stock("600004", 10.0, -0.20, True),
        "600005": stock("600005", 10.0, -0.10, True),
        "600006": stock("600006", 10.0, -0.40, False),   # bearish -> out
        "600007": stock("600007", 0.5, -0.50, True),    # price < 1 -> out
        "600008": stock("600008", 10.0, -0.50, True, amt=1e6),  # amt20 -> out
        "600009": stock("600009", 10.0, -0.35, True, rows_n=10),  # listed<20
        "600010": stock("600010", 10.0, -0.15, True),
    }
    boards = {c: "main" for c in frames}
    # ETF history: 200 bars ENDING at cal[-1] (aligned with stock frames);
    # last 10 bars dip to 95 -> MA200=99.75 > 95 -> gate open
    etf_dates = pd.bdate_range(end=cal[-1], periods=200)
    etf_rows = []
    for i, x in enumerate(etf_dates):
        c = 95.0 if i >= 190 else 100.0
        etf_rows.append([str(x.date()), c, c * 1.01, c * 0.99, c, 1e9])
    etf200 = mk_frame(etf_rows)

    # [1/6] ranking face: deepest first, tie -> low code, filters honored
    close, ma = etf200["close"], etf200["close"].rolling(
        200, min_periods=200).mean()
    sig = compute_signal_day(frames, boards, str(
        etf200.index[-1].date()), close, ma)
    ok("ranking: Top10 deepest-first + tie->low code + filters",
       [p["code"] for p in sig["picks"]][:4] ==
       ["600001", "600002", "600003", "600004"]
       and all(p["code"] not in ("600006", "600007", "600008", "600009")
               for p in sig["picks"])
       and len(sig["picks"]) == 6
       and sig["picks"][0]["drop20"] == round(-0.30, 6)
       and sig["universe"]["qualified_n"] == 6
       and sig["picks"][2]["rank"] == 2)

    # [2/6] gate: close<MA200 -> open; close>MA200 -> closed
    ok("gate: 100<MA200-1 -> open=true; above -> closed",
       sig["gate"]["open"] is True
       and GATE_DISCLOSURE in sig["gate"]["disclosure"])
    etf_up = mk_frame([[str(x.date()), 300.0, 301.0, 299.0, 300.0, 1e9]
                       for x in pd.bdate_range("2026-01-01", periods=200)])
    c2, m2 = etf_up["close"], etf_up["close"].rolling(
        200, min_periods=200).mean()
    sig2 = compute_signal_day(frames, boards, str(
        etf_up.index[-1].date()), c2, m2)
    ok("gate: above-MA200 face -> open=false",
       sig2["gate"]["open"] is False)

    # [3/6] thin market: <5 qualified -> thin, zero picks
    few = {k: frames[k] for k in ("600001", "600002", "600006")}
    sig3 = compute_signal_day(few, boards, str(
        etf200.index[-1].date()), close, ma)
    ok("thin market: <5 qualified -> thin=true, picks empty",
       sig3["thin_market"] is True and sig3["picks"] == [])

    # [4/6] constants frozen-mirror tripwire (drift -> selftest red)
    ok("constants imported from judged runner (no re-derivation)",
       (AMT20_MIN, PRICE_MIN, LISTED_MIN, THIN_MARKET_MIN, FRESH_MAX)
       == (5e7, 1.0, 20, 5, 250))

    # [5/6] bars payload: tail-15 rows, only relevant codes, rounded
    codes = {"600001", "600003"}
    bp = bars_payload(frames, codes, str(etf200.index[-1].date()))
    ok("bars: per-code tail rows, 5-field rows, relevant codes only",
       set(bp) == {"600001", "600003"}
       and len(bp["600001"]) == 15
       and bp["600001"][0][0] == d(75)
       and bp["600001"][-1][0] == d(89))

    # [6/6] B7b contract leg: consumer schema keys subset of producer keys
    ok("B7b contract: SIG keys cover harness-consumed face",
       {"date", "gate", "picks", "thin_market", "universe", "schema"}
       <= set(sig) and {"open", "close"} <= set(sig["gate"])
       and {"code", "board", "drop20", "rank"} <= set(sig["picks"][0]))

    if not ok_all:
        print("SELFTEST FAILED")
        return 2
    print("selftest: ALL LEGS PASS")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    print(f"usage: {sys.argv[0]} [run|selftest] (got {mode!r})")
    return 2


if __name__ == "__main__":
    sys.exit(main())
