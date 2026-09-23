"""Data layer: 100% V8-free multi-source pipeline (all endpoints verified live
from this host, 2026-09-19):

- stocks full history: Tencent RAW klines (kline/kline endpoint, 800/chunk,
  backward-chunked) x sina qfq factor divisors (qfq = raw / F(date)) — replaces
  akshare's py_mini_racer/V8 path which is NOT thread-safe (FATAL
  partition_address_space crash under concurrent fetches).
- stocks daily increment: qt.gtimg.cn realtime quote = one self-contained bar
  (date/OHLC/volume/REAL amount/float cap, field map empirically verified).
- factor re-anchor handling: sina qfq factors re-anchor on every new ex-div;
  per-stock factor snapshots (sidecar) let us rescale stored history precisely.
- index: Tencent fqkline via proxy.finance.qq.com (no corporate actions).
- stock list: akshare stock_info_a_code_name (SSE/SZSE official pages, no V8).
- amount for full-history fetches of NEW stocks is approximated (OHLC-mean x
  volume); the 5019 existing backfilled files hold REAL amounts. Float shares
  for new stocks = current quote floatcap/close (constant over history).
"""
import json
import time
import threading
import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests

import config as C
import indicators as ind

PANEL_FIELDS = ["open", "close", "pct_chg", "amount", "volume", "high", "low",
                "preclose", "outstanding_share"]
PER_STOCK_T = [
    "open", "close", "pct_chg", "amount", "gap", "ma10", "ma20", "ma60",
    "vol_ratio5", "rsi14", "roll_high20", "roll_high60", "mom20", "mom60",
    "rng_pos", "ma20_slope", "dd60", "amt_rank", "mktcap_rank",
    "mom50", "rps50", "rps120", "rh250", "macd_dif", "macd_dea",
    "atr14", "cci14", "wr10", "mfi14", "adx14", "stoch_k", "stoch_d",
    "maxret20", "mom_accel", "intraday_ret", "lhb_net",
]
PER_STOCK_B = ["limit_up", "open_ban", "open_bust", "tradable"]

_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
       "Referer": "https://gu.qq.com/"}
_TX_FQ_URLS = ["https://proxy.finance.qq.com/ifzqgtimg/appstock/app/fqkline/get",
               "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"]
_TX_RAW_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/kline/kline"
_QT_URL = "https://qt.gtimg.cn/q="
_SINA_QFQ_URL = "https://finance.sina.com.cn/realstock/company/{sym}/qfq.js"
_TX_CHUNK = 800

_tls = threading.local()
_th_lock = threading.Lock()
_last_req = {"t": 0.0}


def _session():
    if getattr(_tls, "s", None) is None:
        s = requests.Session()
        s.headers.update(_UA)
        _tls.s = s
    return _tls.s


def _throttle(min_gap=0.06):
    with _th_lock:
        wait = min_gap - (time.time() - _last_req["t"])
        if wait > 0:
            time.sleep(wait)
        _last_req["t"] = time.time()


def _today_iso():
    return dt.date.today().strftime("%Y-%m-%d")


def _sym(code) -> str:
    return ("sh" if str(code).startswith(("60", "68")) else "sz") + str(code)


# ---------------------------------------------------------------- sina qfq factors
def _sina_factors(code) -> pd.DataFrame:
    """Cumulative qfq DIVISORS: qfq(t) = raw(t) / F(t), F = latest entry d<=t.
    Anchored so F=1.0 for the most recent segment; re-anchors on new ex-div."""
    last_err = None
    for k in range(C.DL_RETRIES):
        try:
            _throttle(0.1)
            r = _session().get(_SINA_QFQ_URL.format(sym=_sym(code)), timeout=15)
            body = r.text.split("=", 1)[1].split("\n")[0].strip().rstrip(";")
            d = json.loads(body)
            if not d.get("data"):
                return pd.DataFrame(columns=["d", "f"])
            fdf = pd.DataFrame(d["data"])
            fdf["d"] = pd.to_datetime(fdf["d"])
            fdf["f"] = fdf["f"].astype(float)
            return fdf.sort_values("d").reset_index(drop=True)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.8 * (k + 1))
    raise RuntimeError(f"sina factors {code} failed: {last_err}")


def _factor_path(code):
    return C.BARS_DIR / f"{code}.factor.json"


def _save_factors(code, fdf):
    with open(_factor_path(code), "w", encoding="utf-8") as f:
        json.dump({"d": [str(x.date()) for x in fdf["d"]],
                   "f": [float(x) for x in fdf["f"]]}, f)


def _load_factors(code):
    p = _factor_path(code)
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return pd.DataFrame({"d": pd.to_datetime(d["d"]), "f": d["f"]})
    except Exception:  # noqa: BLE001
        return None


def _f_at(fdf, dates):
    """Vectorized: divisor in effect for each date (latest entry d <= date)."""
    if fdf is None or fdf.empty:
        return np.ones(len(dates), dtype=float)
    idx = np.searchsorted(fdf["d"].values, np.asarray(dates), side="right") - 1
    idx = np.clip(idx, 0, len(fdf) - 1)
    return fdf["f"].values[idx]


def _same_factors(a, b):
    if a is None or b is None or len(a) != len(b):
        return False
    return bool((a["d"].values == b["d"].values).all()
                and np.allclose(a["f"].values, b["f"].values))


# ---------------------------------------------------------------- TX raw bars
def _tx_raw_chunk(sym, beg, end):
    """One chunk of RAW daily bars (no adjustment): [date,open,close,high,low,volume(手)]."""
    param = f"{sym},day,{beg},{end},{_TX_CHUNK}"
    last_err = None
    for k in range(C.DL_RETRIES):
        try:
            _throttle()
            r = _session().get(_TX_RAW_URL, params={"param": param}, timeout=15)
            data = (r.json() or {}).get("data")
            if not isinstance(data, dict) or sym not in data:
                return []
            inner = data[sym]
            if not isinstance(inner, dict) or "day" not in inner:
                return []
            return [list(row[:6]) for row in inner["day"]
                    if isinstance(row, (list, tuple)) and len(row) >= 6]
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.8 * (k + 1))
    raise RuntimeError(f"tx_raw({param}) failed: {last_err}")


def _tx_raw_bars(code, start_ts):
    """Backward-chunked full RAW history from Tencent."""
    sym = _sym(code)
    beg = start_ts.strftime("%Y-%m-%d")
    end = _today_iso()
    rows_all = []
    for _ in range(12):
        rows = _tx_raw_chunk(sym, beg, end)
        if not rows:
            break
        rows_all = rows + rows_all
        if len(rows) < _TX_CHUNK:
            break
        end = (pd.Timestamp(rows[0][0]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        if pd.Timestamp(end) < start_ts:
            break
    if not rows_all:
        return None
    df = pd.DataFrame(rows_all, columns=["date", "open", "close", "high", "low", "volume"])
    df["date"] = pd.to_datetime(df["date"])
    for c in ("open", "close", "high", "low", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["date"] >= start_ts].drop_duplicates("date").sort_values("date")
    if df.empty:
        return None
    df["volume"] = df["volume"] * 100.0  # lots -> shares
    return df


# ---------------------------------------------------------------- qt realtime quote
def _qt_quote(code):
    """Latest trade-day bar with REAL amount + float cap (fields verified)."""
    last_err = None
    for k in range(3):
        try:
            _throttle()
            r = _session().get(_QT_URL + _sym(code), timeout=10)
            txt = r.content.decode("gbk", errors="replace")
            f = txt.split("=", 1)[1].strip().strip('";\n\r').split("~")
            if len(f) < 50:
                return None
            return {
                "date": pd.Timestamp(f[30][:8]),
                "open": float(f[5]), "close": float(f[3]),
                "high": float(f[33]), "low": float(f[34]),
                "prev_close": float(f[4]),
                "volume": float(f[36]) * 100.0,
                "amount": float(f[37]) * 1e4,
                "turnover": float(f[38]) / 100.0,
                "floatcap": float(f[44]) * 1e8,
            }
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.5 * (k + 1))
    raise RuntimeError(f"qt quote {code} failed: {last_err}")


LIVE_DIR = C.ROOT / "data" / "live"
LIVE_DIR.mkdir(parents=True, exist_ok=True)


def _qt_parse_block(line):
    """Parse one 'v_sz000001="..."' block with the verified field map."""
    if "=" not in line:
        return None
    head, payload = line.split("=", 1)
    f = payload.strip().strip('";\n\r ').split("~")
    if len(f) < 50 or not f[2].isdigit():
        return None
    try:
        return {
            "code": f[2], "name": f[1], "date": f[30][:8],
            "open": float(f[5]), "close": float(f[3]), "prev_close": float(f[4]),
            "high": float(f[33]), "low": float(f[34]),
            "volume": float(f[36]) * 100.0,
            "amount": float(f[37]) * 1e4,
            "turnover": float(f[38]) / 100.0,
            "floatcap": float(f[44]) * 1e8,
        }
    except Exception:  # noqa: BLE001
        return None


def pull_live_snapshot(codes=None, batch=60, save=True):
    """Full-market realtime snapshot via batched qt.gtimg quotes (~90 requests,
    ~20s). Saves data/live/latest.parquet + timestamped copy + latest.json."""
    if codes is None:
        spot_p = C.CACHE_DIR / "spot.parquet"
        spot = pd.read_parquet(spot_p) if spot_p.exists() else get_spot()
        codes = list(spot["code"])
    rows = []
    n_err = 0
    syms = [_sym(c) for c in codes]
    for i in range(0, len(syms), batch):
        chunk = syms[i:i + batch]
        try:
            _throttle(0.02)
            r = _session().get(_QT_URL + ",".join(chunk), timeout=15)
            txt = r.content.decode("gbk", errors="replace")
        except Exception:  # noqa: BLE001
            n_err += len(chunk)
            continue
        for line in txt.replace("\n", "").split(";"):
            rec = _qt_parse_block(line)
            if rec:
                rows.append(rec)
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(f"live snapshot empty ({len(codes)} codes, err={n_err})")
    df = df.drop_duplicates("code")
    snap_time = dt.datetime.now()
    if save:
        stamp = snap_time.strftime("%Y%m%d_%H%M%S")
        df.to_parquet(LIVE_DIR / f"snap_{stamp}.parquet", index=False)
        df.to_parquet(LIVE_DIR / "latest.parquet", index=False)
        up = int((df["close"] > df["prev_close"]).sum())
        meta = {
            "time": snap_time.strftime("%Y-%m-%d %H:%M:%S"),
            "stocks": int(len(df)),
            "trade_date": str(df["date"].iloc[0]),
            "total_amount_yi": round(float(df["amount"].sum()) / 1e8, 0),
            "up_count": up,
            "down_count": int((df["close"] < df["prev_close"]).sum()),
            "flat_count": int((df["close"] == df["prev_close"]).sum()),
            "batch_errors": n_err,
        }
        (LIVE_DIR / "latest.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        cutoff = snap_time - dt.timedelta(hours=24)  # keep last 24h of snapshots
        for p in LIVE_DIR.glob("snap_*.parquet"):
            try:
                t = dt.datetime.strptime(p.stem.replace("snap_", ""),
                                        "%Y%m%d_%H%M%S")
                if t < cutoff:
                    p.unlink()
            except Exception:  # noqa: BLE001
                pass
    return df


# ---------------------------------------------------------------- fetch/refresh
def fetch_hist(code: str, start: str) -> pd.DataFrame | None:
    """Full qfq history (new stocks / smoke): TX raw x sina factors.
    amount = OHLC-mean x volume (approx); outstanding_share = current constant."""
    start_ts = pd.to_datetime(start)
    raw = _tx_raw_bars(code, start_ts)
    if raw is None:
        return None
    fdf = _sina_factors(code)
    f = _f_at(fdf, raw["date"].values)
    for c in ("open", "close", "high", "low"):
        raw[c] = raw[c] / f
    raw["amount"] = ((raw["open"] + raw["close"] + raw["high"] + raw["low"]) / 4.0) * raw["volume"]
    raw["pct_chg"] = (raw["close"] / raw["close"].shift(1) - 1.0) * 100.0
    raw["preclose"] = raw["close"].shift(1)
    try:
        q = _qt_quote(code)
        shares = (q["floatcap"] / q["close"]) if q and q["close"] > 0 else np.nan
    except Exception:  # noqa: BLE001
        shares = np.nan
    raw["outstanding_share"] = shares
    raw["turnover"] = np.nan
    return raw[["date", "open", "close", "high", "low", "volume", "amount",
                "pct_chg", "preclose", "outstanding_share", "turnover"]]


def refresh_stock(code, path, ltd) -> str:
    """Fast daily refresh for an existing stock parquet (V8-free):
    1) fetch current factor divisors; on re-anchor rescale stored history by
       F_old/F_new per date; 2) append the latest bar(s) from the qt quote
       (real amount); multi-day gaps filled from TX raw (approx amount)."""
    fdf = _sina_factors(code)
    old = pd.read_parquet(path)
    if "date" not in old.columns:
        return "bad"
    old["date"] = pd.to_datetime(old["date"])
    side = _load_factors(code)
    if side is None or len(side) == 0:
        side = fdf  # first run: assume stored history matches current anchor
        _save_factors(code, fdf)
    elif not _same_factors(side, fdf):
        f_old = _f_at(side, old["date"].values)
        f_new = _f_at(fdf, old["date"].values)
        scale = f_old / np.where(f_new != 0, f_new, np.nan)
        for c in ("open", "close", "high", "low", "preclose"):
            old[c] = old[c] * scale
        _save_factors(code, fdf)

    last = old["date"].max()
    if pd.isna(last) or (ltd is not None and last >= ltd):
        _write_bars(code, old, path)
        return "ok"
    if ltd is None or pd.isna(ltd):
        return "ok"

    new_rows = []
    if last < ltd - pd.Timedelta(days=1):
        # multi-day gap: fill from TX raw chunk (approx amount for gap days)
        gap_raw = _tx_raw_bars(code, last + pd.Timedelta(days=1))
        if gap_raw is not None:
            gap = gap_raw[gap_raw["date"] > last]
            if len(gap):
                gf = _f_at(fdf, gap["date"].values)
                gap = gap.copy()
                for c in ("open", "close", "high", "low"):
                    gap[c] = gap[c] / gf
                gap["amount"] = ((gap["open"] + gap["close"] + gap["high"] + gap["low"])
                                / 4.0) * gap["volume"]
                gap["preclose"] = gap["close"].shift(1)
                gap["outstanding_share"] = (old["outstanding_share"].iloc[-1]
                                            if "outstanding_share" in old.columns else np.nan)
                gap["turnover"] = np.nan
                new_rows.append(gap)
                last = gap["date"].max()

    if last < ltd:  # latest day via realtime quote (real amount + fresh float cap)
        try:
            q = _qt_quote(code)
        except Exception:  # noqa: BLE001
            q = None
        if q is not None and q["date"] == pd.Timestamp(ltd) and q["volume"] > 0:
            fq = float(_f_at(fdf, [pd.Timestamp(ltd)])[0])
            bar = pd.DataFrame([{
                "date": pd.Timestamp(ltd),
                "open": q["open"] / fq, "close": q["close"] / fq,
                "high": q["high"] / fq, "low": q["low"] / fq,
                "volume": q["volume"], "amount": q["amount"],
                "outstanding_share": q["floatcap"] / q["close"] if q["close"] > 0 else np.nan,
                "turnover": q["turnover"],
            }])
            new_rows.append(bar)

    if new_rows:
        add = pd.concat(new_rows, ignore_index=True)
        merged = pd.concat([old, add], ignore_index=True)
        merged = merged.drop_duplicates("date").sort_values("date")
        merged["pct_chg"] = (merged["close"] / merged["close"].shift(1) - 1.0) * 100.0
        merged["preclose"] = merged["close"].shift(1)
        _write_bars(code, merged, path)
        return "upd"
    _write_bars(code, old, path)
    return "ok"


def _write_bars(code, df, path):
    df = df[["date", "open", "close", "high", "low", "volume", "amount",
             "pct_chg", "preclose", "outstanding_share", "turnover"]
            + (["isst"] if "isst" in df.columns else [])]
    df.to_parquet(path, index=False)


# ---------------------------------------------------------------- Tencent index
def _tx_kline(sym, beg, end, qfq=True):
    param = f"{sym},day,{beg},{end},{_TX_CHUNK},{('qfq' if qfq else '')}".rstrip(",")
    last_err = None
    for k in range(C.DL_RETRIES):
        for url in _TX_FQ_URLS:
            try:
                _throttle()
                r = _session().get(url, params={"param": param}, timeout=15)
                data = (r.json() or {}).get("data")  # raises on challenge/HTML
                if not isinstance(data, dict):
                    return []
                inner = data.get(sym)
                if not isinstance(inner, dict):
                    return []
                key = "qfqday" if qfq and "qfqday" in inner else ("day" if "day" in inner else None)
                if key is None:
                    return []
                return [list(row[:6]) for row in inner[key]
                        if isinstance(row, (list, tuple)) and len(row) >= 6]
            except Exception as e:  # noqa: BLE001
                last_err = e
        time.sleep(min(0.8 * (k + 1), 5.0))
    raise RuntimeError(f"tx_kline({param}) failed: {last_err}")


def _tx_hist_sym(sym_full, start_ts, qfq=True):
    beg = start_ts.strftime("%Y-%m-%d")
    end = _today_iso()
    rows_all = []
    for _ in range(12):
        rows = _tx_kline(sym_full, beg, end, qfq=qfq)
        if not rows:
            break
        rows_all = rows + rows_all
        if len(rows) < _TX_CHUNK:
            break
        end = (pd.Timestamp(rows[0][0]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        if pd.Timestamp(end) < start_ts:
            break
    if not rows_all:
        return None
    df = pd.DataFrame(rows_all, columns=["date", "open", "close", "high", "low", "volume"])
    df["date"] = pd.to_datetime(df["date"])
    for c in ("open", "close", "high", "low", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["date"] >= start_ts].drop_duplicates("date").sort_values("date")
    return df if len(df) else None


# ---------------------------------------------------------------- public API
def get_spot() -> pd.DataFrame:
    """A-share code+name list from exchange official pages (via akshare, no V8).
    Hardened (2026-09-21 01:12): the BJSE list page intermittently returns a
    non-JSON error body -> retry, then fall back to the cached universe so a
    flaky list page can never kill the nightly full cycle."""
    import akshare as ak
    df = None
    for attempt in range(3):
        try:
            df = ak.stock_info_a_code_name()
            break
        except Exception as e:  # noqa: BLE001
            print(f"get_spot attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            time.sleep(3 + 3 * attempt)
    if df is None or df.empty:
        cache_p = C.CACHE_DIR / "spot.parquet"
        if cache_p.exists():
            print("get_spot: FALLBACK to cached universe "
                  f"({cache_p.name}, possibly missing today's IPOs)")
            return pd.read_parquet(cache_p)
        raise RuntimeError("get_spot failed and no cached universe available")
    out = pd.DataFrame({"code": df["code"].astype(str).str.zfill(6),
                        "name": df["name"].astype(str)})
    keep = out["code"].str.startswith(C.KEEP_PREFIX)
    bad = out["name"].str.contains("退", case=False, na=False, regex=True)
    return out[keep & ~bad].reset_index(drop=True)


def _bar_path(code: str):
    return C.BARS_DIR / f"{code}.parquet"


def fetch_index(sym: str) -> pd.DataFrame:
    """Index daily history via Tencent (raw==adjusted for indices)."""
    start_ts = pd.to_datetime(C.HIST_START)
    return _tx_hist_sym("sh" + str(sym), start_ts, qfq=True)


def update_index():
    for name, sym in C.BENCH.items():
        p = C.IDX_DIR / f"{name}.parquet"
        try:
            new = fetch_index(sym)
        except Exception as e:  # noqa: BLE001
            print(f"index {name} failed: {e}")
            continue
        if new is None or new.empty:
            print(f"index {name} empty")
            continue
        if p.exists():
            old = pd.read_parquet(p)
            new = pd.concat([old, new]).drop_duplicates("date").sort_values("date")
        new.to_parquet(p, index=False)
    print("update_index: done")


def update_data(workers=8, full=False):
    """Refresh bars (V8-free, threadable) + spot + index. Returns summary."""
    spot = get_spot()
    spot.to_parquet(C.CACHE_DIR / "spot.parquet", index=False)
    codes = list(spot["code"])
    ltd = last_trade_date()
    todo_full, todo_inc = [], []
    for c in codes:
        p = _bar_path(c)
        if full or not p.exists():
            todo_full.append((c, C.HIST_START, None))
        else:
            try:
                last = pd.read_parquet(p, columns=["date"])["date"].max()
            except Exception:
                todo_full.append((c, C.HIST_START, None))
                continue
            if ltd is None or pd.isna(last) or last < ltd:
                todo_inc.append((c, C.HIST_START, p))

    def job(item):
        c, start, path = item
        if path is None:
            df = fetch_hist(c, start)
            if df is None or df.empty:
                return "empty"
            df.to_parquet(_bar_path(c), index=False)
            fdf = _sina_factors(c)
            _save_factors(c, fdf)
            return "new"
        return refresh_stock(c, path, ltd)

    items = todo_full + todo_inc
    n_ok = n_err = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(job, it): it[0] for it in items}
        for f in as_completed(futs):
            try:
                f.result()
                n_ok += 1
            except Exception:  # noqa: BLE001
                n_err += 1
            done = n_ok + n_err
            if done % 1000 == 0 or done == len(futs):
                print(f"  progress {done}/{len(futs)} err={n_err}", flush=True)
    update_index()
    res = {"ok": n_ok, "err": n_err, "full": len(todo_full), "inc": len(todo_inc)}
    print(f"update_data: {res}")
    return res


def last_trade_date():
    p = C.IDX_DIR / "sse.parquet"
    if not p.exists():
        return None
    return pd.read_parquet(p)["date"].max()
def build_cache():
    """Assemble bars into aligned (T, N) matrices; save .npy (mmap) + meta."""
    spot_p = C.CACHE_DIR / "spot.parquet"
    spot = pd.read_parquet(spot_p) if spot_p.exists() else get_spot()
    spot.to_parquet(spot_p, index=False)
    name_map = dict(zip(spot["code"], spot["name"]))
    files = sorted(C.BARS_DIR.glob("*.parquet"))
    keep = [f.stem for f in files if f.stem.startswith(C.KEEP_PREFIX)]
    keep = [c for c in keep if c in name_map]
    print(f"build_cache: {len(keep)} stocks")

    sse = pd.read_parquet(C.IDX_DIR / "sse.parquet")
    cal = pd.to_datetime(sse["date"]).reset_index(drop=True)
    T = len(cal)

    fields = {k: {} for k in PANEL_FIELDS}
    for c in keep:
        df = pd.read_parquet(_bar_path(c))
        df["date"] = pd.to_datetime(df["date"])
        s = df.set_index("date")
        for k in PANEL_FIELDS:
            fields[k][c] = s[k] if k in s.columns else pd.Series(dtype=float)
    P = {}
    for k in PANEL_FIELDS:
        P[k] = pd.DataFrame(fields[k]).reindex(cal).astype(np.float32)
        fields[k] = None
    close, open_, high, low = P["close"], P["open"], P["high"], P["low"]
    volume, amount, pc = P["volume"], P["amount"], P["pct_chg"]

    preclose = P["preclose"].where(np.isfinite(P["preclose"]), close.shift(1))
    gap = (open_ / preclose - 1.0) * 100.0
    ma10, ma20, ma60 = ind.sma(close, 10), ind.sma(close, 20), ind.sma(close, 60)
    vol_ratio5 = volume / volume.rolling(5, min_periods=5).mean()
    rsi14 = ind.rsi(close, 14)
    rh20, rh60 = ind.rmax(close, 20), ind.rmax(close, 60)
    rh250 = ind.rmax(close, 250)
    mom20, mom60 = ind.pct_change(close, 20), ind.pct_change(close, 60)
    mom50, mom120 = ind.pct_change(close, 50), ind.pct_change(close, 120)
    rng_pos = (close - low) / (high - low + 1e-6)
    ma20_slope = ma20 / ma20.shift(5) - 1.0
    dd60 = close / rh60 - 1.0
    mktcap = close * P["outstanding_share"]
    # MACD (12,26,9): DIF/DEA over adjusted closes - causal EMA chain
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_dif = ema12 - ema26
    macd_dea = macd_dif.ewm(span=9, adjust=False).mean()
    # ---- 细分指标层 (2026-09-21 用户令"下载全面技术指标/极度细分策略") ----
    # pandas-vectorized cross-section fields:
    maxret20 = pc.rolling(20, min_periods=20).max()      # lottery/MAX effect
    mom_accel = mom20 - mom50                            # momentum speed-up
    intraday_ret = close / np.where(open_ > 0, open_, np.nan) - 1.0
    # TA-Lib C-speed per-column fields (ATR/CCI/WR/MFI/ADX/STOCH):
    talib = None
    try:
        import talib
    except Exception:  # noqa: BLE001
        pass
    if talib is not None:
        H = np.ascontiguousarray(high.values, dtype=np.float64)
        L = np.ascontiguousarray(low.values, dtype=np.float64)
        Cv = np.ascontiguousarray(close.values, dtype=np.float64)
        Vv = np.ascontiguousarray(volume.values, dtype=np.float64)
        Nc = Cv.shape[1]
        atr14 = np.full(Cv.shape, np.nan)
        cci14 = np.full(Cv.shape, np.nan)
        wr10 = np.full(Cv.shape, np.nan)
        mfi14 = np.full(Cv.shape, np.nan)
        adx14 = np.full(Cv.shape, np.nan)
        stoch_k = np.full(Cv.shape, np.nan)
        stoch_d = np.full(Cv.shape, np.nan)
        for i in range(Nc):
            h, l, c, v = H[:, i], L[:, i], Cv[:, i], Vv[:, i]
            if not np.isfinite(c).any():
                continue
            # NaN-free segment approach (2026-09-21): TA-Lib's ATR/MFI/STOCH
            # propagate NaN FOREVER after a suspension gap (Wilder recursion).
            # Calling them per contiguous finite segment re-warms the chain at
            # every gap, so a halt kills only the local window - not history.
            ok = np.isfinite(h) & np.isfinite(l) & np.isfinite(c) \
                & np.isfinite(v)
            segs = []
            start = None
            for t in range(len(ok)):
                if ok[t] and start is None:
                    start = t
                elif not ok[t] and start is not None:
                    segs.append((start, t))
                    start = None
            if start is not None:
                segs.append((start, len(ok)))
            for a, b in segs:
                if b - a < 30:
                    continue
                hs, ls, cs, vs = h[a:b], l[a:b], c[a:b], v[a:b]
                atr14[a:b, i] = talib.ATR(hs, ls, cs, timeperiod=14)
                mfi14[a:b, i] = talib.MFI(hs, ls, cs, vs, timeperiod=14)
                sk, sd = talib.STOCH(hs, ls, cs, fastk_period=9,
                                     slowk_period=3, slowk_matype=0,
                                     slowd_period=3)
                stoch_k[a:b, i] = sk
                stoch_d[a:b, i] = sd
            # CCI/WILLR/ADX are NaN-recovering - plain calls are safe
            cci14[:, i] = talib.CCI(h, l, c, timeperiod=14)
            wr10[:, i] = talib.WILLR(h, l, c, timeperiod=10)
            adx14[:, i] = talib.ADX(h, l, c, timeperiod=14)
        atr14 = pd.DataFrame(atr14, index=close.index, columns=close.columns)
        cci14 = pd.DataFrame(cci14, index=close.index, columns=close.columns)
        wr10 = pd.DataFrame(wr10, index=close.index, columns=close.columns)
        mfi14 = pd.DataFrame(mfi14, index=close.index, columns=close.columns)
        adx14 = pd.DataFrame(adx14, index=close.index, columns=close.columns)
        stoch_k = pd.DataFrame(stoch_k, index=close.index, columns=close.columns)
        stoch_d = pd.DataFrame(stoch_d, index=close.index, columns=close.columns)
    else:  # graceful degradation: families depending on these stay asleep
        nanf = pd.DataFrame(np.nan, index=close.index, columns=close.columns)
        atr14 = cci14 = wr10 = mfi14 = adx14 = stoch_k = stoch_d = nanf

    # ---- 龙虎榜聪明钱字段 (user order: beyond technical analysis) ----
    # Point-in-time ONLY: uses 上榜日 + 净买额/市场总成交额 (published after
    # that day's close -> tradeable at next open). The forward-return columns
    # (上榜后N日) are LOOKAHEAD data and are deliberately never read here.
    lhb_net = np.full(close.shape, np.nan, dtype=np.float32)
    lhb_p = C.ROOT / "data" / "lhb" / "lhb_detail.parquet"
    if lhb_p.exists():
        try:
            lhb = pd.read_parquet(lhb_p)
            lhb["d"] = pd.to_datetime(lhb["上榜日"]).dt.normalize()
            g = (lhb.groupby(["代码", "d"])["净买额占总成交比"]
                 .max().reset_index())
            day_pos = {d: i for i, d in enumerate(cal)}
            col_pos = {c: i for i, c in enumerate(close.columns)}
            dv = g["d"].map(day_pos)
            cv = g["代码"].astype(str).str.zfill(6).map(col_pos)
            ok = dv.notna() & cv.notna()
            if ok.any():
                lhb_net[dv[ok].astype(int).values,
                        cv[ok].astype(int).values] = \
                    g.loc[ok, "净买额占总成交比"].values.astype(np.float32)
            print(f"lhb_net: {int(ok.sum())} stock-days merged")
        except Exception as e:  # noqa: BLE001
            print(f"lhb integration failed (families sleep): {e}")
    lhb_net = pd.DataFrame(lhb_net, index=close.index, columns=close.columns)

    N = close.shape[1]
    codes_arr = np.asarray(list(close.columns), dtype="<U8")
    names_arr = np.asarray([name_map.get(c, "") for c in close.columns], dtype="<U16")
    p2 = codes_arr.astype("U2")
    lim_pct = np.where((p2 == "30") | (p2 == "68"), 20.0, 10.0).astype(np.float32)

    def daily_rank(mat_values):
        r = np.full((T, N), np.nan, dtype=np.float32)
        for t in range(T):
            row = mat_values[t]
            m = np.isfinite(row)
            if m.sum() < 10:
                continue
            idx = np.argsort(row[m], kind="stable")
            r[t, m] = (np.argsort(idx) / max(m.sum() - 1, 1)).astype(np.float32)
        return r

    amt_rank = daily_rank(amount.values.astype(np.float64))
    mktcap_rank = daily_rank(mktcap.values.astype(np.float64))
    rps50 = daily_rank(mom50.values.astype(np.float64))
    rps120 = daily_rank(mom120.values.astype(np.float64))

    def f32(x):
        a = x.values if hasattr(x, "values") else x
        return a.astype(np.float32)

    first_valid = np.argmax(np.isfinite(close.values), axis=0)
    has_data = np.isfinite(close.values).any(axis=0)
    day_idx = (np.arange(T)[:, None] - first_valid[None, :]).astype(np.int32)
    day_idx[:, ~has_data] = -10 ** 6

    lim_b = lim_pct[None, :]
    limit_up = (pc.values >= lim_b - 0.15) & np.isfinite(pc.values)
    open_ban = (gap.values >= lim_b - 0.05) & np.isfinite(gap.values)
    open_bust = (gap.values <= -(lim_b - 0.05)) & np.isfinite(gap.values)
    cv = close.values
    av = amount.values
    tradable = ((day_idx >= C.MIN_LIST_DAYS) & np.isfinite(cv)
                & (cv >= C.MIN_PRICE) & (cv <= C.MAX_PRICE) & (av >= C.MIN_AMOUNT))

    above = (cv > ma20.values) & np.isfinite(ma20.values)
    listed = np.isfinite(cv) & (day_idx >= C.MIN_LIST_DAYS)
    breadth = np.where(listed.sum(1) > 0,
                        (above & listed).sum(1) / np.maximum(listed.sum(1), 1),
                        0.0).astype(np.float32)

    np.save(C.CACHE_DIR / "codes.npy", codes_arr)
    np.save(C.CACHE_DIR / "names.npy", names_arr)
    np.save(C.CACHE_DIR / "dates.npy", cal.values.astype("datetime64[D]"))
    np.save(C.CACHE_DIR / "lim_pct.npy", lim_pct)
    np.save(C.CACHE_DIR / "day_idx.npy", day_idx)
    np.save(C.CACHE_DIR / "breadth.npy", breadth)
    for nm, arr in {
        "open": open_, "close": close, "pct_chg": pc, "amount": amount, "gap": gap,
        "ma10": ma10, "ma20": ma20, "ma60": ma60, "vol_ratio5": vol_ratio5,
        "rsi14": rsi14, "roll_high20": rh20, "roll_high60": rh60,
        "mom20": mom20, "mom60": mom60, "rng_pos": rng_pos,
        "ma20_slope": ma20_slope, "dd60": dd60, "amt_rank": amt_rank,
        "mktcap_rank": mktcap_rank, "mom50": mom50,
        "rps50": rps50, "rps120": rps120,
        "rh250": rh250, "macd_dif": macd_dif, "macd_dea": macd_dea,
        "atr14": atr14, "cci14": cci14, "wr10": wr10, "mfi14": mfi14,
        "adx14": adx14, "stoch_k": stoch_k, "stoch_d": stoch_d,
        "maxret20": maxret20, "mom_accel": mom_accel,
        "intraday_ret": intraday_ret, "lhb_net": lhb_net,
    }.items():
        np.save(C.CACHE_DIR / f"{nm}.npy", f32(arr))
    for nm, arr in {"limit_up": limit_up, "open_ban": open_ban,
                    "open_bust": open_bust, "tradable": tradable}.items():
        np.save(C.CACHE_DIR / f"{nm}.npy", arr)
    for b in ("hs300", "csi500", "sse"):
        bp = C.IDX_DIR / f"{b}.parquet"
        arr = (pd.read_parquet(bp).set_index("date")["close"].reindex(cal).values.astype(np.float32)
               if bp.exists() else np.full(T, np.nan, np.float32))
        np.save(C.CACHE_DIR / f"bench_{b}.npy", arr)
    print(f"build_cache: T={T} N={N} {cal.iloc[0].date()}..{cal.iloc[-1].date()}")
    return {"T": T, "N": N}


def load_cache(mmap=True):
    """Load panel cache. Big tensors are memmaps when mmap=True (parallel workers)."""
    mode = "r" if mmap else None
    out = {"dates": np.load(C.CACHE_DIR / "dates.npy"),
           "codes": np.load(C.CACHE_DIR / "codes.npy"),
           "names": np.load(C.CACHE_DIR / "names.npy"),
           "lim_pct": np.load(C.CACHE_DIR / "lim_pct.npy")}
    for nm in PER_STOCK_T + PER_STOCK_B + ["day_idx"]:
        p = C.CACHE_DIR / f"{nm}.npy"
        if p.exists():
            out[nm] = np.load(p, mmap_mode=mode)
    p = C.CACHE_DIR / "breadth.npy"
    if p.exists():
        out["breadth"] = np.load(p, mmap_mode=mode)
    for b in ("hs300", "csi500", "sse"):
        p = C.CACHE_DIR / f"bench_{b}.npy"
        if p.exists():
            out[f"bench_{b}"] = np.load(p, mmap_mode=mode)
    return out


def window(cache, i0, i1):
    """Slice all per-stock tensors to [i0:i1] (views when mmap)."""
    sl = slice(i0, i1)
    return {k: cache[k][sl] for k in cache if k in PER_STOCK_T + PER_STOCK_B}
