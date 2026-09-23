"""基本面负面清单系统（用户四条规则）。

① 亏损的不做       —— 最新报告期净利润 ≤ 0 → 剔除（自动）
② 暴雷的不做       —— 净利润同比 < -60%（暴雷代理）+ ST/退名称 + 手动黑名单（自动+手动）
③ 共识衰亡行业不做 —— blacklist.industries 关键词（预置"房地产"，用户可增删）（自动）
④ 舆论负面广不做   —— 舆情判断无法可靠自动化：由人判断，`run.py blacklist add` 执行（手动）

数据源：东财业绩报表 stock_yjbb_em（实测本网络可用，全市场 ~11450 只单次请求 15 秒，
含 净利润 / 净利润同比 / 所处行业 三个关键字段）。缓存于 data/negative/，按报告期+周期刷新。
无业绩数据的标的（ETF/新股）按名称关键词过滤（如"房地产ETF"）。

接入点：universe 筛选 → 备单终检 → 会话持仓负面离场，三层同源。
限制（如实说明）：历史回测用"当前"负面清单剔除股票池——存在幸存者口径近似，
但方向保守（宁可错杀当下可疑者，不追过去的亏损者）。
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os

import pandas as pd

from .config import AppConfig, DATA_DIR

log = logging.getLogger("quant.fund")

NEG_DIR = os.path.join(DATA_DIR, "negative")
BLACKLIST_FILE = os.path.join(NEG_DIR, "blacklist.json")
_MEM: dict = {}  # 报告期 → (df, 时间戳) 进程内TTL缓存

_DEFAULT_BLACKLIST = {
    "codes": {},          # {"600000": "舆论负面 2026-09 说明", ...}
    "industries": ["房地产", "房地产开发", "房地产服务"],  # 市场共识衰亡行业（用户可增删）
    "names_contains": ["ST", "退"],
    "note": "行业与个股黑名单：run.py blacklist add/remove/add-industry/remove-industry 维护；"
            "舆论负面由人判断后录入，系统三层强制执行",
}


def load_blacklist() -> dict:
    os.makedirs(NEG_DIR, exist_ok=True)
    bl = dict(_DEFAULT_BLACKLIST)
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, encoding="utf-8") as f:
                user = json.load(f)
            for k in _DEFAULT_BLACKLIST:
                if k in user:
                    bl[k] = user[k]
        except Exception as e:  # noqa: BLE001
            log.warning("blacklist.json 读取失败用默认: %s", e)
    return bl


def save_blacklist(bl: dict) -> str:
    os.makedirs(NEG_DIR, exist_ok=True)
    bl["updated"] = dt.datetime.now().isoformat(timespec="seconds")
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(bl, f, ensure_ascii=False, indent=2)
    return BLACKLIST_FILE


def name_excluded(name: str, bl: dict) -> str | None:
    """名称级负面命中（ST/退/黑名单行业关键词，ETF无业绩数据时也走这里）。"""
    for kw in bl.get("names_contains", []):
        if kw and kw in name:
            return f"名称含{kw}"
    for kw in bl.get("industries", []):
        if kw and kw in name:
            return f"行业排除:{name}"
    return None


# ---------------------------------------------------------------- 业绩数据

def _report_dates() -> list[str]:
    """候选报告期（降序）：今年与去年各季末，晚披露的由调用方逐个尝试。"""
    today = dt.date.today()
    out: list[str] = []
    for year in (today.year, today.year - 1):
        for md in ("0930", "0630", "0331", "1231"):
            rpt = dt.date(year, int(md[:2]), int(md[2:]))
            if rpt <= today:
                out.append(rpt.strftime("%Y%m%d"))
    return sorted(set(out), reverse=True)


def update_fundamentals(cfg: AppConfig, force: bool = False) -> tuple[pd.DataFrame | None, str]:
    """拉取/刷新最新业绩报表（净利润/同比/行业）。返回 (df|None, 报告期)。

    带进程内10分钟TTL缓存：会话60秒轮询调用负面离场判定时不再重复读CSV。
    """
    import time as _time
    fcfg = cfg.fundamental
    os.makedirs(NEG_DIR, exist_ok=True)
    now = _time.time()
    for rpt in _report_dates():
        cached = _MEM.get(rpt)
        if cached is not None and not force and now - cached[1] < 600:
            return cached[0], rpt
        cache = os.path.join(NEG_DIR, f"earnings_{rpt}.csv")
        if os.path.exists(cache):
            mtime = dt.datetime.fromtimestamp(os.path.getmtime(cache))
            fresh = (dt.datetime.now() - mtime).days < fcfg.earnings_cache_days
            if fresh and not force:
                df = pd.read_csv(cache, dtype={"股票代码": str})
                _MEM[rpt] = (df, now)
                return df, rpt
        try:
            import akshare as ak
            df = ak.stock_yjbb_em(date=rpt)
        except Exception:  # noqa: BLE001 该报告期未披露完/接口波动 → 试上一期
            continue
        if df is None or len(df) < 1000:
            continue
        df["股票代码"] = df["股票代码"].astype(str).str.zfill(6)
        keep = ["股票代码", "股票简称", "净利润-净利润", "净利润-同比增长", "所处行业", "最新公告日期"]
        df[[c for c in keep if c in df.columns]].to_csv(cache, index=False)
        _MEM[rpt] = (df, now)
        log.info("业绩报表已更新: %s 报告期 %d 只 → %s", rpt, len(df), cache)
        return df, rpt
    log.warning("业绩报表全候选期获取失败（负面清单自动项降级为仅黑名单+名称过滤）")
    return None, ""


# ---------------------------------------------------------------- 排除判定

def build_exclusions(cfg: AppConfig, codes: list[str], names: dict[str, str],
                     force_refresh: bool = False) -> dict[str, str]:
    """返回 {code: reason}：负面清单命中情况（自动亏损/暴雷/行业 + 手动黑名单）。

    只判定给定 codes；无业绩数据的代码退化为名称关键词匹配。
    任何内部异常都返回空 dict（负面清单失效不阻塞交易主流程，但日志告警）。
    """
    bl = load_blacklist()
    fcfg = cfg.fundamental
    out: dict[str, str] = {}
    if not fcfg.enabled:
        return out
    try:
        earnings, rpt = update_fundamentals(cfg, force=force_refresh)
    except Exception as e:  # noqa: BLE001
        log.warning("业绩数据获取异常（负面清单降级）: %s", e)
        earnings, rpt = None, ""

    prof: dict[str, tuple] = {}
    if earnings is not None:
        sub = earnings[earnings["股票代码"].isin(set(codes))]
        for _, r in sub.iterrows():
            prof[str(r["股票代码"])] = (
                pd.to_numeric(r.get("净利润-净利润"), errors="coerce"),
                pd.to_numeric(r.get("净利润-同比增长"), errors="coerce"),
                str(r.get("所处行业", "") or ""),
            )
    log.debug("负面清单判定 %d 只（业绩覆盖 %d，报告期 %s）", len(codes), len(prof), rpt or "无")

    for code in codes:
        name = str(names.get(code, ""))
        if code in bl.get("codes", {}):
            out[code] = f"黑名单:{bl['codes'][code]}"
            continue
        r = name_excluded(name, bl)
        if r:
            out[code] = r
            continue
        p = prof.get(code)
        if p is None:
            continue  # 无业绩数据且名称未命中 → 放行（ETF/新股）
        np_, yoy, industry = p
        if pd.notna(np_) and float(np_) <= fcfg.min_net_profit:
            out[code] = "亏损:最新报告期净利润≤0"
            continue
        if pd.notna(yoy):
            yoy_ratio = float(yoy) / 100.0  # 东财同比字段为百分数
            if yoy_ratio < fcfg.profit_yoy_floor:
                out[code] = f"暴雷:净利同比{yoy_ratio:.0%}"
                continue
        for kw in bl.get("industries", []):
            if kw and kw in industry:
                out[code] = f"行业排除:{industry}"
                break
    return out


def negative_exit_orders(cfg: AppConfig, positions: dict, names: dict[str, str]) -> list[dict]:
    """持仓负面离场单：持仓中新触发负面清单（亏损披露/暴雷/行业/黑名单）→ 强制清仓。

    "不做"包含持货：已持仓的标的一旦触发负面即离场（T+1 可卖部分）。
    """
    if not cfg.fundamental.enabled or not cfg.fundamental.exit_on_negative:
        return []
    if not positions:
        return []
    excl = build_exclusions(cfg, list(positions.keys()), names)
    out: list[dict] = []
    LOT = 100
    for c, pos in positions.items():
        if c not in excl:
            continue
        avail = pos.get("available", 0)
        shares = avail // LOT * LOT
        if shares > 0:
            out.append({"code": c, "side": "sell", "shares": int(shares), "reason": "negative"})
    return out
