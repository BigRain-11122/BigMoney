"""舆论/负面事件因子（用户纪律 2026-09-19：大面积负面报道=走人）。

数据源：东财全市场公告（ak.stock_notice_report，按日回溯）→ 本地负面关键词过滤。
事件 = 立案/行政处罚/退市风险提示/警示函/资金占用/失信/债务逾期等硬负面公告
（新闻大面积负面报道通常滞后于公告，公告是更早更硬的信号）。

两个层面：
1) 回测层：负面事件后 N 交易日禁持该股（negday 矩阵，进化学习 N）
2) 决策层：paper 出持仓时，近 7 天有负面公告的持仓直接剔除
仅模拟研究。
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

try:
    import akshare as ak
except Exception:
    ak = None

from .config import path, ensure_dirs
from . import data as D

NEG_KW = ["立案", "行政处罚", "处罚决定", "退市风险", "终止上市", "警示函",
          "监管函", "资金占用", "占用资金", "失信", "债务逾期", "违规",
          "冻结", "立案调查", "问询函"]

_EVENTS_FP = None


def events_fp():
    global _EVENTS_FP
    if _EVENTS_FP is None:
        os.makedirs(path("data", "events"), exist_ok=True)
        _EVENTS_FP = path("data", "events", "negative_events.parquet")
    return _EVENTS_FP


def load_events():
    fp = events_fp()
    if not os.path.exists(fp):
        return None
    try:
        df = pd.read_parquet(fp)
        return df if len(df) else None
    except Exception:
        return None


def recent_negative_codes(days=7):
    """近 N 自然日内有负面公告的股票: {code: '标题;标题'}（决策层否决用）。"""
    ev = load_events()
    if ev is None:
        return {}
    cut = pd.Timestamp.today() - pd.Timedelta(days=days)
    m = pd.to_datetime(ev["date"]) >= cut
    if not m.any():
        return {}
    recent = ev[m]
    out = {}
    for code, grp in recent.groupby("code"):
        out[str(code)] = ";".join(grp["title"].astype(str).head(3))
    return out


def _norm_code(s):
    s = str(s)
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits[-6:] if len(digits) >= 6 else digits


# ---------- 热度（关注度）快照：雪球全市场关注榜，每日自建历史 ----------
def _hot_dir():
    d = path("data", "events", "hot_rank")
    os.makedirs(d, exist_ok=True)
    return d


def fetch_hot_snapshot():
    """采集当日雪球全市场关注热度快照（自建历史，供日后热度因子回测与决策展示）。"""
    rows = []
    try:
        df = D._retry(ak.stock_hot_follow_xq, symbol="最热门")
        code_col = next((c for c in ("股票代码", "代码", "symbol") if c in df.columns), None)
        hot_col = next((c for c in ("热度", "热门度") if c in df.columns), None)
        fol_col = next((c for c in ("关注", "关注数", "粉丝数") if c in df.columns), None)
        if code_col is not None and hot_col is not None:
            for _, r in df.iterrows():
                code = _norm_code(r[code_col])
                if len(code) == 6:
                    rows.append({
                        "code": code,
                        "hot": float(pd.to_numeric(r[hot_col], errors="coerce") or 0),
                        "followers": (float(pd.to_numeric(r[fol_col], errors="coerce") or 0)
                                      if fol_col is not None else 0.0),
                    })
    except Exception as e:
        print(f"[hotrank] 雪球关注榜采集失败: {str(e)[:100]}", flush=True)
        return 0
    if not rows:
        print("[hotrank] 无数据", flush=True)
        return 0
    today = pd.Timestamp.today().strftime("%Y%m%d")
    fp = os.path.join(_hot_dir(), f"hot_{today}.parquet")
    pd.DataFrame(rows).drop_duplicates("code").to_parquet(fp, index=False)
    print(f"[hotrank] 快照入库: {len(rows)} 只 -> {os.path.basename(fp)}", flush=True)
    return len(rows)


def latest_hot_rank():
    """最新一份热度快照: {code: hot}。"""
    d = _hot_dir()
    try:
        files = sorted(f for f in os.listdir(d) if f.endswith(".parquet"))
    except Exception:
        return {}
    if not files:
        return {}
    try:
        df = pd.read_parquet(os.path.join(d, files[-1]))
        return dict(zip(df["code"].astype(str), df["hot"].astype(float)))
    except Exception:
        return {}


def _fetch_day(d):
    """拉取某交易日的全市场公告并过滤负面事件。"""
    if ak is None:
        return []
    for attempt in range(2):
        try:
            df = ak.stock_notice_report(symbol="全部", date=d.strftime("%Y%m%d"))
            break
        except Exception:
            time.sleep(1.0 + attempt)
    else:
        return []
    if df is None or not len(df):
        return []
    title_col = None
    code_col = None
    for c in ("公告标题", "标题", "公告名称"):
        if c in df.columns:
            title_col = c
            break
    for c in ("公告代码", "代码"):
        if c in df.columns:
            code_col = c
            break
    if title_col is None or code_col is None:
        return []
    titles = df[title_col].astype(str)
    pat = "|".join(NEG_KW)
    hits = df[titles.str.contains(pat, na=False)]
    rows = []
    for _, r in hits.iterrows():
        code = _norm_code(r[code_col])
        if len(code) == 6:
            rows.append({"date": d, "code": code,
                         "title": str(r[title_col])[:80]})
    return rows


def fetch_events(trading_days=700, workers=3):
    """按交易日逐日拉公告、过滤负面事件、增量合并去重入库。"""
    if ak is None:
        print("[events] akshare 不可用", flush=True)
        return None
    bench = D.load_benchmark()  # 用指数日期做交易日历
    days = [d for d in bench.index
            if d <= pd.Timestamp.today()][-int(trading_days):]
    if not days:
        print("[events] 无交易日可拉取", flush=True)
        return None
    print(f"[events] 拉取 {days[0].date()}~{days[-1].date()} 共 {len(days)} 个交易日公告",
          flush=True)
    rows = []
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(_fetch_day, d): d for d in days}
        for fut in as_completed(futs):
            try:
                rows.extend(fut.result())
            except Exception:
                pass
            done += 1
            if done % 50 == 0 or done == len(futs):
                print(f"[events] 进度 {done}/{len(futs)} 累计负面事件 {len(rows)}",
                      flush=True)
    new = pd.DataFrame(rows)
    if not len(new):
        print("[events] 本窗口未发现负面事件", flush=True)
        return load_events()
    old = load_events()
    if old is not None and len(old):
        both = pd.concat([old, new])
    else:
        both = new
    both["date"] = pd.to_datetime(both["date"])
    both = both.drop_duplicates(subset=["date", "code", "title"]) \
        .sort_values("date")
    both.to_parquet(events_fp(), index=False)
    print(f"[events] 入库完成：{len(both)} 条负面事件 "
          f"({both['date'].min().date()}~{both['date'].max().date()})",
          flush=True)
    return both
