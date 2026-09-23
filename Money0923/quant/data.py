"""数据层：多数据源自动切换 + CSV 缓存 + 增量更新。

实测本网络环境下的可用性（2026-09 验证）：
- 交易日历：sina tool_trade_date_hist_sina ✔
- 股票日线：新浪 stock_zh_a_daily ✔（东财 push2 接口断连 → 自动降级新浪）
- ETF 日线：东财 fund_etf_hist_em ✔
- 股票快照：新浪 stock_zh_a_spot ✔（含昨收，用于盘中撮合与涨跌停判定）
- ETF 快照：东财 fund_etf_spot_em ✔
- 股票池：中证指数沪深300成分 ∩ 成交额Top（csindex ✔，失败则纯成交额筛选）

universe.csv：高流动性主板股票（60只）+ ETF池（20只）
data/daily/{code}.csv：前复权日线（增量追加）
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import clock
from .config import AppConfig, DAILY_DIR, DATA_DIR, ensure_dirs

log = logging.getLogger("quant.data")

UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.csv")

# ETF 代码前缀（沪：510/511/512/513/515/516/517/518/560/561/562/563/588；深：159）
_ETF_PREFIX = ("510", "511", "512", "513", "515", "516", "517", "518",
               "560", "561", "562", "563", "588", "159")


def is_etf(code: str) -> bool:
    return len(code) == 6 and code.startswith(_ETF_PREFIX)


# 货币/理财类ETF黑名单（近端分钟数据验证发现：511880银华日利/511990华宝添益等
# 名称不含"货币"但本质是货币基金，无波动收益，会被低波动因子误选入组合）
_MONEY_ETF_CODES = {"511880", "511990", "511620", "511660", "511680", "511700",
                    "511760", "511810", "511830", "511860", "511870", "511900",
                    "511910", "511920", "511930", "511950", "511970", "159972"}
_MONEY_ETF_NAME_KEYS = ("货币", "日利", "添益", "理财", "现金")


def is_money_etf(code: str, name: str = "") -> bool:
    """货币/理财类ETF（无交易价值，永不入池）。"""
    if code in _MONEY_ETF_CODES:
        return True
    return any(k in (name or "") for k in _MONEY_ETF_NAME_KEYS)


# T+0 回转交易品种（交易所规定）：跨境ETF/债券ETF/黄金ETF/商品ETF 当日买当日可卖；
# A股股票型ETF与全部股票为 T+1。沪市前缀可靠覆盖：511(债券)/513(跨境)/518(黄金)；
# 深市跨境/商品类按名称关键词注册（黄金股ETF为A股股票型，须排除）。
_T0_PREFIX = ("511", "513", "518")
_T0_NAME_KEYS = ("恒生", "纳指", "纳斯达克", "标普", "香港", "港股", "中概", "海外", "美国",
                 "日经", "印度", "德国", "法国", "沙特", "东南亚", "亚太", "亚洲", "全球",
                 "黄金", "豆粕", "饲料", "能源化工", "有色", "商品", "债")
_T0_REGISTRY: set[str] = set()


def register_t0_names(uni: pd.DataFrame) -> None:
    """按 universe 名称注册深市跨境/商品类 T+0 品种（沪市前缀已覆盖，无需注册）。"""
    for _, r in uni.iterrows():
        c, name = str(r.get("code", "")), str(r.get("name", ""))
        if not is_etf(c) or c.startswith(_T0_PREFIX):
            continue
        if "黄金股" in name:
            continue  # 黄金股ETF=A股股票型，T+1
        if any(k in name for k in _T0_NAME_KEYS):
            _T0_REGISTRY.add(c)


def is_t0(code: str) -> bool:
    """T+0 回转品种（当日买当日可卖）：跨境/债券/黄金/商品ETF。"""
    if code in _T0_REGISTRY:
        return True
    return len(code) == 6 and code.startswith(_T0_PREFIX)


def max_order_shares(code: str) -> int:
    """单笔申报数量上限（交易所规则）：创业板股票≤30万股，主板股票≤100万股，基金≤100万份。"""
    if is_etf(code):
        return 1_000_000
    if code.startswith("30"):
        return 300_000
    return 1_000_000


def limit_up_pct(code: str) -> float:
    """涨跌幅限制：创业板/科创板股票与588科创ETF为20%，主板与普通ETF为10%。
    注意：创业板ETF等 20% 品种由 validation.effective_limit 数据推断后修正，撮合层须用后者。"""
    if code.startswith(("30", "68")) or code.startswith("588"):
        return 0.20
    return 0.10


def _col(df: pd.DataFrame, *names: str) -> pd.Series:
    for n in names:
        if n in df.columns:
            return df[n]
    raise KeyError(f"列 {names} 不存在，实际列: {list(df.columns)[:25]}")


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _retry_call(fn, tries: int = 3, wait: float = 2.0):
    last: Exception | None = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 网络抖动需容忍
            last = e
            time.sleep(wait * (i + 1))
    raise RuntimeError(f"重试{tries}次仍失败: {last}") from last


def _sina_symbol(code: str) -> str:
    """6/51/56/58 开头为沪市（含588科创ETF），00/30/15/159 为深市。"""
    if code.startswith(("6", "51", "56", "58")):
        return "sh" + code
    return "sz" + code


# ---------------------------------------------------------------- universe

# 备用ETF清单（东财快照失败时兜底，均为高流动性主流品种）
_DEFAULT_ETFS = [
    ("510300", "沪深300ETF"), ("510500", "中证500ETF"), ("512100", "中证1000ETF"),
    ("588000", "科创50ETF"), ("159915", "创业板ETF"), ("159949", "创业板50"),
    ("512880", "证券ETF"), ("512690", "酒ETF"), ("512480", "半导体ETF"),
    ("512660", "军工ETF"), ("512800", "银行ETF"), ("512010", "医药ETF"),
    ("515790", "光伏ETF"), ("515030", "新能源车ETF"), ("518880", "黄金ETF"),
    ("510880", "红利ETF"), ("513100", "纳指ETF"), ("513500", "标普500ETF"),
    ("159920", "恒生ETF"), ("511010", "国债ETF"),
]


def _apply_negative_screen(cfg: AppConfig, df: pd.DataFrame) -> pd.DataFrame:
    """负面清单过滤（亏损/暴雷/共识衰亡行业/黑名单），失败时降级放行不阻塞。"""
    if not getattr(cfg, "fundamental", None) or not cfg.fundamental.enabled or not len(df):
        return df
    try:
        from . import fundamental
        names = dict(zip(df["code"], df["name"]))
        excl = fundamental.build_exclusions(cfg, df["code"].tolist(), names)
        if excl:
            sample = "; ".join(f"{c}({r[:10]})" for c, r in list(excl.items())[:8])
            log.info("负面清单剔除 %d/%d 只: %s%s", len(excl), len(df), sample,
                     "..." if len(excl) > 8 else "")
            return df[~df["code"].isin(excl)]
        return df
    except Exception as e:  # noqa: BLE001
        log.warning("负面清单过滤异常（本批跳过）: %s", e)
        return df


def _load_universe_cache(cfg: AppConfig) -> pd.DataFrame:
    """只读股票池（零网络）：盘中伴生联赛用；缓存不存在则报错（不静默联网）。"""
    if not os.path.exists(UNIVERSE_FILE):
        raise RuntimeError("universe.csv 缺失：请先跑 run.py init 建立本地缓存")
    uni = pd.read_csv(UNIVERSE_FILE, dtype={"code": str})
    register_t0_names(uni)
    return uni


def update_universe(cfg: AppConfig, force: bool = False) -> pd.DataFrame:
    """刷新股票池（当日已有缓存则直接用）。

    股票：沪深300成分按权重取Top（csindex 权重表，单请求稳定；
          成分口径为上月末，属"近似时点"选择，对日频轮动影响可忽略）
    ETF：东财快照按成交额取Top，失败则用内置主流清单兜底
    """
    if not force and os.path.exists(UNIVERSE_FILE):
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(UNIVERSE_FILE))
        if mtime.date() == dt.date.today():
            uni = pd.read_csv(UNIVERSE_FILE, dtype={"code": str})
            register_t0_names(uni)
            return uni

    import akshare as ak

    # ---- 股票：沪深300 ∩ 权重Top
    stocks = None
    try:
        c = _retry_call(lambda: ak.index_stock_cons_weight_csindex(symbol="000300"))
        df = pd.DataFrame({
            "code": c["成分券代码"].astype(str).str.zfill(6),
            "name": c["成分券名称"].astype(str),
            "weight": pd.to_numeric(c["权重"], errors="coerce"),
        })
        df = df[~df["name"].str.contains("ST|退", na=False)]
        df = df[~df["code"].str.startswith("68")]  # 剔除科创板（200股起报单，规则不同）
        ranked = df.sort_values("weight", ascending=False)
        ranked = _apply_negative_screen(cfg, ranked)   # 负面清单：亏损/暴雷/行业/黑名单
        stocks = ranked.head(cfg.universe.stock_universe_size)[["code", "name", "weight"]]
        log.info("股票池: 沪深300权重Top %d 只（负面清单过滤后）", len(stocks))
    except Exception as e:  # noqa: BLE001
        log.warning("沪深300权重表失败: %s，退化为成分列表", e)
        try:
            c = _retry_call(lambda: ak.index_stock_cons_csindex(symbol="000300"), tries=2)
            df = pd.DataFrame({"code": c["成分券代码"].astype(str).str.zfill(6),
                               "name": c["成分券名称"].astype(str)})
            df = df[~df["name"].str.contains("ST|退", na=False)]
            stocks = df.head(cfg.universe.stock_universe_size)
        except Exception as e2:  # noqa: BLE001
            log.error("csindex成分也失败: %s", e2)
    if stocks is None and os.path.exists(UNIVERSE_FILE):
        old = pd.read_csv(UNIVERSE_FILE, dtype={"code": str})
        stocks = old[old["kind"] == "stock"][["code", "name"]]
        log.warning("股票数据源全部失败，沿用旧股票池 %d 只", len(stocks))
    if stocks is None or not len(stocks):
        raise RuntimeError("股票池数据源全部失败且无缓存")

    # ---- 小市值端：中证1000 权重最小40只（小市值策略族标的池；2×滑点成本分档保诚实）
    smalls = None
    try:
        c = _retry_call(lambda: ak.index_stock_cons_weight_csindex(symbol="000852"), tries=2)
        df = pd.DataFrame({
            "code": c["成分券代码"].astype(str).str.zfill(6),
            "name": c["成分券名称"].astype(str),
            "weight": pd.to_numeric(c["权重"], errors="coerce"),
        })
        big = set(stocks["code"]) if stocks is not None else set()
        df = df[(~df["name"].str.contains("ST|退", na=False))
                & (~df["code"].str.startswith("68"))
                & df["code"].str.startswith(("00", "60", "30"))
                & (~df["code"].isin(big))]
        # 中证1000 权重升序 ≈ 市值升序：负面清单过滤后取最小 40 只
        ranked = df.sort_values("weight", ascending=True)
        ranked = _apply_negative_screen(cfg, ranked)
        smalls = ranked.head(cfg.universe.small_universe_size)[["code", "name"]]
        log.info("小市值端: 中证1000权重最小 %d 只（负面清单过滤后）", len(smalls))
    except Exception as e:  # noqa: BLE001
        log.warning("中证1000权重表失败（小市值端本批跳过）: %s", e)
    if smalls is None or not len(smalls):
        smalls = pd.DataFrame(columns=["code", "name"])

    # ---- ETF：东财快照成交额Top
    etfs = None
    try:
        etf_spot = _retry_call(ak.fund_etf_spot_em, tries=2)
        edf = pd.DataFrame({
            "code": _col(etf_spot, "代码").astype(str).str.zfill(6),
            "name": _col(etf_spot, "名称").astype(str),
            "price": _num(_col(etf_spot, "最新价")),
            "amount": _num(_col(etf_spot, "成交额")),
        })
        etfs = edf[edf["code"].apply(is_etf)
                   & ~edf.apply(lambda r: is_money_etf(r["code"], r["name"]), axis=1)  # 剔除货币/理财ETF
                   & edf["price"].between(0.3, 300.0)               # 放宽上限以纳入债券/黄金类ETF
                   & edf["amount"].notna() & (edf["amount"] > 0)
                   ].sort_values("amount", ascending=False).head(cfg.universe.etf_universe_size * 2)[["code", "name"]]
        etfs = _apply_negative_screen(cfg, etfs).head(cfg.universe.etf_universe_size)  # 行业ETF同受负面清单约束
    except Exception as e:  # noqa: BLE001
        log.warning("东财ETF快照失败: %s，使用内置ETF清单", e)
    if etfs is None or not len(etfs):
        etfs = pd.DataFrame(_DEFAULT_ETFS[: cfg.universe.etf_universe_size], columns=["code", "name"])

    out = pd.concat([
        stocks.assign(kind="stock", slip_mult=1.0),
        smalls.assign(kind="small", slip_mult=2.0),
        etfs.assign(kind="etf", slip_mult=1.0),
    ], ignore_index=True)[["code", "name", "kind", "slip_mult"]]
    ensure_dirs()
    out.to_csv(UNIVERSE_FILE, index=False)
    register_t0_names(out)
    log.info("股票池已刷新: %d 大盘 + %d 小市值 + %d 只ETF", len(stocks), len(smalls), len(etfs))
    return out


def load_universe() -> pd.DataFrame:
    if not os.path.exists(UNIVERSE_FILE):
        raise FileNotFoundError("universe.csv 不存在，请先运行 run.py init")
    uni = pd.read_csv(UNIVERSE_FILE, dtype={"code": str})
    register_t0_names(uni)
    return uni


def load_slip_mult() -> dict[str, float]:
    """code → 滑点成本倍数（小市值=2.0，其余=1.0；universe 无该列时全 1.0）。"""
    try:
        uni = load_universe()
        if "slip_mult" in uni.columns:
            m = pd.to_numeric(uni["slip_mult"], errors="coerce").fillna(1.0)
            return {str(c): float(v) for c, v in zip(uni["code"], m)}
    except Exception:  # noqa: BLE001
        pass
    return {}


# ---------------------------------------------------------------- daily bars

_EM_HIST_COLS = {"日期": "date", "开盘": "open", "收盘": "close", "最高": "high",
                 "最低": "low", "成交量": "volume", "成交额": "amount"}
_TX_FAIL_UNTIL = 0.0  # 腾讯日线源熔断时间戳（挂起/失败后10分钟内跳过，防连环20s超时拖垮日更块）
_STD_COLS = ["date", "open", "high", "low", "close", "volume", "amount"]


def _standardize(raw: pd.DataFrame, from_em: bool) -> pd.DataFrame:
    if from_em:
        raw = raw.rename(columns=_EM_HIST_COLS)
    keep = [c for c in _STD_COLS if c in raw.columns]
    df = raw[keep].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    for c in keep[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # 无成交额列（新浪ETF源）时用 volume×close 近似
    if "amount" not in df.columns and "volume" in df.columns:
        df["amount"] = df["volume"] * df["close"]
    return df


def _fetch_hist(code: str, start: str, end: str) -> pd.DataFrame:
    """股票：新浪源优先（东财接口在本网络断连，留作备选）；ETF：四级源链。

    ETF 源链（2026-09-21 实测教训）：①新浪**股票**端点 stock_zh_a_daily——
    基金端点 fund_etf_hist_sina 冻结在 09-18 三日不更（30只ETF齐冻结），而
    股票端点逐bar数值与既有缓存一致（同不复权基准）且尊重 start/end；
    ②腾讯 stock_zh_a_hist_tx——不同宿主，新浪限流时仍可用（当日实测含
    当日K线且数值一致）；③新浪基金端点（冻结但全史可去重合并兜底）；
    ④东财 qfq（断连+复权基准不同→接缝检测触发全量重拉改基准，污染清除
    机制自动联动清缓存）。
    """
    import akshare as ak
    import socket
    socket.setdefaulttimeout(20)  # akshare 各源无内置超时（实测腾讯级可挂起5分钟+）
    if is_etf(code):
        try:
            raw = _retry_call(lambda: ak.stock_zh_a_daily(
                symbol=_sina_symbol(code), start_date=start, end_date=end), tries=2)
            if raw is not None and len(raw):
                return _standardize(raw, from_em=False)
        except Exception as e:  # noqa: BLE001
            log.debug("ETF股票端点失败 %s: %s，转腾讯", code, e)
        # 腾讯日线兜底（不同宿主，新浪限流时仍可用；2026-09-21 20:30 实测
        # 含当日K线且数值与新浪逐bar一致=同基准可无缝续接）。tx 返回列中
        # amount=成交量(手)：重映射为 volume(股)，成交额由 _standardize 按
        # volume×close 近似补齐（与基金端点缓存口径一致）。带熔断：该端点
        # 实测会挂起（无超时+失败连环=30只×40秒拖垮日更块），失败后10分钟
        # 内不再尝试。
        global _TX_FAIL_UNTIL
        if time.time() >= _TX_FAIL_UNTIL:
            try:
                raw = _retry_call(lambda: ak.stock_zh_a_hist_tx(
                    symbol=_sina_symbol(code), start_date=start, end_date=end), tries=2)
                if raw is not None and len(raw):
                    raw = raw.rename(columns={"amount": "volume"})
                    raw["volume"] = pd.to_numeric(raw["volume"], errors="coerce") * 100
                    return _standardize(raw, from_em=False)
            except Exception as e:  # noqa: BLE001
                _TX_FAIL_UNTIL = time.time() + 600
                log.debug("ETF腾讯源失败/挂起 %s: %s →熔断10分钟", code, e)
        try:
            raw = _retry_call(lambda: ak.fund_etf_hist_sina(symbol=_sina_symbol(code)), tries=2)
            return _standardize(raw, from_em=False)
        except Exception as e:  # noqa: BLE001
            log.debug("ETF新浪基金源失败 %s: %s，转东财", code, e)
            raw = _retry_call(lambda: ak.fund_etf_hist_em(
                symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq"), tries=2)
            return _standardize(raw, from_em=True)
    try:
        raw = _retry_call(lambda: ak.stock_zh_a_daily(
            symbol=_sina_symbol(code), start_date=start, end_date=end, adjust="qfq"), tries=2)
        return _standardize(raw, from_em=False)
    except Exception as e:  # noqa: BLE001
        log.debug("股票新浪源失败 %s: %s，转东财", code, e)
        raw = _retry_call(lambda: ak.stock_zh_a_hist(
            symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq"), tries=2)
        return _standardize(raw, from_em=True)


def _daily_path(code: str) -> str:
    return os.path.join(DAILY_DIR, f"{code}.csv")


_META_DIR = os.path.join(DATA_DIR, "daily_meta")
_FULL_REFRESH_DAYS = 7  # qfq复权基准每周全量重拉一次

# ---------------------------------------------------------------- 数据纪元（污染清除机制）
# 用户红线（2026-09-21）："错误的训练数据及时清空，发现以后，不要污染我的模型"。
# 数据纪元=数据内容版本号（stock/futures 两域独立）：历史被重写（周全量重拉/
# 拼接缝重拉/校验发现修正/期货日更重拼接）时 bump 对应域纪元 →
#   ① eval_cache 旧分清除（evolve 按纪元行清除，详见 _purge_stale_cache）；
#   ② 联赛实战证据按事件类型清除（arena._purge_polluted_evidence：
#      校验发现类=错误数据上挣的证据/认证不可留；例行重写类=只清缓存分）。
# 增量追加（只加尾部新K线，不改历史）不 bump——已知有界近似：当天窗口触及
# 新增尾K的少量缓存条目会陈旧数小时，面板末日推进后键自然翻新自愈；若按日
# bump 则缓存每日全清=机制作废（本纪元只管"历史被改写"这一硬污染）。
DATA_EPOCH_FILE = os.path.join(DATA_DIR, "data_epoch.json")


def data_epoch() -> dict:
    """当前数据纪元：{"stock": n, "futures": n, "reason_stock": str,
    "reason_futures": str, "time": str}。文件缺失=纪元0（首次运行）。"""
    try:
        with open(DATA_EPOCH_FILE, encoding="utf-8") as f:
            e = json.load(f)
        return {"stock": int(e.get("stock", 0)), "futures": int(e.get("futures", 0)),
                "reason_stock": str(e.get("reason_stock", "")),
                "reason_futures": str(e.get("reason_futures", "")),
                "time": str(e.get("time", ""))}
    except Exception:  # noqa: BLE001
        return {"stock": 0, "futures": 0, "reason_stock": "",
                "reason_futures": "", "time": ""}


def bump_data_epoch(domain: str, reason: str) -> None:
    """历史重写/发现坏数据时升对应域纪元（domain: stock|futures）。原子写防半截。

    并发 bump 丢失一次计数无害——纪元只须"变化"，不须精确计数。"""
    e = data_epoch()
    e[domain] = int(e.get(domain, 0)) + 1
    e[f"reason_{domain}"] = str(reason)
    e["time"] = dt.datetime.now().isoformat(timespec="seconds")
    ensure_dirs()
    tmp = DATA_EPOCH_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False)
    os.replace(tmp, DATA_EPOCH_FILE)
    log.warning("【污染清除】数据纪元 %s→%d（%s）——旧数据上算出的分数/证据将失效重算",
                domain, e[domain], reason)


def _full_pull_due(code: str, today: dt.date) -> bool:
    """距上次全量重拉≥7天则重拉（qfq 前复权基准随除权漂移，增量拼接会产生假跳空）。"""
    os.makedirs(_META_DIR, exist_ok=True)
    stamp = os.path.join(_META_DIR, f"{code}.txt")
    if not os.path.exists(stamp):
        return True
    try:
        last = dt.date.fromisoformat(open(stamp, encoding="utf-8").read().strip())
        return (today - last).days >= _FULL_REFRESH_DAYS
    except Exception:  # noqa: BLE001
        return True


def _mark_full_pull(code: str) -> None:
    os.makedirs(_META_DIR, exist_ok=True)
    with open(os.path.join(_META_DIR, f"{code}.txt"), "w", encoding="utf-8") as f:
        f.write(dt.date.today().isoformat())


def _horizon_file() -> str:
    return os.path.join(_META_DIR, "_horizon_pending.json")


def _horizon_pending(all_codes: list, default_start: str) -> set:
    """下载口径（history_years→default_start）变更 → 待整段重拉集合。

    此前口径变更不会触发已 stamp 的代码重拉（增量更新只补尾部、stamp 新鲜
    则跳过），历史永远停在旧口径——扩历史（2026-09-21 3.5→25年）必须强制
    整段重拉一次。自愈式：成功一只移除一只，失败（限流/断连）留在集合里
    下次运行重试；集合空=扩史完成，文件留痕。"""
    try:
        with open(_horizon_file(), encoding="utf-8") as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        data = None
    if not isinstance(data, dict) or data.get("start") != default_start:
        data = {"start": default_start, "codes": list(all_codes)}
        os.makedirs(_META_DIR, exist_ok=True)
        tmp = _horizon_file() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, _horizon_file())
    return {c for c in (data.get("codes") or []) if c}


def _save_horizon_pending(default_start: str, pending: set) -> None:
    os.makedirs(_META_DIR, exist_ok=True)
    tmp = _horizon_file() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"start": default_start, "codes": sorted(pending)}, f, ensure_ascii=False)
    os.replace(tmp, _horizon_file())


def _same_hist(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    """两段日线内容是否一致（污染清除判定：内容未变=未发生历史重写）。

    行数、日期序列、全部数值列逐一比对；只要任何一根K线不同即视为重写。"""
    if a is None or b is None or len(a) != len(b):
        return False
    if a["date"].astype(str).tolist() != b["date"].astype(str).tolist():
        return False
    for c in ("open", "high", "low", "close", "volume", "amount"):
        if c not in a.columns or c not in b.columns:
            continue
        x = pd.to_numeric(a[c], errors="coerce").fillna(-1.0)
        y = pd.to_numeric(b[c], errors="coerce").fillna(-1.0)
        if not np.allclose(x, y, rtol=0.0, atol=1e-6):
            return False
    return True


def update_daily(cfg: AppConfig, codes: list[str] | None = None) -> list[str]:
    """增量更新日线缓存，返回本次有更新的代码列表。

    qfq 增量拼接防护（微观结构专家审查P0）：前复权基准随除权变化，
    ① 每周全量重拉 ② 拼接缝异常(>±5.5%)时立即全量重拉 ③ 换数据源口径差异同样触发重拉。
    """
    ensure_dirs()
    uni = load_universe()
    all_codes = codes or uni["code"].tolist()

    today = dt.date.today()
    # 当日收盘后（15:30 后）数据才完整；否则以昨收为终点
    if dt.datetime.now().time() >= dt.time(15, 30):
        try:
            end_date = clock.last_trade_date(today).strftime("%Y%m%d")
        except Exception:  # noqa: BLE001
            end_date = (today - dt.timedelta(days=1)).strftime("%Y%m%d")
    else:
        end_date = clock.last_trade_date(today - dt.timedelta(days=1)).strftime("%Y%m%d")

    updated: list[str] = []
    full_pulled: list[str] = []
    lagging: list[tuple[str, str]] = []
    default_start = (today - dt.timedelta(days=int(cfg.universe.history_years * 366))).strftime("%Y%m%d")
    horizon_pending = _horizon_pending(all_codes, default_start)
    for code in all_codes:
        path = _daily_path(code)
        start = default_start
        full_pull = True
        cached_last_close = None
        prev_df = None  # 旧缓存内容（污染清除判定：内容未变的重拉≠历史重写）
        if os.path.exists(path):
            try:
                cached = pd.read_csv(path, dtype={"date": str})
                prev_df = cached
                if len(cached):
                    last = str(cached["date"].iloc[-1]).replace("-", "")
                    # 先判全量重拉（数据最新也须周期性重拉防qfq拼接假跳空）；
                    # 下载口径变更（扩史）同样强制整段重拉
                    full_pull = _full_pull_due(code, today) or code in horizon_pending
                    if last >= end_date and not full_pull:
                        continue
                    if last >= end_date:
                        start = default_start  # 数据最新但到全量重拉周期：整段重拉
                    else:
                        cached_last_close = float(cached["close"].iloc[-1])
                        if not full_pull:
                            start = (pd.Timestamp(str(cached["date"].iloc[-1]))
                                     + pd.Timedelta(days=1)).strftime("%Y%m%d")
            except Exception:  # noqa: BLE001 缓存损坏则重拉
                full_pull = True
        try:
            new = _fetch_hist(code, start, end_date)
        except Exception as e:  # noqa: BLE001
            log.warning("下载失败 %s: %s", code, e)
            continue
        if new is None or not len(new):
            continue
        # 拼接缝异常检测：新旧片段接缝跳空超±5.5%（除权重估/换源口径）→ 全量重拉。
        # 守卫（2026-09-21 实测教训）：接缝检测只对"增量语义"有效——返回首根
        # K线必须在缓存末根**之后**（源尊重 start 参数）。fund_etf_hist_sina 等
        # 忽略 start 返回全史的源，首根是数年前K线，拿它与昨日收盘比=必然假
        # 接缝（实测每次守护重启30只ETF全被误判全量重拉）；全史交给去重合并。
        if cached_last_close is not None and not full_pull and len(new):
            new_first = str(new["date"].iloc[0]).replace("-", "")
            cached_last_d = str(cached["date"].iloc[-1]).replace("-", "")
            first_open = float(new["open"].iloc[0])
            if (new_first > cached_last_d and first_open > 0
                    and not (0.945 <= first_open / cached_last_close <= 1.055)):
                log.warning("%s 拼接缝异常(%.2f%%)→全量重拉",
                            code, (first_open / cached_last_close - 1) * 100)
                full_pull = True
                try:
                    new = _fetch_hist(code, default_start, end_date)
                except Exception as e:  # noqa: BLE001
                    log.warning("全量重拉失败 %s: %s（保留旧缓存）", code, e)
                    continue
        if full_pull:
            merged = new.drop_duplicates(subset="date").sort_values("date")
        elif os.path.exists(path):
            old = pd.read_csv(path, dtype={"date": str})
            new = new[~new["date"].isin(set(old["date"]))]
            merged = pd.concat([old, new], ignore_index=True)
        else:
            merged = new
        merged.drop_duplicates(subset="date").sort_values("date").to_csv(path, index=False)
        if full_pull:
            _mark_full_pull(code)
            horizon_pending.discard(code)  # 扩史重拉成功→移出待重集合（自愈）
            # 污染清除判定（科学口径）：只有真实改写了历史内容才升纪元——
            # ①与旧缓存内容一致的重拉（源冻结/重复拉同数据）不算重写；
            # ②首拉落盘（无旧缓存）=池成分新增，由评估缓存键的成分哈希覆盖。
            # 否则源一冻结，每次守护重启都全量重拉同内容→纪元连跳→整个
            # 评估缓存被反复清空（2026-09-21 实测：30只ETF一晚跳4级）。
            if prev_df is not None and not _same_hist(prev_df, merged):
                full_pulled.append(code)
        updated.append(code)
        merged_last = str(merged["date"].iloc[-1]).replace("-", "") if len(merged) else ""
        if merged_last and merged_last < end_date:
            lagging.append((code, merged_last))
        time.sleep(0.35)  # 接口限速
    log.info("日线缓存更新完成，更新 %d/%d 只", len(updated), len(all_codes))
    if horizon_pending or full_pulled:
        _save_horizon_pending(default_start, horizon_pending)
    if horizon_pending:
        log.warning("【数据口径】仍有 %d 只待整段重拉（限流/断连自愈重试中，下次运行继续）：前8 %s",
                    len(horizon_pending), sorted(horizon_pending)[:8])
    elif full_pulled:
        log.info("【数据口径】扩史重拉本轮完成（成功 %d 只）", len(full_pulled))
    if lagging:
        # 数据新鲜度告警：合并后仍滞后=数据源停更（2026-09-21 实测新浪ETF基金
        # 端点冻结3个交易日，30只ETF齐滞）。面板端表现为尾部NaN（诚实缺席），
        # 但停更必须可见可审计——训练/决策正在用过期尾部跑。
        log.warning("【数据新鲜度】%d 只尾部滞后于 %s（数据源停更？）：%s",
                    len(lagging), end_date,
                    " ".join(f"{c}止于{d}" for c, d in sorted(lagging)[:8]))
    # 历史重写（周全量重拉/拼接缝重拉/首拉）→ 升股票数据纪元：旧数据上的
    # 评估缓存分清除重算（qfq 前复权基准漂移会改历史值，陈旧分=污染）。
    # 仅"内容真实改写"计入（_same_hist 判定）——源冻结时反复重拉同内容不升纪元。
    if full_pulled:
        bump_data_epoch("stock", f"全量重拉改写历史{len(full_pulled)}只（qfq基准/换源重写）")
    return updated


def load_daily(code: str) -> pd.DataFrame | None:
    path = _daily_path(code)
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path, dtype={"date": str})
    except Exception:  # noqa: BLE001
        return None
    if not len(df):
        return None
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def load_all_daily(codes: list[str], years: float = 3.5) -> dict[str, pd.DataFrame]:
    """读取缓存并统一截取最近 years 年（保证股票/ETF 时间窗一致，避免幸存者偏差长窗口）。"""
    cutoff = pd.Timestamp(dt.date.today() - dt.timedelta(days=int(years * 366)))
    frames = {}
    for c in codes:
        f = load_daily(c)
        if f is None or len(f) <= 60:
            continue
        f = f[f.index >= cutoff]
        if len(f) > 60:  # 截取后仍需足够样本
            frames[c] = f
    return frames


@dataclass
class PanelData:
    """dates × codes 对齐面板。NaN 表示停牌/未上市（该日不可交易）。
    slip_mult：每标的滑点成本倍数（小市值=2.0，其余=1.0），回测/模拟盘撮合同源使用。"""
    open: pd.DataFrame
    high: pd.DataFrame
    low: pd.DataFrame
    close: pd.DataFrame
    volume: pd.DataFrame
    amount: pd.DataFrame
    codes: list[str]
    dates: pd.DatetimeIndex
    slip_mult: "np.ndarray | None" = None

    def window(self, start: pd.Timestamp, end: pd.Timestamp) -> "PanelData":
        m = (self.dates >= start) & (self.dates <= end)
        dates = self.dates[m]
        return PanelData(
            open=self.open.loc[dates], high=self.high.loc[dates], low=self.low.loc[dates],
            close=self.close.loc[dates], volume=self.volume.loc[dates], amount=self.amount.loc[dates],
            codes=self.codes, dates=dates, slip_mult=self.slip_mult,
        )


def build_panel(frames: dict[str, pd.DataFrame], slip_map: dict[str, float] | None = None) -> PanelData:
    import numpy as np
    all_dates = pd.DatetimeIndex(sorted(set().union(*[f.index for f in frames.values()])))
    codes = list(frames.keys())

    def _mat(field: str) -> pd.DataFrame:
        return pd.DataFrame({c: frames[c][field].reindex(all_dates) for c in codes})

    slip = None
    if slip_map:
        slip = np.array([float(slip_map.get(c, 1.0)) for c in codes])
    return PanelData(
        open=_mat("open"), high=_mat("high"), low=_mat("low"),
        close=_mat("close"), volume=_mat("volume"), amount=_mat("amount"),
        codes=codes, dates=all_dates, slip_mult=slip,
    )


def full_panel(cfg: AppConfig, refresh: bool = False, readonly: bool = False
               ) -> tuple[pd.DataFrame, PanelData]:
    """返回 (universe, panel)。缓存齐全时仅做增量更新。

    数据真实性闸：所有K线先过 validate_frames（OHLC矛盾/离谱跳变/缺失率/样本量），
    坏数据不得进入进化/回测——坏数据喂出的规律就是系统级幻觉。

    readonly=True：跳过 update_universe/update_daily（零网络）直接读本地缓存——
    盘中伴生联赛专用（盘中拉新浪会殃及交易会话限流；面板=昨夜日更口径，
    日频决策本就用昨收盘数据，语义正确）。
    """
    if readonly:
        uni = _load_universe_cache(cfg)
    else:
        uni = update_universe(cfg, force=refresh)
        update_daily(cfg)
    frames = load_all_daily(uni["code"].tolist(), years=cfg.universe.history_years)
    if len(frames) < 10:
        raise RuntimeError(f"可用行情数据过少（{len(frames)} 只），请检查网络后重跑 init")

    from .validation import validate_frames  # 延迟导入避免循环依赖
    frames, _vq = validate_frames(frames)
    if len(frames) < 30:
        raise RuntimeError(f"数据校验后仅 {len(frames)} 只通过，质量不足，拒绝进化（宁空仓不喂假数据）")

    slip_map = {}
    if "slip_mult" in uni.columns:
        slip_map = {str(c): float(v) for c, v in
                    zip(uni["code"], pd.to_numeric(uni["slip_mult"], errors="coerce").fillna(1.0))}
    # 期货接入架构裁决（2026-09-21 全品种指令）：F.* 列**永不并入本面板**——
    # 股票策略会把期货当"低波股"选（权重语义错配=隐形杠杆刷分）。期货走
    # futures.futures_window 自服务通道：cta_trend 策略/futures_backtest 引擎
    # 按评估窗口自取对齐数据，开关=cfg.universe.enable_futures；
    # 日更由 run.py auto 日常块挂载 update_futures_daily。
    panel = build_panel(frames, slip_map=slip_map)
    return uni, panel


# ---------------------------------------------------------------- 实时快照

def spot_quotes_light(codes: list[str]) -> dict[str, dict]:
    """轻量行情主源（腾讯 qt.gtimg.cn 逐标的）：会话只需盯持仓/订单几只票，
    不该每60秒拉一次全市场5000股大表（既浪费也是新浪限流根源，2026-09-21
    开盘实测：限流致成交延误12分钟）。返回格式与 spot_prices 一致。
    amount 取腾讯第37字段（万元→元），解析失败按0（调用方回退近5日均额）。
    F.* 期货代码走新浪 nf_ 主力连续源（futures.spot_quotes_futures，含涨跌停字段）。"""
    import requests
    out: dict[str, dict] = {}
    if not codes:
        return out
    fut_codes = [c for c in codes if str(c).startswith("F.")]
    stk_codes = [c for c in codes if not str(c).startswith("F.")]
    if fut_codes:
        from .futures import spot_quotes_futures
        out.update(spot_quotes_futures(fut_codes))
    # 分批请求（50只/批）：会话全宇宙~190只≈4请求，任何规模都走轻量源
    for k0 in range(0, len(stk_codes), 50):
        chunk = stk_codes[k0:k0 + 50]
        syms = [f"{'sh' if c[0] in '56' else 'sz'}{c}" for c in chunk]
        try:
            r = requests.get("http://qt.gtimg.cn/q=" + ",".join(syms), timeout=8)
            r.encoding = "gbk"
            for seg in r.text.split(";"):
                if "~" not in seg:
                    continue
                p = seg.split("~")
                if len(p) < 40:
                    continue
                code = p[2].zfill(6)
                try:
                    amount = float(p[37]) * 10000.0
                except (ValueError, IndexError):
                    amount = 0.0
                out[code] = {"name": p[1], "price": float(p[3]) if p[3] else 0.0,
                             "prev_close": float(p[4]) if p[4] else 0.0,
                             "amount": amount}
        except Exception:  # noqa: BLE001
            continue
    return {c: v for c, v in out.items() if v.get("price", 0) > 0}


def spot_prices(codes: list[str]) -> dict[str, dict]:
    """实时快照：code -> {name, price, prev_close, amount}。股票走新浪，ETF走东财。

    amount=当日成交额（元），供模拟盘成交额参与率约束使用；缺失时为0（调用方回退近5日均额）。
    """
    import akshare as ak
    out: dict[str, dict] = {}
    stocks = [c for c in codes if not is_etf(c)]
    etfs = [c for c in codes if is_etf(c)]

    if stocks:
        spot = _retry_call(ak.stock_zh_a_spot)
        code_s = spot["代码"].astype(str)
        sub = spot[code_s.str[-6:].isin(stocks)]
        for _, r in sub.iterrows():
            c = str(r["代码"])[-6:]
            out[c] = {"name": str(r.get("名称", "")),
                      "price": float(_num(pd.Series([r["最新价"]])).iloc[0]) if pd.notna(r["最新价"]) else 0.0,
                      "prev_close": float(r["昨收"]) if pd.notna(r["昨收"]) else 0.0,
                      "amount": float(_num(pd.Series([r.get("成交额", 0)])).iloc[0] or 0.0)}
    if etfs:
        spot = _retry_call(ak.fund_etf_spot_em)
        code_s = spot["代码"].astype(str).str.zfill(6)
        sub = spot[code_s.isin(etfs)]
        has_prev = "昨收" in spot.columns
        for _, r in sub.iterrows():
            c = str(r["代码"]).zfill(6)
            out[c] = {"name": str(r.get("名称", "")),
                      "price": float(r["最新价"]) if pd.notna(r["最新价"]) else 0.0,
                      "prev_close": float(r["昨收"]) if has_prev and pd.notna(r["昨收"]) else 0.0,
                      "amount": float(_num(pd.Series([r.get("成交额", 0)])).iloc[0] or 0.0)}
    return out
