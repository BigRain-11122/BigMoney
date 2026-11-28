# 同一笔钱，两种做多：一手期货换掉多少 ETF 底仓

- 判词：`BETTER_PER_YUAN_BUT_NOT_BUYABLE_AT_THIS_CAPITAL`
- 证据时点：2026-11-26（逐面时点见 JSON `face_cutoffs`）
- 问的人：1,000,000 元账户

One hedged IC lot risks 92,768 CNY a year = 116.0% of the 8% budget on 1,000,000, the same risk as 88.3% of the ETF book. Per yuan it needs (1,159,599), the lot returns 9.62% against 8.00% risk (Sharpe 1.20) while the ETF book returns 10.89% against 10.51% (Sharpe 1.08). That rung is 1.16x this capital, so the swap is not buyable today.

## 三把尺（同一手，三种算法）

| 产品 | 对冲后年波动(元) | 占 8% 预算 | 等价 ETF 仓位 | 首档资金(元) | 每元收益 | 每元波动 | 每元夏普 | 每元判 |
|---|---|---|---|---|---|---|---|---|
| IC | 92,768 | 116.0% | 88.3% | 1,159,599 | 9.62% | 8.00% | 1.20 | CARRY_BETTER |
| IM | 93,600 | 117.0% | 89.1% | 1,169,997 | 10.82% | 8.00% | 1.35 | CARRY_BETTER |

对照：ETF 复合书 None —— 年化 10.89% / 波动 10.51% / 夏普 1.08 / 最大回撤 -10.56%（时点 2026-11-26）。

## 怎么读这张表

- **风险预算才是那把有否决权的尺**：8% 是预算，不是目标。一手 IC 占掉 116.0%，即一手就超过整个预算——这就是 sizing 面印 0 手的算术原因，不是保守。
- **名义口径不回答问题**：一手名义 1,275,000 元，是 ETF 底仓权益腿的数倍，所以「替多少」只能按风险或按资金算，不能按名义。
- **每元口径给的是另一件事**：一旦资金到 1,159,599 元，这一手的每元夏普 1.20 对 ETF 的 1.08；资金不够时它是「更好但买不起」，不是「不该买」。

## 诚实边

- Ruler A reads the sizing face's own hedged-vol figure; ruler C multiplies the risk face's ann_vol by the same notional. They differ by -18.9% on IC (different windows) and are printed side by side, never averaged.
- The ETF book's vol is its measured 8%-target implementation (it de-levers only), not the 8% target itself.
- Replacing the ETF core also removes its bond/cash defensive leg; this face prices risk and return, not the drawdown path in a crash.
- One lot is a discrete jump: there is no partial lot below the first rung.
