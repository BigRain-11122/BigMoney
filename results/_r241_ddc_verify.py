"""r241 s2 verification: dd_control engine flag (compile / byte-identity / fixture)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from engine import run_backtest

# synthetic production-form panel (r157/r221: fixture mirrors real load form)
dates = pd.bdate_range("2020-01-01", periods=200)
def mk(start=100.0, drift=0.0, vol=0.01, seed=7):
    import numpy as np
    rs = np.random.RandomState(seed)
    px = start * (1 + rs.normal(drift, vol, 200)).cumprod()
    return pd.DataFrame({"open": px, "high": px*1.01, "low": px*0.99,
                         "close": px, "volume": abs(rs.normal(1e6,1e5,200)),
                         "amount": abs(rs.normal(1e8,1e7,200))}, index=dates)
prices = {"111111": mk(seed=1), "222222": mk(seed=2), "333333": mk(seed=3)}
sig = pd.DataFrame(False, index=dates, columns=list(prices))
sig.iloc[5:9] = True   # early entries
sig.iloc[80:84] = True  # mid-window re-entries (post-drawdown zone)

r_none1 = run_backtest(prices, {"max_positions": 3}, entry_signal=sig, exit_signal=(sig <= 0))
r_none2 = run_backtest(prices, {"max_positions": 3}, entry_signal=sig, exit_signal=(sig <= 0))
assert json.dumps(r_none1["metrics"], sort_keys=True) == json.dumps(r_none2["metrics"], sort_keys=True)
assert "dd_control_days_de_risked" not in r_none1["metrics"], "None path must not emit new keys"
print("F1 None-path deterministic + keyset clean: PASS")

DDC = {"dd_trigger": -0.05, "de_risk_to": 0.50, "re_up_at": -0.02}
r_on = run_backtest(prices, {"max_positions": 3}, entry_signal=sig,
                    exit_signal=(sig <= 0), dd_control=DDC)
m = r_on["metrics"]
for k in ("dd_control_days_de_risked", "dd_control_scaled_entries",
          "dd_control_state_end", "dd_control_min_dd"):
    assert k in m, f"flag ON must emit {k}"
print("F2 flag-ON keyset:", {k: m[k] for k in m if k.startswith("dd_control")})

# forcing fixture: 90%-deployed continuous-entry portfolio on a heavy-crash
# panel -> NAV drawdown must breach the -5% trigger and engage de-risk
sig_all = pd.DataFrame(True, index=dates, columns=list(prices))
FORCE = {"max_positions": 3, "position_size_pct": 0.30, "initial_stop": -0.95,
         "take_profit_levels": (5.0, 5.0), "time_decay_period": 9999}
crash = {"111111": mk(drift=-0.004, vol=0.02, seed=5),
         "222222": mk(drift=-0.004, vol=0.02, seed=6),
         "333333": mk(drift=-0.004, vol=0.02, seed=8)}
rc = run_backtest(crash, FORCE, entry_signal=sig_all,
                  exit_signal=(sig_all <= 0), dd_control=DDC)
mc = rc["metrics"]
assert mc["dd_control_min_dd"] <= -0.05, f"crash panel must breach trigger, got {mc['dd_control_min_dd']}"
assert mc["dd_control_days_de_risked"] > 0, "de-risk state must engage"
assert mc["dd_control_scaled_entries"] > 0, "entries during de-risk must be scaled"
print("F3 crash fixture:", {k: mc[k] for k in mc if k.startswith("dd_control")})

# V-recovery fixture: crash then rebound -> dd narrows above re_up_at,
# state must flip back to normal while days_de_risked stays > 0 (hysteresis)
vpanel = {"111111": mk(drift=0.0, vol=0.001, seed=5)}
import numpy as np
rs = np.random.RandomState(11)
leg1 = 100 * (1 + rs.normal(-0.006, 0.005, 100)).cumprod()
leg2 = leg1[-1] * (1 + rs.normal(0.008, 0.003, 100)).cumprod()
px = np.concatenate([leg1, leg2])
vdf = pd.DataFrame({"open": px, "high": px*1.005, "low": px*0.995,
                    "close": px, "volume": np.full(200, 1e6),
                    "amount": np.full(200, 1e8)}, index=dates)
vsig = pd.DataFrame(True, index=dates, columns=["111111"])
rv = run_backtest({"111111": vdf}, {"max_positions": 1, "position_size_pct": 0.90,
                    "initial_stop": -0.95, "take_profit_levels": (5.0, 5.0),
                    "time_decay_period": 9999},
                  entry_signal=vsig, exit_signal=(vsig <= 0), dd_control=DDC)
mv = rv["metrics"]
assert mv["dd_control_days_de_risked"] > 0, "V fixture must engage de-risk"
assert mv["dd_control_state_end"] == "normal", f"recovery must restore state, got {mv['dd_control_state_end']}"
print("F4 V-recovery fixture:", {k: mv[k] for k in mv if k.startswith("dd_control")})

# validation guards
for bad in ({"dd_trigger": -0.05, "de_risk_to": 0.0, "re_up_at": -0.02},
            {"dd_trigger": -0.02, "de_risk_to": 0.5, "re_up_at": -0.05},
            {"dd_trigger": -0.05, "de_risk_to": 0.5, "re_up_at": 0.01}):
    try:
        run_backtest(prices, {}, entry_signal=sig, exit_signal=(sig <= 0), dd_control=bad)
        raise AssertionError("bad config must raise")
    except ValueError:
        pass
print("F5 config validation guards: PASS")
print("ALL ENGINE DD_CONTROL LEGS PASS")
