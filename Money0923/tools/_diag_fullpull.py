"""诊断：逐码重演 update_daily 的 full_pull 判定，找出下一轮仍会触发全量重拉的代码。

背景（2026-09-21 20:04 取证）：守护启动时"全量重拉27只"bump 了数据纪元——
若这27只在每次重启都会重拉，则每次重启都会清空整个股票评估缓存=严重低效。
本脚本只读不写。
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from quant import data as qd

uni = qd.load_universe()
codes = uni["code"].tolist()
today = dt.date.today()
end_date = qd.clock.last_trade_date(today - dt.timedelta(days=1)).strftime("%Y%m%d") \
    if dt.datetime.now().time() < dt.time(15, 30) else \
    qd.clock.last_trade_date(today).strftime("%Y%m%d")

no_stamp, due, no_csv, csv_err, lagging, ok_skip = [], [], [], [], [], []
for c in codes:
    path = qd._daily_path(c)
    stamp = os.path.join(qd._META_DIR, f"{c}.txt")
    if not os.path.exists(stamp):
        no_stamp.append(c)
        continue
    try:
        last = dt.date.fromisoformat(open(stamp, encoding="utf-8").read().strip())
        if (today - last).days >= 7:
            due.append((c, str(last)))
            continue
    except Exception:
        due.append((c, "bad-stamp"))
        continue
    if not os.path.exists(path):
        no_csv.append(c)
        continue
    try:
        cached = pd.read_csv(path, dtype={"date": str})
        last_bar = str(cached["date"].iloc[-1]).replace("-", "") if len(cached) else ""
        if last_bar < end_date:
            lagging.append((c, last_bar))
        else:
            ok_skip.append(c)
    except Exception:
        csv_err.append(c)

print(f"宇宙={len(codes)} 只 | end_date={end_date}")
print(f"无stamp(每次必全量重拉!): {len(no_stamp)} {no_stamp[:15]}")
print(f"stamp到期(≥7天): {len(due)} {due[:10]}")
print(f"无CSV: {len(no_csv)} {no_csv[:10]}")
print(f"CSV读坏: {len(csv_err)} {csv_err[:10]}")
print(f"数据滞后(last<end, 会走增量+接缝检测): {len(lagging)} {lagging[:8]}")
print(f"正常跳过: {len(ok_skip)}")
