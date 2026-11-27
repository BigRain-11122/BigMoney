# QA · three_book_wallet_ride · r2204 (bm-c)

面：`results/three_book_wallet_ride.json` · 页面：`research/THREE_BOOK_WALLET_RIDE.md` ·
脚本：`scripts/three_book_wallet_ride.py` · 证据截止：2026-11-26

## 本轮主张（逐条可复核）

| # | 主张 | 证据 | 判定 |
|---|---|---|---|
| 1 | 钱包臂 65/35/0 逐位复现父面 `best_inside_gate`（cagr / sharpe / vol / maxdd，容差 5e-6） | `run` 输出四行 identity 全 OK；`results/three_book_wallet_ride.json → identity_vs_parent` | PASS |
| 2 | 窗口 = 父面窗口（1670 bar），不是今天的面板 | `window.bars=1670` == `three_book_wallet.json.window.bars`；`identity_bars_match=true` | PASS |
| 3 | 1 年期起数 = bars − hold + 1（1421 = 1670 − 250 + 1） | `arms.wallet.hold.1y.starts=1421`；smoke 谓词第 4 问按此逐档核对 4/4 | PASS |
| 4 | 判词由印出的数字推出（pct_losing=4.2%>0 且 p90/p10=12.15≥3 → 区间判词） | `check` 重算 verdict 与面一致 rc0；负控（改判词）rc2 | PASS |
| 5 | 今天是整窗最深一格这件事有独立复核 | 另起一段脚本独立算 `eq/peak-1`：min=-0.067237 @2026-11-26（最后 bar），与父面 maxdd 逐位相同 | PASS |
| 6 | 自检 13 腿全绿，含 4 条行为腿（漂移→STALE、真矛盾→CHECK FAILED 且不戴 STALE、负控、分位失序） | `selftest` 13/13 | PASS |
| 7 | 链腿接线且只读不重写 | `Tools\s6_chain_bmc.py 2204 --only=three_book_wallet_ride` → 1/1 rc0，0.7s（check 绿时零 run 成本） | PASS |
| 8 | 冒烟腿能吃住「面与页面不一致」 | `three_book_wallet_ride_problems()` → `[]`；负控改 `today.hole` → 立即报 2 条 | PASS |

## 未做 / 不宣称

- 全量冒烟（~1000s）本窗未跑；只跑了本面自己的判定函数与负控。
- S6 全链 388 腿未整跑，只跑 `--only=three_book_wallet_ride` 一条验接线。
- 四条臂的波动不同，页面只允许「区间宽度按自身 sigma」这一种横向读法，绝对区间不可相减；
  这一点写进了页面正文与 `not_claimed`，不是注解。
- 本面是 2020-2026 的**样本内**路径形状，不是对 2027 年的预测。

## 复跑

```
python scripts\three_book_wallet_ride.py run
python scripts\three_book_wallet_ride.py check     # 上游动=STALE(rc3) / 自相矛盾=CHECK FAILED(rc2)
python scripts\three_book_wallet_ride.py selftest  # 13/13
python Tools\s6_chain_bmc.py 2204 --only=three_book_wallet_ride
```
