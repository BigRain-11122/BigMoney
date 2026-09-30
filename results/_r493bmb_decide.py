import subprocess, os
# 1) refresh log tail
LOG = 'logs/astock_daily_refresh.log'
if os.path.exists(LOG):
    with open(LOG, 'rb') as f:
        f.seek(max(0, os.path.getsize(LOG) - 1500))
        print('=== astock_daily_refresh.log tail ===')
        print(f.read().decode('utf-8', 'replace'))
else:
    print('no refresh log')
# 2) sina connectivity probe: one tiny request (quarantined sym 000016 daily qfq tail)
try:
    import akshare as ak
    df = ak.stock_zh_a_daily(symbol='sz000016', start_date='20260925', end_date='20260930')
    print('SINA PROBE OK rows:', len(df))
    print(df.tail(3).to_string())
except Exception as e:
    print('SINA PROBE FAIL:', type(e).__name__, str(e)[:200])
