"""Market regime detection: 0=bull 1=chop 2=crash 3=rebound (style adaptation layer)."""
import numpy as np
import pandas as pd

NAMES = ["bull", "chop", "crash", "rebound"]
N_REGIMES = 4


def compute(idx_close, breadth):
    """idx_close: [T] index closes (SSE composite); breadth: [T] fraction of
    stocks above their MA20. Returns int8 regime id series [T]."""
    s = pd.Series(np.asarray(idx_close, dtype=float))
    b = pd.Series(np.asarray(breadth, dtype=float))
    ma20 = s.rolling(20, min_periods=20).mean()
    ma60 = s.rolling(60, min_periods=60).mean()
    dd60 = s / s.rolling(60, min_periods=20).max() - 1.0

    crash_now = (dd60 < -0.07) | (b < 0.35)
    was_crash = crash_now.rolling(10, min_periods=1).max().shift(1).fillna(0.0) > 0
    rising = b > b.shift(5) + 0.05
    bull = (s > ma60) & (ma20 > ma60) & (b > 0.55)

    rid = np.ones(len(s), dtype=np.int8)                 # default chop
    rid[bull.fillna(False).values] = 0
    rebound = (was_crash.fillna(False).values & (~crash_now.values) & rising.fillna(False).values)
    rid[rebound] = 3
    rid[crash_now.fillna(False).values] = 2
    rid[:60] = 1                                        # warmup
    return rid
