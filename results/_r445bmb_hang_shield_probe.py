# _r445bmb_hang_shield_probe.py -- r445 hang-shield live-fire probe (no network):
# 1) module imports + gate default path OK
# 2) fake hanging ak fetch -> fetch_one must raise TimeoutError at deadline
# 3) real fast path: a fetch that returns promptly must parse through
import importlib.util
import io
import sys
import time

spec = importlib.util.spec_from_file_location("uad", "scripts/update_astock_daily.py")
m = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(m)
    print("P1 module-exec: OK (gate path did not SystemExit)")
except SystemExit as e:
    print(f"P1 module-exec: gate SystemExit code={e.code} (legal lane default)")

# P2: hang shield
def _hang(*a, **k):
    time.sleep(30)
m.ak.stock_zh_a_daily = _hang
t0 = time.time()
try:
    m.fetch_one("000001", "sz", timeout_s=1.5)
    print("P2 FAIL: no TimeoutError raised")
    sys.exit(1)
except TimeoutError as e:
    dt = time.time() - t0
    print(f"P2 HANG-SHIELD PASS: TimeoutError at {dt:.1f}s :: {str(e)[:70]}")
    assert dt < 5, "deadline not honored"

# P3: fast passthrough with a fake df
import pandas as pd
class _Rec:
    def __init__(self, d):
        self._d = d
    def __getitem__(self, k):
        return self._d[k]
def _fast(*a, **k):
    return pd.DataFrame({
        "date": ["2026-09-29"], "open": [10.0], "high": [10.5],
        "low": [9.9], "close": [10.2], "volume": [1000.0],
        "amount": [10200.0], "outstanding_share": [1e8], "turnover": [1.0]})
m.ak.stock_zh_a_daily = _fast
rows = m.fetch_one("000001", "sz", timeout_s=10)
assert rows and rows[0]["date"] == "2026-09-29" and rows[0]["close"] == 10.2, rows
print("P3 FAST-PATH PASS: rows parse through shield:", rows[0])

# P4: exception relay (non-hang fetch error must propagate verbatim)
def _boom(*a, **k):
    raise ConnectionError("synthetic conn fail")
m.ak.stock_zh_a_daily = _boom
try:
    m.fetch_one("000001", "sz", timeout_s=10)
    print("P4 FAIL: no relay")
    sys.exit(1)
except ConnectionError as e:
    print("P4 RELAY PASS: ConnectionError propagated:", e)
print("ALL PROBES GREEN")
