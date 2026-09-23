"""数据层：标的清单、历史行情下载（akshare 多源容错）、面板加载。

数据源策略（本机实测 2026-09-19）：
- 东财 push2 集群不可达 → 股票/ETF/指数走新浪源（全历史，股票前复权）
- 清单：优先东财快照，失败自动降级新浪
- 场外基金净值仅东财提供 → 暂缓，supervise 每小时重试，东财恢复后自动补全
仅用于本地模拟研究。下载断点续传：data/manifest.json 记录进度，重复运行自动增量。
"""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

try:
    import akshare as ak
except Exception:
    ak = None

from .config import CFG, path, ensure_dirs

ensure_dirs()

INDEX_SYMBOLS = ["sh000300", "sh000001", "sh000905", "sz399006",
                 "hk_HSI", "us_INX"]  # Windows 文件名禁冒号，用下划线
_HIST_COLS = {"日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
              "最低": "low", "成交量": "volume", "成交额": "amount"}
_DATE_FMT = "%Y%m%d"

# 精选池（v1：巨头+行业龙头快照；免费源拉全市场过慢，cron 后续可扩展）
US_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
              "BRK.B", "LLY", "JPM", "V", "UNH", "XOM", "MA", "COST", "HD",
              "PG", "JNJ", "ABBV", "MRK", "ORCL", "CRM", "AMD", "NFLX", "ADBE",
              "PEP", "KO", "WMT", "BAC", "TMO", "LIN", "ASML", "TXN", "QCOM",
              "INTU", "AMGN", "ISRG", "CAT", "GS", "MS", "DIS", "VZ", "IBM",
              "GE", "RTX", "NKE", "UNP", "SPGI", "BLK", "MBLZ", "AXP", "GS",
              "HON", "UPS", "T", "VRTX", "GILD", "REGN", "AMAT", "LRCX", "KLAC",
              "MU", "NOW", "PANW", "CRWD", "SNPS", "CDNS", "ADP", "CMCSA",
              "MCD", "SBUX", "TGT", "LOW", "BKNG", "MAR", "MDLZ", "CL", "KMB",
              "CVX", "COP", "SLB", "PSX", "EOG", "MPC", "FCX", "NEM", "NEE",
              "DUK", "SO", "PLD", "AMT", "SPG", "O", "CCI", "WELL", "MO", "PM",
              "MDT", "ABT", "BSX", "SYK", "ZTS", "ELV", "CI", "HUM", "CVS",
              "MRNA", "BIIB", "DHR", "ROCHE", "NOVN", "AZN", "SHEL", "BP",
              "TTE", "HSBC", "BABA", "JD", "PDD", "NTES", "BIDU", "TCEHY",
              "LI", "NIO", "XPEV", "BEKE", "TME", "IQ", "YUMC", "HTHT"]
HK_TICKERS = ["00700", "09988", "03690", "09618", "01810", "09888", "01299",
              "00005", "00939", "01398", "03988", "02318", "00001", "00386",
              "00883", "02628", "03228", "01038", "00688", "01211", "02015",
              "02331", "00388", "00002", "00003", "00006", "00011", "00016",
              "00017", "00066", "00083", "00101", "00175", "00267", "00285",
              "00316", "00322", "00669", "00762", "00823", "00868", "00941",
              "00960", "00968", "01044", "01109", "01113", "01171", "01177",
              "01359", "01610", "01766", "01898", "01928", "01997", "02007",
              "02018", "02020", "02318", "02333", "02688", "02696", "02899",
              "03888", "06030", "06618", "06862", "07006", "07618", "07777",
              "09633", "09868", "09961", "02013", "06098", "03222", "03160",
              "09898", "09999", "01816", "02202", "06060", "02319"]


# ---------- 基础工具 ----------
def _retry(fn, *args, **kwargs):
    last = None
    for i in range(4):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last = e
            time.sleep(1.0 + 1.5 * i)
    raise last


def _col(df, *names, default=None):
    for n in names:
        if n in df.columns:
            return df[n]
    return default


def _sina_symbol(code):
    """东财裸代码 → 新浪带交易所前缀：60/68/51/56/58→sh，00/30/15→sz。"""
    return ("sh" if str(code).startswith(("6", "5")) else "sz") + str(code)


def _manifest_path():
    return path("data", "manifest.json")


def load_manifest():
    fp = _manifest_path()
    if os.path.exists(fp):
        try:
            with open(fp, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"index": {}, "stocks": {}, "etfs": {}, "funds": {},
            "meta": {"fails": {}, "complete": False}}


def save_manifest(m):
    with open(_manifest_path(), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)


# ---------- 标的清单（缓存7天） ----------
def _list_cache(fp):
    if os.path.exists(fp):
        if (time.time() - os.path.getmtime(fp)) / 86400 < 7:
            return pd.read_csv(fp, dtype={"code": str})
    return None


def _filter_stocks(df, code_col, name_col, cap_col):
    df = df[df[code_col].astype(str).str[:2].isin(CFG["universe"]["boards"])]
    if CFG["universe"]["exclude_st"]:
        df = df[~df[name_col].astype(str).str.upper().str.contains("ST|退", na=False)]
    cap = _col(df, cap_col, default=pd.Series(np.nan, index=df.index))
    out = pd.DataFrame({"code": df[code_col].astype(str),
                        "name": df[name_col].astype(str),
                        "mktcap": pd.to_numeric(cap, errors="coerce")})
    return out.sort_values("mktcap", ascending=False)


def _tencent_mktcaps(codes, batch=60):
    """腾讯批量行情取总市值（亿），仅用于标的池优先级排序。"""
    import requests
    caps = {}
    syms = [_sina_symbol(c) for c in codes]
    for i in range(0, len(syms), batch):
        try:
            r = requests.get("https://qt.gtimg.cn/q=" + ",".join(syms[i:i + batch]),
                             timeout=10)
            r.encoding = "gbk"
            for line in r.text.strip().split(";"):
                line = line.strip()
                if "=" not in line:
                    continue
                f = line.split("=", 1)[1].strip('"').split("~")
                if len(f) > 45:
                    try:
                        caps[str(f[2])] = float(f[45])  # [44]流通市值 [45]总市值(亿)
                    except ValueError:
                        pass
        except Exception:
            pass
        time.sleep(0.15)
    return caps


def stock_list(refresh=False):
    fp = path("data", "list_stocks.csv")
    if not refresh:
        cached = _list_cache(fp)
        if cached is not None:
            return cached
    if ak is None:
        raise RuntimeError("akshare 未安装")
    try:  # 东财快照（快，含总市值）
        df = ak.stock_zh_a_spot_em()
        out = _filter_stocks(df, "代码", "名称", "总市值")
    except Exception as e:
        print(f"[download] 东财股票快照失败({str(e)[:60]})，"
              f"改用沪深交易所官方清单+腾讯批量市值", flush=True)
        df = ak.stock_info_a_code_name()  # 交易所官方：code/name
        df = df[df["code"].astype(str).str[:2].isin(CFG["universe"]["boards"])]
        if CFG["universe"]["exclude_st"]:
            df = df[~df["name"].astype(str).str.upper().str.contains("ST|退", na=False)]
        caps = _tencent_mktcaps(df["code"].tolist())
        out = pd.DataFrame({"code": df["code"].astype(str),
                            "name": df["name"].astype(str)})
        out["mktcap"] = out["code"].map(caps)
        out = out.sort_values("mktcap", ascending=False)
    out.to_csv(fp, index=False, encoding="utf-8")
    return out


def etf_list(refresh=False):
    fp = path("data", "list_etfs.csv")
    if not refresh:
        cached = _list_cache(fp)
        if cached is not None:
            return cached
    try:  # 东财
        df = ak.fund_etf_spot_em()
        vol = _col(df, "成交量", "成交额", default=pd.Series(np.nan, index=df.index))
        out = pd.DataFrame({"code": _col(df, "代码", "基金代码").astype(str),
                            "name": _col(df, "名称", "基金简称").astype(str),
                            "turnover": pd.to_numeric(vol, errors="coerce")})
    except Exception as e:
        print(f"[download] 东财ETF快照失败({str(e)[:60]})，降级新浪ETF列表", flush=True)
        df = ak.fund_etf_category_sina(symbol="ETF基金")
        # 新浪：代码(sh510300)/名称/最新价/.../成交量/成交额
        vol = _col(df, "成交额", "成交量", default=pd.Series(np.nan, index=df.index))
        out = pd.DataFrame({"code": _col(df, "代码", "symbol").astype(str)
                            .str.replace("^(sh|sz)", "", regex=True),
                            "name": _col(df, "名称", "基金简称").astype(str),
                            "turnover": pd.to_numeric(vol, errors="coerce")})
    out = out.sort_values("turnover", ascending=False)
    out.to_csv(fp, index=False, encoding="utf-8")
    return out


def fund_list(refresh=False):
    fp = path("data", "list_funds.csv")
    if not refresh:
        cached = _list_cache(fp)
        if cached is not None:
            return cached
    df = ak.fund_open_fund_rank_em(symbol="全部")  # 仅东财提供
    out = pd.DataFrame({"code": _col(df, "基金代码", "代码").astype(str),
                        "name": _col(df, "基金简称", "名称").astype(str)})
    out.to_csv(fp, index=False, encoding="utf-8")
    return out


def us_list(refresh=False):
    fp = path("data", "list_us.csv")
    if not refresh and os.path.exists(fp):
        return pd.read_csv(fp, dtype={"code": str})
    out = pd.DataFrame({"code": US_TICKERS,
                        "name": US_TICKERS,
                        "mktcap": float("nan")})
    out.to_csv(fp, index=False, encoding="utf-8")
    return out


def hk_list(refresh=False):
    fp = path("data", "list_hk.csv")
    if not refresh and os.path.exists(fp):
        return pd.read_csv(fp, dtype={"code": str})
    out = pd.DataFrame({"code": HK_TICKERS,
                        "name": HK_TICKERS,
                        "mktcap": float("nan")})
    out.to_csv(fp, index=False, encoding="utf-8")
    return out


# ---------- 单标的下载（各源均返回全历史，本地增量合并） ----------
def _parquet(kind, code):
    return path("data", kind, f"{code}.parquet")


def _norm_hist(df):
    df = df.rename(columns=_HIST_COLS)
    df["date"] = pd.to_datetime(df["date"])
    for c in ("open", "high", "low", "close", "volume", "amount"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan
    return (df[["date", "open", "high", "low", "close", "volume", "amount"]]
            .dropna(subset=["close"]).drop_duplicates("date").sort_values("date"))


def _fetch_stock(code, start=None):
    """新浪日线（前复权全历史）。"""
    return _norm_hist(_retry(ak.stock_zh_a_daily, symbol=_sina_symbol(code),
                             adjust="qfq"))


def _fetch_etf(code, start=None):
    """新浪ETF日线（不复权，全历史）。"""
    return _norm_hist(_retry(ak.fund_etf_hist_sina, symbol=_sina_symbol(code)))


def _fetch_fund(code, start=None):
    """东财场外基金单位净值（东财恢复后可用）。"""
    df = _retry(ak.fund_open_fund_info_em, symbol=code, indicator="单位净值走势")
    df = pd.DataFrame({"date": pd.to_datetime(_col(df, "净值日期", "日期")),
                       "nav": pd.to_numeric(_col(df, "单位净值"), errors="coerce")})
    return df.dropna().drop_duplicates("date").sort_values("date")


def _fetch_fund_wrap(code, start=None):
    return _fetch_fund(code)


def _fetch_us(code, start=None):
    """新浪美股日线（前复权全历史）。"""
    df = _retry(ak.stock_us_daily, symbol=code, adjust="qfq")
    df["date"] = pd.to_datetime(df["date"])
    for c in ("open", "high", "low", "close", "volume"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan
    if "amount" not in df.columns:
        df["amount"] = np.nan
    return (df[["date", "open", "high", "low", "close", "volume", "amount"]]
            .dropna(subset=["close"]).drop_duplicates("date").sort_values("date"))


def _fetch_hk(code, start=None):
    """新浪港股日线（前复权全历史）。"""
    df = _retry(ak.stock_hk_daily, symbol=code, adjust="qfq")
    df["date"] = pd.to_datetime(df["date"])
    for c in ("open", "high", "low", "close", "volume", "amount"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan
    return (df[["date", "open", "high", "low", "close", "volume", "amount"]]
            .dropna(subset=["close"]).drop_duplicates("date").sort_values("date"))


def _fetch_index(symbol):
    """新浪指数日线（全历史）。A股直连；恒指/标普走各自接口。"""
    if symbol.startswith("hk_"):
        df = _retry(ak.stock_hk_index_daily_sina, symbol=symbol[3:])
    elif symbol.startswith("us_"):
        df = _retry(ak.index_us_stock_sina, symbol=symbol[3:])
    else:
        df = _retry(ak.stock_zh_index_daily, symbol=symbol)
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df[["date", "close"]].dropna().sort_values("date")


def update_one(kind, code, fetch, full_start="20050101"):
    """更新单个标的（全量拉取+增量合并），返回 ok/fresh/empty/fail。"""
    fp = _parquet(kind, code)
    old = None
    if os.path.exists(fp):
        old = pd.read_parquet(fp)
        if len(old):
            last = pd.to_datetime(old["date"].max())
            if last >= pd.Timestamp.today() - pd.Timedelta(days=3):
                return "fresh"
    df = fetch(code, full_start)
    if df is None or not len(df):
        return "ok" if (old is not None and len(old)) else "empty"
    if old is not None and len(old):
        df = pd.concat([old, df]).drop_duplicates("date", keep="last") \
            .sort_values("date")
    df.to_parquet(fp, index=False)
    return "ok"


def _safe_update(kind, code, fetch, sleep_s):
    time.sleep(sleep_s)
    try:
        return update_one(kind, code, fetch)
    except Exception:
        return "fail"


# ---------- 阶段下载 ----------
def _jobs_for(kind, codes, fetch, start="20050101"):
    return [(kind, str(c), fetch, start) for c in codes]


def run_download(stage="all", limit=None, workers=2, sleep_s=0.25):
    """下载历史数据。stage: index/core/etf/stocks/funds/all；断点续传。"""
    try:
        with open(path("state", "pids", "download.pid"), "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass
    m = load_manifest()
    m["meta"].setdefault("fails", {})

    def _run(jobs):
        if not jobs:
            return
        n_ok = n_fresh = n_empty = n_fail = 0
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            futs = {ex.submit(_safe_update, k, c, f, sleep_s): (k, c)
                    for k, c, f, s in jobs}
            for i, fut in enumerate(as_completed(futs), 1):
                kind, code = futs[fut]
                st = fut.result()
                m.setdefault(kind, {})[code] = st
                if st == "ok":
                    n_ok += 1
                elif st == "fresh":
                    n_fresh += 1
                elif st == "fail":
                    m["meta"]["fails"][f"{kind}:{code}"] = \
                        m["meta"]["fails"].get(f"{kind}:{code}", 0) + 1
                    n_fail += 1
                else:
                    n_empty += 1
                if i % 25 == 0 or i == len(futs):
                    save_manifest(m)
                    print(f"[download] {kind} {i}/{len(futs)} ok={n_ok} "
                          f"fresh={n_fresh} empty={n_empty} fail={n_fail}",
                          flush=True)
        save_manifest(m)

    if stage in ("all", "core", "index"):
        for sym in INDEX_SYMBOLS:
            try:
                df = _fetch_index(sym)
                df.to_parquet(path("data", "index", f"{sym}.parquet"), index=False)
                m["index"][sym] = "ok"
                print(f"[download] index {sym}: {len(df)} 行", flush=True)
            except Exception as e:
                m["index"][sym] = "fail"
                print(f"[download] index {sym} 失败: {str(e)[:100]}", flush=True)
        save_manifest(m)

    if stage in ("all", "core", "etf"):
        try:
            el = etf_list()
        except Exception as e:
            print(f"[download] ETF 清单获取失败: {str(e)[:100]}", flush=True)
            el = pd.DataFrame(columns=["code"])
        if stage == "core":
            codes = el["code"].head(40)
        else:
            codes = el["code"].head(limit or CFG["universe"]["etf_top_n"])
        _run(_jobs_for("etfs", codes, _fetch_etf))

    if stage in ("all", "core", "stocks"):
        try:
            sl = stock_list()
        except Exception as e:
            print(f"[download] 股票清单获取失败: {str(e)[:100]}", flush=True)
            sl = pd.DataFrame(columns=["code"])
        if stage == "core":
            codes = sl["code"].head(60)
        else:
            codes = sl["code"] if CFG["universe"].get("download_all_stocks", True) \
                else sl["code"].head(CFG["universe"]["max_stock_names"])
            if limit:
                codes = codes.head(limit)
        _run(_jobs_for("stocks", codes, _fetch_stock))

    if stage in ("all", "funds"):
        try:
            fl = fund_list()
            codes = fl["code"].head(limit or CFG["universe"]["fund_top_n"])
            _run(_jobs_for("funds", codes, _fetch_fund_wrap))
        except Exception as e:
            print(f"[download] 场外基金阶段失败(东财源暂不可达，稍后自动重试): "
                  f"{str(e)[:100]}", flush=True)

    if stage in ("all", "hk"):
        try:
            hl = hk_list()
            _run(_jobs_for("hk", hl["code"], _fetch_hk))
        except Exception as e:
            print(f"[download] 港股阶段失败: {str(e)[:100]}", flush=True)

    if stage in ("all", "us"):
        try:
            ul = us_list()
            _run(_jobs_for("us", ul["code"], _fetch_us))
        except Exception as e:
            print(f"[download] 美股阶段失败: {str(e)[:100]}", flush=True)

    if stage == "all":
        stocks_ok = sum(1 for v in m.get("stocks", {}).values()
                        if v in ("ok", "fresh"))
        etfs_ok = sum(1 for v in m.get("etfs", {}).values()
                      if v in ("ok", "fresh"))
        hk_ok = sum(1 for v in m.get("hk", {}).values() if v in ("ok", "fresh"))
        us_ok = sum(1 for v in m.get("us", {}).values() if v in ("ok", "fresh"))
        m["meta"]["complete"] = (stocks_ok >= 500 and etfs_ok >= 100
                                 and hk_ok >= 50 and us_ok >= 50)
    save_manifest(m)
    print(f"[download] 阶段 {stage} 完成 complete={m['meta'].get('complete')}",
          flush=True)


# ---------- 统计与面板 ----------
def data_stats():
    m = load_manifest()

    def cnt(kind):
        d = m.get(kind, {})
        return {"ok": sum(1 for v in d.values() if v in ("ok", "fresh")),
                "total": len(d),
                "fail": sum(1 for v in d.values() if v == "fail")}

    files = {}
    for k in ("stocks", "etfs", "funds", "index", "hk", "us"):
        d = path("data", k)
        files[k] = len(os.listdir(d)) if os.path.isdir(d) else 0
    return {"stocks": cnt("stocks"), "etfs": cnt("etfs"), "funds": cnt("funds"),
            "hk": cnt("hk"), "us": cnt("us"),
            "files": files, "complete": m["meta"].get("complete", False)}


def load_panel(kind="stocks", max_names=None, start=None, min_days=None,
               order_codes=None, want_volume=False):
    """收盘价面板（日期×标的，float32）；want_volume=True 同时返回成交量面板。

    返回 (close_panel, volume_panel)；volume_panel 不 ffill（停牌=NaN，热度因子
    需要真实停牌语义），与 close_panel 同索引同列序。基金无 volume，volume_panel 全 NaN。
    """
    max_names = max_names or CFG["universe"]["max_stock_names"]
    min_days = CFG["universe"]["min_history_days"] if min_days is None else min_days
    start = start or CFG["walk_forward"]["train_start"]
    codes = order_codes
    if codes is None:
        d = path("data", kind)
        codes = [f[:-8] for f in os.listdir(d) if f.endswith(".parquet")]
    series = {}
    vseries = {}
    val_col = "nav" if kind == "funds" else "close"
    want_vol = want_volume and kind != "funds"
    uni = CFG["universe"]
    junk_filter = kind == "stocks" and uni.get("exclude_long_suspension", True)
    for c in codes[:max_names]:
        fp = _parquet(kind, str(c))
        if not os.path.exists(fp):
            continue
        try:
            df = pd.read_parquet(fp, columns=["date", val_col]
                                 + (["volume"] if want_vol else []))
        except Exception:
            df = pd.read_parquet(fp, columns=["date", val_col])
        df = df.rename(columns={val_col: "close"})
        df = df[pd.to_datetime(df["date"]) >= pd.Timestamp(start)]
        if len(df) < min_days:
            continue
        if junk_filter:
            # 暴雷股典型形态过滤（用户纪律：不买暴雷/ST/退市边缘）：
            # 1) 历史自然日间隔 > max_gap_days ≈ 长期停牌（重组/暴雷/退市前兆）
            dates = pd.to_datetime(df["date"])
            gaps = dates.diff().dt.days
            if len(gaps) and pd.notna(gaps.max()) \
                    and gaps.max() > uni.get("max_gap_natural_days", 120):
                continue
            # 2) 数据终点距今 > stale_days = 当前停牌/退市边缘
            if (pd.Timestamp.today() - dates.max()).days \
                    > uni.get("stale_days", 90):
                continue
        idx = pd.DatetimeIndex(pd.to_datetime(df["date"]))
        keep = ~pd.Series(idx).duplicated().values
        s = pd.Series(df["close"].astype("float32").values, index=idx)
        series[str(c)] = s[keep]
        if want_volume:
            if "volume" in df.columns:
                v = pd.Series(pd.to_numeric(df["volume"], errors="coerce")
                              .astype("float32").values, index=idx)[keep]
            else:
                v = pd.Series(np.nan, index=idx[keep])
            vseries[str(c)] = v
    if not series:
        return (pd.DataFrame(), pd.DataFrame()) if want_volume else pd.DataFrame()
    panel = pd.DataFrame(series).sort_index().ffill(limit=10).astype("float32")
    if not want_volume:
        return panel
    vpanel = pd.DataFrame(vseries).sort_index()
    vpanel = vpanel.reindex(columns=panel.columns).reindex(panel.index)
    return panel, vpanel.astype("float32")


def load_order_codes():
    fp = path("data", "list_stocks.csv")
    if os.path.exists(fp):
        return pd.read_csv(fp, dtype={"code": str})["code"].tolist()
    return None


def load_benchmark(symbol=None):
    symbol = symbol or CFG["benchmark"]
    df = pd.read_parquet(path("data", "index", f"{symbol}.parquet"))
    s = pd.Series(df["close"].astype("float32").values,
                  index=pd.DatetimeIndex(pd.to_datetime(df["date"])))
    return s[~s.index.duplicated()].sort_index()
