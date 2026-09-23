"""Pull a full-market realtime snapshot to local (data/live/).

Standalone: python live_pull.py   (anytime; ~20s)
Also invoked by run_tick during market hours every 10 minutes.
"""
import config as C
import data as D

if __name__ == "__main__":
    df = D.pull_live_snapshot()
    import json
    meta = json.loads((D.LIVE_DIR / "latest.json").read_text(encoding="utf-8"))
    print(f"快照落盘: {meta['stocks']} 只 | 行情日期 {meta['trade_date']} | "
          f"全市场成交 {meta['total_amount_yi']:.0f} 亿 | "
          f"涨{meta['up_count']}/平{meta['flat_count']}/跌{meta['down_count']}")
    print(f"位置: {D.LIVE_DIR / 'latest.parquet'}")
