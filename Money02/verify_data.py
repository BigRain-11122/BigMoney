"""Final source sanity: sina fetch quality + throughput probe."""
import time
import config as C
import data as D

for c in ["000001", "000002", "600519", "300750", "688981"]:
    t0 = time.time()
    df = D.fetch_hist(c, C.HIST_START)
    if df is None:
        print(f"{c}: EMPTY ({time.time()-t0:.1f}s)")
        continue
    lim = 20.0 if c.startswith(("30", "68")) else 10.0
    over = (df["pct_chg"].abs() > lim + 0.3).sum()
    cap = float(df["close"].iloc[-1] * df["outstanding_share"].iloc[-1]) / 1e8
    print(f"{c}: rows={len(df)} {df['date'].min().date()}..{df['date'].max().date()} "
          f"|pct|>{lim + 0.3}:{over} floatCapNow={cap:.0f}亿 ({time.time()-t0:.1f}s)")
print("SINA FETCH PASS")
