"""miniQMT 实盘接口（xtquant 适配器）。

接入前提：
1. QMT 客户端以「极简模式」运行且保持登录（建议交易日 8:45 前启动）
2. 复制 config.example.json → config.json，填写 qmt.account_id（资金账号）与
   qmt.qmt_path（QMT 安装目录下 userdata_mini 路径）
3. xtquant 可导入：`pip install xtquant`；装不上则把 QMT 自带库目录填到
   qmt.xtquant_path（如 D:\\QMT\\bin.x64\\Lib\\site-packages）
4. qmt.dry_run=true 时仅打印委托不真实报单——联调通过后手动改 false
5. 合规：按《证券市场程序化交易管理规定》（2025-07 施行），程序化交易须先向
   券商完成报备；本系统为日频调仓（远低于高频报备线），但仍需走报备流程。
"""
from __future__ import annotations

import logging
import os
import sys

from .config import QmtConfig

log = logging.getLogger("quant.qmt")


def qmt_symbol(code: str) -> str:
    """600519 → 600519.SH；000001/159915 → .SZ。"""
    if code.startswith(("60", "68", "51", "56", "58")):
        return code + ".SH"
    return code + ".SZ"


class QmtBroker:
    def __init__(self, cfg: QmtConfig):
        self.cfg = cfg
        self.dry_run = bool(cfg.dry_run)
        if not cfg.account_id or not cfg.qmt_path:
            raise RuntimeError(
                "QMT 未配置：请复制 config.example.json 为 config.json，填写 qmt.account_id（资金账号）"
                "与 qmt.qmt_path（QMT 目录下 userdata_mini 路径）")
        if cfg.xtquant_path and os.path.isdir(cfg.xtquant_path):
            sys.path.insert(0, cfg.xtquant_path)
        try:
            from xtquant import xtconstant  # noqa: F401
            from xtquant.xttrader import XtQuantTrader  # noqa: F401
            from xtquant.xttype import StockAccount  # noqa: F401
        except ImportError as e:
            raise RuntimeError(
                "xtquant 未安装：pip install xtquant，或在 config.json 的 qmt.xtquant_path 填入 "
                "QMT 自带库路径（如 D:\\QMT\\bin.x64\\Lib\\site-packages）") from e

        if self.dry_run:
            log.warning("QMT dry_run=true：只生成委托记录，不真实报单（联调通过后改 false）")
            self.trader = None
            self.account = None
            self._xt_cls = None
            self._acc_cls = None
            self._const = None
            return

        from xtquant import xtconstant
        from xtquant.xttrader import XtQuantTrader
        from xtquant.xttype import StockAccount
        self._const = xtconstant
        self.trader = XtQuantTrader(cfg.qmt_path, int(cfg.session_id))
        self.trader.start()
        ret = self.trader.connect()
        if ret != 0:
            raise RuntimeError(f"QMT 连接失败（connect={ret}）：请确认 QMT 极简模式已启动并登录")
        self.account = StockAccount(cfg.account_id)
        if self.trader.subscribe(self.account) != 0:
            raise RuntimeError("QMT 订阅账户回报失败")
        log.info("QMT 已连接，账户 %s", cfg.account_id)

    # -------------------------------------------------- 查询

    def asset(self) -> dict:
        """真实账户权益。dry_run 返回空。"""
        if self.dry_run:
            return {}
        a = self.trader.query_stock_asset(self.account)
        return {"cash": float(getattr(a, "cash", 0.0) or 0.0),
                "market_value": float(getattr(a, "market_value", 0.0) or 0.0),
                "total": float(getattr(a, "total_asset", 0.0) or 0.0)}

    def positions(self) -> dict:
        """真实持仓：code -> {shares, available, cost}。"""
        if self.dry_run:
            return {}
        out: dict[str, dict] = {}
        for p in self.trader.query_stock_positions(self.account) or []:
            code = str(getattr(p, "stock_code", "")).split(".")[0]
            cost = float(getattr(p, "avg_price", 0) or getattr(p, "open_price", 0) or 0)
            out[code] = {"shares": int(getattr(p, "volume", 0) or 0),
                         "available": int(getattr(p, "can_use_volume", 0) or 0),
                         "cost": float(cost or 0.0)}
        return out

    def orders(self) -> list:
        if self.dry_run:
            return []
        return list(self.trader.query_stock_orders(self.account) or [])

    # -------------------------------------------------- 交易

    def buy(self, code: str, shares: int, price: float):
        return self._order(code, "buy", shares, price)

    def sell(self, code: str, shares: int, price: float):
        return self._order(code, "sell", shares, price)

    def _order(self, code: str, side: str, shares: int, price: float):
        sym = qmt_symbol(code)
        # 委托价精度：股票0.01元，基金0.001元（交易所最小变动价位）
        from .data import is_etf
        px = round(float(price), 3 if is_etf(code) else 2)
        if self.dry_run:
            log.info("[QMT-dry] %s %s %d股 @%.3f（未真实报单）", side, sym, shares, px)
            return None
        order_type = self._const.STOCK_BUY if side == "buy" else self._const.STOCK_SELL
        seq = self.trader.order_stock(self.account, sym, order_type, int(shares),
                                      self._const.FIX_PRICE, px,
                                      "quant", f"money_{self.cfg.session_id}")
        if seq is None or int(seq) < 0:
            log.error("QMT 下单失败 %s %s seq=%s", side, sym, seq)
            return None
        log.info("[QMT] 已报单 %s %s %d股 @%.3f seq=%s", side, sym, shares, px, seq)
        return seq

    def cancel_all(self) -> None:
        """撤当日全部未完结委托（收盘前与紧急停机用）。"""
        if self.dry_run or self.trader is None:
            return
        try:
            for o in self.trader.query_stock_orders(self.account) or []:
                try:
                    self.trader.cancel_order_stock(self.account, getattr(o, "order_id", None))
                except Exception:  # noqa: BLE001 已成交/已撤的会失败，忽略
                    pass
        except Exception as e:  # noqa: BLE001
            log.warning("批量撤单异常: %s", e)


# -------------------------------------------------- 自动发现（全自动化接入）

def discover_qmt() -> tuple[str, str] | None:
    """扫描本机 QMT（miniQMT）安装：userdata_mini 目录 → 提取资金账号。

    用户指令（2026-09-20）：全自动化、不人工填值——QMT 装好后守护启动时
    自动发现并写回 config.json。保守策略防误判：
    · 只认目录名精确 "userdata_mini"（极独特，不模糊匹配）；
    · 深度只进"疑似 QMT 安装目录"（名字含 qmt/券商/迅投关键字），不全盘漫游；
    · 账号仅从目录/文件名中的纯数字（5-12 位）提取，多候选取最新修改者；
      提取不到则留空（qmt_path 先接入，账号待补，绝不编造）。
    返回 (qmt_path, account_id)；未发现返回 None。
    """
    import re
    import time

    roots: list[str] = []
    for drive in ("C:\\", "D:\\", "E:\\"):
        if os.path.isdir(drive):
            roots.append(drive)
    home = os.path.expanduser("~")
    roots += [os.path.join(home, n) for n in ("Desktop", "Downloads", "AppData\\Local", "AppData\\Roaming")]
    roots += ["C:\\Program Files", "C:\\Program Files (x86)"]

    hint = re.compile(r"qmt|userdata|xtquant|迅投|国金|中泰|华鑫|东兴|国盛|九州|安信|极速", re.I)
    found: list[str] = []
    seen: set[str] = set()
    deadline = time.time() + 20.0  # 时间盒20秒：装上QMT后下次守护启动自动接入
    for root in roots:
        if time.time() > deadline:
            break
        if not os.path.isdir(root):
            continue
        try:
            for ent in os.scandir(root):
                if time.time() > deadline:
                    break
                if not ent.is_dir(follow_symlinks=False):
                    continue
                if ent.name.lower() == "userdata_mini":
                    if ent.path not in seen:
                        seen.add(ent.path)
                        found.append(ent.path)
                    continue
                if not hint.search(ent.name):
                    continue  # 只深入疑似安装目录
                try:
                    for ent2 in os.scandir(ent.path):
                        if ent2.is_dir(follow_symlinks=False) and ent2.name.lower() == "userdata_mini":
                            if ent2.path not in seen:
                                seen.add(ent2.path)
                                found.append(ent2.path)
                except OSError:
                    continue
        except OSError:
            continue
    if not found:
        return None
    found.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    qmt_path = found[0]

    # 账号提取：userdata_mini 两层内 + 父目录（安装根）一层的纯数字条目
    digits = re.compile(r"^\d{5,12}$")
    cands: list[tuple[float, str]] = []

    def _scan_nums(base: str, depth: int) -> None:
        try:
            for ent in os.scandir(base):
                if digits.match(ent.name):
                    cands.append((ent.stat().st_mtime, ent.name))
                elif depth > 0 and ent.is_dir(follow_symlinks=False):
                    _scan_nums(ent.path, depth - 1)
        except OSError:
            return

    _scan_nums(qmt_path, 1)
    _scan_nums(os.path.dirname(qmt_path), 0)
    account = ""
    if cands:
        cands.sort(reverse=True)
        account = cands[0][1]
    return qmt_path, account
