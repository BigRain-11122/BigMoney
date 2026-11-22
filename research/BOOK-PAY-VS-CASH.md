# 扣完搜索租金，这本书比躺着赚利息多多少
> 由 `scripts/book_pay_vs_cash_ruler.py` 渲染，数字不手抄。`generated 2026-11-23T03:35:17+0800`，`cutoff 2026-11-20`（parent window end (parent carries no cutoff field)）。
## 一句话
按 58 次尝试扣完租金，这本书比躺利息多 ￥237/年（0.024 个百分点），而它一年内 5% 概率的尾部回撤是 19.1%——超额是估计宽度的量级，不是边的量级。
## 两半都印出来
| 读法 | 年化 | 在 ￥1,000,000 上是 |
|---|---|---|
| 标题（不扣租金，父面原样） | 11.16% | ￥111,600 |
| 扣租金（N=58 次尝试） | 1.801% | ￥18,007 |
| 躺利息（回购净利率） | 1.777% | ￥17,770 |
| **超额（扣租金 - 躺利息）** | 0.024% | **￥237** |

## 代价
* 一年内 5% 概率的尾部回撤：**19.09%**（￥-190,919）。
* 要靠超额把这一个坏年补回来，需要 **806 年**。

## 反面问题：审计多少次它才值得上
只有当「为找这本书花掉的独立尝试次数」不超过 **58 次**时，扣租金的年化才仍高于躺利息。本司机械可数的三次审计是 58 / 123 / 450 —— 都在这条线之上或之上沿。

## N 阶梯（同一套算术，格子自洽）
| 尝试次数 N | 可信夏普 | 可预算年化 | 相对躺利息 | ￥1,000,000 上的差 | 过线 |
|---|---|---|---|---|---|
| 2 | 0.8939 | 9.386% | 7.609% | ￥76,089 | 是 |
| 5 | 0.6257 | 6.570% | 4.793% | ￥47,929 | 是 |
| 10 | 0.4735 | 4.972% | 3.195% | ￥31,947 | 是 |
| 20 | 0.3436 | 3.608% | 1.831% | ￥18,308 | 是 |
| 40 | 0.2285 | 2.399% | 0.622% | ￥6,222 | 是 |
| 55 | 0.1794 | 1.884% | 0.107% | ￥1,067 | 是 |
| 58 | 0.1715 | 1.801% | 0.024% | ￥237 | 是 |
| 100 | 0.0926 | 0.972% | -0.805% | ￥-8,047 | 否 |
| 200 | 0.0000 | 0.000% | -1.777% | ￥-17,770 | 否 |
| 450 | 0.0000 | 0.000% | -1.777% | ￥-17,770 | 否 |

## 现金腿的取证
* 发布值：`cash_net_annual=1.777%`（来源 results/capital_placement.json，`generated 2026-11-22T19:20:03+08:00`，`cutoff 2026-11-20`）。
* 面板复核：GC001 在本书面窗口内日度年化利率均值 **1.974%**（1667 天，2020-01-03→2026-11-20），与发布净值差 0.197pp → **CROSS_CHECK_OK**。差额=佣金与窗口不同源，披露不调和。
* 次查：GC007 同窗均值 2.071%。
* 最新报价：2026-11-20 GC001 收盘 1.395%（年化）。

## 不许只挑一边信
* the deflation is a haircut, not a posterior: the headline row is printed beside the deflated row so neither reading is hidden
* cash_net_annual is one published rate carried on the placement face; a real parking programme re-quotes daily and its realised carry moves
* the book is fully invested, so no idle cash earns this rate inside it -- the comparison is 'this book' vs 'the same money parked'
* excess is computed on the parent's published volatility, so a regime change moves both the pay and the tail
