# 同一笔 100 万，两本书各要多少钱才能开

> 由 `scripts/capital_union_decision.py` 生成，禁手改。各面自印 cutoff：

- `carry_open_capital` = 2026-11-23
- `etf_book_capacity_edge` = 2026-11-24
- `etf_book_ticket_floor` = 2026-11-24

**判词** `ETF_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY` / 最弱面 cutoff = 2026-11-23

## 一行话

> At 1,000,000 CNY the ETF book is open (one lot 14,666.23 CNY, 68.2x the floor) while the carry book prints 0 executable lot(s) and needs 1,129,566 CNY to open its cheapest leg (short 129,566 = 12.96%). Today's ETF capacity line sits at 1,043,801 CNY (reading 0.9580% of ADV against a 1.00% line), so this capital fits with 43,801 CNY of headroom on the best day of the last 60 sessions. Opening both at once needs 2,173,367 CNY on the best capacity day (1,626,042 on the median day).

## 两本账并排

| | ETF 复合书 | 股指期货贴水 carry |
|---|---:|---:|
| 100 万下能开 | 是 | 否 |
| 一手/首档门槛 | 14,666.23 CNY | 1,129,566 CNY |
| 差多少 | — | 129,566 CNY（12.96%） |
| 今天这一档容量读数 | 0.9580% ADV（闸 1.00%） | — |
| 100 万在容量线上的余量 | 43,801 CNY | — |

## 两本一起开要多少

- 最好的一天容量档：2,173,367 CNY（carry 首档 + ETF 容量线资本）
- 中位的一天：1,626,042 CNY

## 口径与限制

- The ETF capacity reading is a 60-session ladder of 20-day median ADV, not an order-book measurement: it says how often this capital fits, not how much it costs to push.
- etf_book_ticket_floor is a whole-lot arithmetic face and its cutoff can lag the capacity face; every face's own cutoff is printed in face_cutoffs.
- The carry book's funding rung comes from the adopted 8% hard cap; the un-adopted road (lower target to 8.9958%/9.2208%) is printed on that face and is not applied here.
