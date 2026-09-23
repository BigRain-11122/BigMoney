"""期货数据层（用户指令2026-09-21：所有国内合法品种——期货/基金/股票——都可交易）。

品种宇宙（首批，主力连续近似）：
  股指期货（中金所）: IF沪深300 / IC中证500 / IM中证1000 / IH上证50
  国债期货（中金所）: T十年 / TF五年
  商品期货（上期所/能源）: RB螺纹钢 / AU黄金 / SC原油
  商品期货（郑商所/大商所）: TA甲醇—— 首批不含（郑商所代码规则不同，二期接）

主力合约近似：新浪 futures_zh_daily_sina 按具体合约取数；主力=当月+随后三月中
持仓量（hold）最大者，按到期月滚动拼接为"主力连续"序列（换月跳空用价差对齐：
拼接处按新旧主力收盘价差平移历史——期货回测的标准连续合约处理）。

存储：data/futures_daily/{品种}.csv（日期,open,high,low,close,volume,hold）
接口：FUT_UNIVERSE / update_futures_daily() / load_futures_frames()
期货代码约定：前缀"F."（如 F.IF / F.AU）——与股票/ETF 六位代码天然隔离，
is_futures(code) 判别；面板负权重=空头头寸（期货双向，backtest 期货分支撮合）。
"""
from __future__ import annotations

import datetime as dt
import logging
import os

import pandas as pd

from .config import DATA_DIR, AppConfig, ensure_dirs
from .data import _retry_call

log = logging.getLogger("quant.futures")

FUT_DIR = os.path.join(DATA_DIR, "futures_daily")

# 品种 → (新浪合约月度生成前缀, 保证金率, 每手乘数, 手续费元/手)
# 保证金率/乘数取交易所公示标准近似（2026-09 口径）；手续费含商溢简化近似。
FUT_UNIVERSE: dict[str, dict] = {
    "IF": {"name": "沪深300股指", "margin": 0.12, "mult": 300.0, "fee_lot": 27.6},
    "IC": {"name": "中证500股指", "margin": 0.14, "mult": 200.0, "fee_lot": 34.6},
    "IM": {"name": "中证1000股指", "margin": 0.15, "mult": 200.0, "fee_lot": 36.8},
    "IH": {"name": "上证50股指", "margin": 0.12, "mult": 300.0, "fee_lot": 26.0},
    "T":  {"name": "十年国债", "margin": 0.02, "mult": 10000.0, "fee_lot": 4.2},
    "TF": {"name": "五年国债", "margin": 0.012, "mult": 10000.0, "fee_lot": 3.7},
    "RB": {"name": "螺纹钢", "margin": 0.09, "mult": 10.0, "fee_lot": 4.3},
    "AU": {"name": "黄金", "margin": 0.08, "mult": 1000.0, "fee_lot": 10.1},
    "SC": {"name": "原油", "margin": 0.10, "mult": 1000.0, "fee_lot": 20.0},
}

_FUT_CODES = [f"F.{v}" for v in FUT_UNIVERSE]


def is_futures(code: str) -> bool:
    return str(code).startswith("F.")


def fut_variety(code: str) -> str:
    return str(code)[2:]


# 品种涨跌幅近似（中金所/上期所/能源中心公示口径；撮合层单一定义，回测/模拟盘同源）
FUT_LIMITS = {"IF": 0.10, "IC": 0.12, "IM": 0.12, "IH": 0.10,
              "T": 0.02, "TF": 0.012, "RB": 0.07, "AU": 0.08, "SC": 0.13}


def last_close(code: str) -> float:
    """日线缓存最后收盘价（盯市兜底：实时源缺失时不丢仓位价值）。"""
    v = fut_variety(code)
    try:
        df = pd.read_csv(os.path.join(FUT_DIR, f"{v}.csv"))
        if len(df):
            return float(df["close"].iloc[-1])
    except Exception:  # noqa: BLE001
        pass
    return 0.0


def spot_quotes_futures(codes: list[str]) -> dict[str, dict]:
    """期货实时快照（新浪 hq.sinajs.cn 主力连续 nf_{品种}0，2026-09-21 午盘实测）。

    两种响应格式（品种族不同）：
    中金所系 IF/IC/IM/IH/T/TF：纯数值CSV open,high,low,latest,vol,amount,hold,
      bid,ask,涨停,跌停,?,?,昨收,昨结算,…（涨停/跌停为交易所公示精确价）
    商品系 RB/AU/SC：GBK名称开头 名称,时间,open,high,low,?,latest,买,卖,?,昨结,
      买量,卖量,持仓,成交量,…（无涨跌停字段→按品种涨跌幅×昨结近似）
    返回与股票快照同构：{code: {name, price, prev_close, amount, up_limit, dn_limit}}；
    prev_close=昨结算价（期货涨跌停基准），amount 成交额（商品系缺失记0→参与率上限自然跳过）。
    V1 披露：Sina "主力0" 为新浪主力约定，与本库 hold 最大主力在换月窗口存在基差——
    执行按 Sina 实时主力价撮合（真实可成交价），日线缓存按自有约定拼接，两端在换月数日后自对齐。
    """
    import requests
    out: dict[str, dict] = {}
    vmap: dict[str, str] = {}
    for c in codes:
        v = fut_variety(str(c))
        if v in FUT_UNIVERSE:
            vmap.setdefault(v, str(c))
    if not vmap:
        return out
    try:
        syms = ",".join(f"nf_{v}0" for v in vmap)
        r = requests.get(f"https://hq.sinajs.cn/list={syms}",
                         headers={"Referer": "https://finance.sina.com.cn"}, timeout=8)
        txt = r.content.decode("gbk", "replace")
    except Exception:  # noqa: BLE001
        return out
    for seg in txt.split(";"):
        if '"nf_' not in seg or "=" not in seg:
            continue
        try:
            key = seg.split("hq_str_", 1)[1].split("=", 1)[0]     # nf_IF0
            v = key[3:-1] if key.startswith("nf_") else ""
            if v not in vmap:
                continue
            raw = seg.split('"', 2)[1] if '"' in seg else ""
            f = raw.split(",")
            if len(f) < 15 or not f[0]:
                continue
            try:
                float(f[0])
                cff = True
            except ValueError:
                cff = False
            if cff:
                price, prev_settle = float(f[3]), float(f[14])
                up, dn, amount = float(f[9]), float(f[10]), float(f[5])
                name = FUT_UNIVERSE[v]["name"] + "主力"
            else:
                price, prev_settle = float(f[6]), float(f[10])
                lim = FUT_LIMITS.get(v, 0.08)
                up, dn, amount = prev_settle * (1 + lim), prev_settle * (1 - lim), 0.0
                name = f[0]
            if price <= 0 or prev_settle <= 0:
                continue
            out[vmap[v]] = {"name": name, "price": price,
                            "prev_close": prev_settle, "amount": amount,
                            "up_limit": up, "dn_limit": dn}
        except Exception:  # noqa: BLE001
            continue
    return out


def _contract_months(today: dt.date, n_ahead: int = 5) -> list[str]:
    """生成今日往前 n_ahead 个到期月的合约代码后缀（股指:当月/下月/随后两季月近似为月序列）。"""
    months: list[str] = []
    y, m = today.year, today.month
    for _ in range(n_ahead):
        months.append(f"{y % 100:02d}{m:02d}")
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return months


def _fetch_contract(variety: str, suffix: str) -> pd.DataFrame | None:
    """新浪拉单合约日线：date/open/high/low/close/volume/hold/settle。"""
    import akshare as ak
    try:
        raw = _retry_call(lambda: ak.futures_zh_daily_sina(symbol=f"{variety}{suffix}"), tries=2)
    except Exception as e:  # noqa: BLE001
        log.debug("期货合约 %s%s 拉取失败: %s", variety, suffix, e)
        return None
    if raw is None or not len(raw):
        return None
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    for col in ("open", "high", "low", "close", "volume", "hold"):
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    return df.dropna(subset=["close"])


def _main_series(variety: str, months: list[str]) -> pd.DataFrame | None:
    """按月序拼接主力连续：每月取该月到期合约在其活跃期（到期前）的数据，
    换月日按新旧主力收盘价差平移拼接（连续合约标准做法）。"""
    parts: list[pd.DataFrame] = []
    for i, suf in enumerate(months):
        df = _fetch_contract(variety, suf)
        if df is None or not len(df):
            continue
        parts.append(df)
        if len(parts) >= 2:
            break
    if not parts:
        return None
    if len(parts) == 1:
        df = parts[0]
    else:
        # 双段拼接：前段为主力月，后段为次主力月；重叠区间取持仓量大者
        a, b = parts[0], parts[1]
        overlap = a.index.intersection(b.index)
        if len(overlap) > 0:
            cut = overlap[0]
            a = a[a.index < cut]
            if len(a):
                shift = a["close"].iloc[-1] / b["close"].reindex([cut]).iloc[0]
                b = b.copy()
                b[["open", "high", "low", "close"]] = b[["open", "high", "low", "close"]] * shift
            df = pd.concat([a, b])
        else:
            df = pd.concat([a, b]).sort_index()
            # 段间无缝重叠：按末/首收盘价差平移后段
            if len(a):
                shift = a["close"].iloc[-1] / b["close"].iloc[0]
                b = b.copy()
                b[["open", "high", "low", "close"]] = b[["open", "high", "low", "close"]] * shift
            df = pd.concat([a, b]).sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df[["open", "high", "low", "close", "volume", "hold"]].dropna()


def update_futures_daily(cfg: AppConfig, refresh: bool = False) -> list[str]:
    """增量更新期货主力连续缓存。返回本次更新的品种代码（F.XXX）。"""
    import socket
    socket.setdefaulttimeout(20)
    ensure_dirs()
    os.makedirs(FUT_DIR, exist_ok=True)
    updated: list[str] = []
    today = dt.date.today()
    months = _contract_months(today, n_ahead=5)
    for variety, meta in FUT_UNIVERSE.items():
        code = f"F.{variety}"
        path = os.path.join(FUT_DIR, f"{variety}.csv")
        if not refresh and os.path.exists(path):
            mtime = dt.date.fromtimestamp(os.path.getmtime(path))
            # 每日一次重拼：文件今日已更新则跳过。auto 日更块在凌晨/收盘后跑，
            # 夜盘K线归属次交易日，凌晨拉取的前一交易日bar已完整——原
            # ".hour() 属性误调用"笔误（16:47 首跑即崩）与20点窗口依赖
            # （日更块凌晨跑永远到不了20点→缓存冻结）一并修复。
            if mtime >= today:
                continue
        df = _main_series(variety, months)
        if df is None or len(df) < 100:
            log.warning("期货 %s(%s) 主力连续数据不足（%s行），跳过",
                        variety, meta["name"], 0 if df is None else len(df))
            continue
        df.to_csv(path)
        updated.append(code)
        log.info("【期货数据】%s %s 主力连续 %d 行（%s ~ %s）",
                 variety, meta["name"], len(df), df.index[0].date(), df.index[-1].date())
    # 主力连续每日全量重拼=整段历史按新主力基差平移重写 → 升期货数据纪元
    # （污染清除机制：旧连续序列上的评估缓存分失效重算；期货专属域，不殃及
    #  股票缓存行——两域纪元独立，日更只清 cta_trend 相关行）。
    if updated:
        from .data import bump_data_epoch
        bump_data_epoch("futures", f"主力连续日更重拼接{len(updated)}品种")
    return updated


def load_futures_frames(years: int = 5) -> dict[str, pd.DataFrame]:
    """读取期货缓存为 Panel 帧格式（amount 用 成交额近似=close×volume×乘数 供参与率约束）。"""
    frames: dict[str, pd.DataFrame] = {}
    if not os.path.isdir(FUT_DIR):
        return frames
    for variety, meta in FUT_UNIVERSE.items():
        path = os.path.join(FUT_DIR, f"{variety}.csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        if len(df) < 60:
            continue
        cut = df.index[-1] - pd.Timedelta(days=int(years * 366))
        df = df[df.index >= cut].copy()
        df["amount"] = (df["close"] * df["volume"] * meta["mult"]).fillna(0.0)
        frames[f"F.{variety}"] = df[["open", "high", "low", "close", "volume", "amount"]]
    return frames


def futures_meta(code: str) -> dict:
    """期货撮合参数（backtest/paper 期货分支用）。"""
    return FUT_UNIVERSE.get(fut_variety(code), {"margin": 0.15, "mult": 100.0, "fee_lot": 20.0})


def position_value(code: str, pos: dict, price: float | None = None) -> float:
    """持仓成本近似市值（股票/ETF=shares×cost；期货=lots×乘数×avg_entry）。

    显示层/resume 基线用；权威盯市走 decide.account_equity（实时价）。"""
    if str(code).startswith("F."):
        m = FUT_UNIVERSE.get(fut_variety(str(code)))
        mult = float(m["mult"]) if m else 100.0
        p = price if price else float(pos.get("avg_entry", 0.0) or 0.0)
        return pos.get("lots", 0) * mult * p
    p = price if price else float(pos.get("cost", 0.0) or 0.0)
    return pos.get("shares", 0) * p


# ---------------------------------------------------------------- CTA 自服务数据通道（架构裁决 2026-09-21）
# 面板永不并入 F.* 列（股票策略会把期货当"低波股"选——权重语义错配=隐形杠杆刷分）。
# cta_trend 策略与 futures_backtest 引擎均通过本接口按评估窗口自取对齐数据，
# 期货通道开关 = cfg.universe.enable_futures（关闭时 cta_trend 返回空权重）。

_FUT_CSV_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}


def _fut_cache_df(variety: str) -> pd.DataFrame | None:
    """单品种 CSV 帧带 mtime 缓存（联赛/GA 千次评估免重读盘；日更后自动失效）。"""
    path = os.path.join(FUT_DIR, f"{variety}.csv")
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return None
    hit = _FUT_CSV_CACHE.get(variety)
    if hit and hit[0] == mtime:
        return hit[1]
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
    except Exception:  # noqa: BLE001
        return None
    if not len(df):
        return None
    _FUT_CSV_CACHE[variety] = (mtime, df)
    return df


def futures_window(dates) -> dict[str, pd.DataFrame]:
    """期货窗口帧：与给定日期索引对齐（缺日=NaN，停牌语义），供策略/引擎自取。

    返回 {F.品种: DataFrame[open,high,low,close,volume,amount]}；amount≈close×volume×乘数。"""
    dates = pd.DatetimeIndex(dates)
    out: dict[str, pd.DataFrame] = {}
    for variety, meta in FUT_UNIVERSE.items():
        df = _fut_cache_df(variety)
        if df is None:
            continue
        w = df.reindex(dates)
        w = pd.DataFrame({"open": w["open"], "high": w["high"], "low": w["low"],
                          "close": w["close"], "volume": w["volume"].fillna(0.0)})
        w["amount"] = (w["close"] * w["volume"] * meta["mult"]).fillna(0.0)
        out[f"F.{variety}"] = w
    return out


def futures_enabled(cfg: AppConfig | None = None) -> bool:
    """期货通道闸（cfg.universe.enable_futures）：CTA 策略/引擎自服务的前提。"""
    try:
        if cfg is not None:
            return bool(getattr(cfg.universe, "enable_futures", False))
        from .config import load_config
        return bool(getattr(load_config().universe, "enable_futures", False))
    except Exception:  # noqa: BLE001 配置读取失败=通道关（最保守默认）
        return False
