"""Live view: paper portfolio marked to the latest local snapshot + market state."""
import json

import pandas as pd

import config as C
import data as D


def main():
    snap_p = D.LIVE_DIR / "latest.parquet"
    if not snap_p.exists():
        print("no snapshot yet - run: python live_pull.py")
        return
    snap = pd.read_parquet(snap_p).set_index("code")
    meta = json.loads((D.LIVE_DIR / "latest.json").read_text(encoding="utf-8"))
    print(f"快照时间: {meta['time']} | 行情日期: {meta['trade_date']} | "
          f"全市场: {meta['stocks']}只 成交{meta['total_amount_yi']:.0f}亿 "
          f"涨{meta['up_count']}/平{meta['flat_count']}/跌{meta['down_count']}")

    paper_p = RP_paper = C.RESULTS_DIR / "paper.json"
    if paper_p.exists():
        paper = json.loads(paper_p.read_text(encoding="utf-8"))
        cash = paper["cash"]
        total = cash
        print(f"\n100万模拟盘实时盯盘:")
        print(f"{'代码':<8}{'名称':<8}{'持仓':>7}{'成本':>8}{'现价':>8}{'浮盈':>9}")
        for code, p in paper["positions"].items():
            if code in snap.index:
                px = float(snap.loc[code, "close"])
                val = p["shares"] * px
                pnl = val - p["cash_cost"]
                total += val
                name = str(snap.loc[code, "name"])[:4]
                print(f"{code:<8}{name:<8}{p['shares']:>7d}{p['cost']:>8.3f}"
                      f"{px:>8.2f}{pnl / p['cash_cost'] * 100:8.1f}%")
            else:
                total += p["shares"] * p.get("last", p["cost"])
                print(f"{code:<8}{'(无快照)':<8}{p['shares']:>7d}")
        print(f"{'现金':>16}{cash:>23,.0f}")
        print(f"{'总权益':>16}{total:>23,.0f}  ({(total / C.CAPITAL - 1) * 100:+.2f}%)")
    else:
        print("paper.json 尚未建立（首个交易日收盘后自动开张）")

    sig_p = C.RESULTS_DIR / "signals.json"
    if sig_p.exists():
        sig = json.loads(sig_p.read_text(encoding="utf-8"))
        print(f"\n待执行信号(信号日 {sig['signal_date']} 市场状态 {sig['regime']} "
              f"目标仓位 {sig['exposure'] * 100:.0f}%):")
        for b in sig["buys"][:8]:
            code = b["code"]
            px = float(snap.loc[code, "close"]) if code in snap.index else float("nan")
            print(f"  {b['code']} {b['name']:<6} {b['fam_cn']} score={b['score']:.3f} 现价={px:.2f}")


if __name__ == "__main__":
    main()
