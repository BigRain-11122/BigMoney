"""Structured market rules. Backtest engine reads this, never hardcodes.

Version: v2026.09.22
Source: see market_rules.md
"""
import math
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


# ---------------------------------------------------------------------------
# D5 cost-basis v2 -- liquidity-tiered slippage (BACKTEST_SCIENCE.md s5).
# Frozen thresholds; NEW batches declare the basis version in their report;
# historical anchors keep the v1 flat basis (engine default path unchanged,
# dual-track prevents anchor drift). x2/x3 stress stays a second-level stress
# face applied on whichever basis a batch declares.
# ---------------------------------------------------------------------------

COST_BASIS_V1 = "v1-flat"           # per-side 13.041bp = fixed fees + 10bp flat slippage
COST_BASIS_V2 = "v2-adv20-tiered"   # ADV(20d) tiers 2/5/10bp + 1% ADV fill cap

# ADV(20d) tier edges, unit = yuan of mean daily turnover
ADV20_TIER_2BP_YUAN = 500_000_000.0   # >= 5e8 -> 2bp
ADV20_TIER_5BP_YUAN = 100_000_000.0   # [1e8, 5e8) -> 5bp; < 1e8 -> 10bp
ADV_FILL_CAP_RATE = 0.01              # entry demand above 1% of ADV(20d) does not fill

SLIPPAGE_TIER_2BP = 0.0002
SLIPPAGE_TIER_5BP = 0.0005
SLIPPAGE_TIER_10BP = 0.001            # == FeeSchedule.slippage_a (legacy flat)


def cost_v2_slippage(adv20_yuan) -> float:
    """Per-side slippage rate for an ADV(20d) turnover figure (yuan).

    adv20_yuan = rolling 20-day mean daily turnover ending at the SIGNAL
    close (the engine shifts it one execution day internally, so callers
    pass the unshifted through-date panel). Missing or invalid input falls
    back to the 10bp tier (= legacy slippage_a): a data gap can never
    cheapen costs.
    """
    try:
        v = float(adv20_yuan)
    except (TypeError, ValueError):
        return SLIPPAGE_TIER_10BP
    if math.isnan(v):
        return SLIPPAGE_TIER_10BP
    if v >= ADV20_TIER_2BP_YUAN:
        return SLIPPAGE_TIER_2BP
    if v >= ADV20_TIER_5BP_YUAN:
        return SLIPPAGE_TIER_5BP
    return SLIPPAGE_TIER_10BP


def cost_v2_side_rate(adv20_yuan, fee: FeeSchedule = None) -> float:
    """Full per-side rate under the v2 basis: fixed fees + tiered slippage."""
    f = fee if fee is not None else FeeSchedule()
    return (f.commission_rate + f.handling_fee + f.supervision_fee
            + cost_v2_slippage(adv20_yuan))
