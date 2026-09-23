"""Current universe/tradability stats from the panel cache (hard numbers)."""
import numpy as np

import config as C
import data as D

cache = D.load_cache(mmap=False)
T = len(cache["dates"])
N = len(cache["codes"])
tr = np.asarray(cache["tradable"])
print(f"面板: N={N} 只（沪深主板+创业板+科创板，剔除北交所/B股/退整理/现名ST）")
print(f"日历: {str(cache['dates'][0])} ~ {str(cache['dates'][-1])}  T={T} 个交易日")
print(f"股票数据行: {T * N / 1e6:.1f}M 格")
for label, i in [("最新交易日", T - 1), ("一年前", T - 250), ("三年前", T - 750)]:
    print(f"{label}({str(cache['dates'][i])}): 实际可交易 = {int(tr[i].sum())} 只")
am = np.asarray(cache["amount"])
print(f"最新日成交额合计: {np.nansum(am[-1]) / 1e12:.2f} 万亿元")
print(f"最小门槛: 上市≥{C.MIN_LIST_DAYS}交易日 / 价格{C.MIN_PRICE}-{C.MAX_PRICE}元 / 当日成交额≥{C.MIN_AMOUNT / 1e6:.0f}百万元")
