"""Global configuration: A-share short-term trading system (E:\Money)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BARS_DIR = ROOT / "data" / "bars"
IDX_DIR = ROOT / "data" / "index"
# spawn workers re-import this module fresh: cache dir must be inheritable
# via env (see smoke.py) or worker processes would look in the default path.
CACHE_DIR = Path(os.environ.get("MONEY_CACHE_DIR") or (ROOT / "data" / "cache"))
# per-market state isolation (2026-09-22: crypto league/paper live in their
# own results dir; A-share stays at the default results/)
RESULTS_DIR = Path(os.environ.get("MONEY_RESULTS_DIR") or (ROOT / "results"))
LOGS_DIR = ROOT / "logs"
for _d in (BARS_DIR, IDX_DIR, CACHE_DIR, RESULTS_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

HIST_START = "19900101"       # full domestic history (sources bottom out ~1992-1993)

# universe: SH/SZ main boards + ChiNext + STAR (BSE/B-shares excluded)
KEEP_PREFIX = ("60", "00", "30", "68")
MIN_LIST_DAYS = 120          # trading days since first bar before tradable
MIN_PRICE = 2.0
MAX_PRICE = 500.0
MIN_AMOUNT = 3.0e7           # daily turnover floor (CNY)

# execution & fees (A-share reality)
CAPITAL = 1_000_000.0
COMMISSION = 2.5e-4          # per side
MIN_COMMISSION = 5.0
STAMP_TAX = 5.0e-4            # sell side only
SLIPPAGE = 1.0e-3             # per side, applied on open fills
AMOUNT_PART_CAP = 0.05        # our order <= 5% of the day's turnover
LOT = 100
MAX_POS_PCT = 0.15            # single-name cap of total equity
MIN_HOLD_DAYS = 3             # user rule 2026-09-22: no day-trading - every
                              # position must complete >=3 full sessions before
                              # any non-protective exit (stop-loss exempt)

# walk-forward / evolution
TRAIN_DAYS = 480
TEST_DAYS = 60
START_OFFSET = 130            # warmup days for indicators before first train window
POP = 40
GENS_MAX = 10
ELITE = 4
PLATEAU = 4                   # early-stop when no improvement for N generations
TOURN = 3
MUT_P = 0.15
MUT_SIG = 0.12
SEED = 20260919
WF_BUDGET_MIN = 240           # soft time budget for one walk-forward pass (full-history run)

# benchmarks: hs300 / csi500 / sse composite (regime uses sse)
BENCH = {"hs300": "000300", "csi500": "000905", "sse": "000001"}

# download
DL_WORKERS = 12
DL_RETRIES = 4
