"""Structured market rules. Backtest engine reads this, never hardcodes.

Version: v2026.09.22
Source: see market_rules.md
"""
from dataclasses import dataclass, field
from datetime import date


RULES_VERSION = "v2026.09.22"
RULES_UPDATED = "2026-09-22"


@dataclass(frozen=True)
class FeeSchedule:
    commission_rate: float = 0.00025       # 万2.5 (双边)
    commission_min: float = 5.0            # 起点5元
    stamp_tax: float = 0.0                 # ETF 免征
    transfer_fee: float = 0.0             # ETF 不收过户费
    handling_fee: float = 0.0000341        # 经手费 0.0341‰ 双边
    supervision_fee: float = 0.00002      # 证管费 0.002% 双边
    slippage_a: float = 0.001              # A 级流动性
    slippage_c: float = 0.003              # C 级流动性


@dataclass(frozen=True)
class PriceLimit:
    main_board: float = 0.10
    star_chinext: float = 0.20
    st_main_board: float = 0.10            # 2026-07-06 从 5% 改为 10%
    bse: float = 0.30


# T+0 ETF codes (can buy and sell same day)
T0_ETF_CODES = frozenset({
    # 债券 ETF
    "511260", "511090", "511010",
    # 黄金 ETF
    "518880", "159934",
    # 跨境 ETF
    "513100", "513500", "513050", "513180", "159920", "513520",
    # 货币 ETF (not in our universe but listed for completeness)
    "511880", "511990",
})


def is_t0(code: str) -> bool:
    return code in T0_ETF_CODES


def min_lot(code: str) -> int:
    return 100   # 1 hand = 100 shares for buy


def price_tick(code: str) -> float:
    return 0.001  # funds


def total_buy_cost(price: float, qty: int,
                   fee: FeeSchedule = FeeSchedule()) -> float:
    """Total cash needed to buy qty shares at price (incl fees)."""
    gross = price * qty
    fee_total = max(gross * fee.commission_rate, fee.commission_min)
    fee_total += gross * (fee.handling_fee + fee.supervision_fee)
    fee_total += gross * fee.slippage_a
    return gross + fee_total


def total_sell_proceeds(price: float, qty: int,
                        fee: FeeSchedule = FeeSchedule()) -> float:
    """Cash received after selling qty shares at price (net of fees)."""
    gross = price * qty
    fee_total = max(gross * fee.commission_rate, fee.commission_min)
    fee_total += gross * (fee.handling_fee + fee.supervision_fee)
    fee_total += gross * fee.slippage_a
    return gross - fee_total
