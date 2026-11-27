# QA — cb_union_lens r2187 (2026-11-27)

## 面是什么
三本「各自说开得动」的书（ETF 复合书 / 转债双低袖 / 指数期货 carry 书）在同一只 1,000,000 元
钱包下的联合口径：每本占多少钱、2^3 组合里哪些能同时开、开不动的那本差多少钱。

## 为什么是新产品面（不是重复）
`results/capital_union_decision.json` 立判词 `ETF_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY`
时，转债双低袖尚未入册（该面只含 `etf_book` + `carry_book` 两段）。今天 `cb_book_ticket_floor`
已经在 1,000,000 档印 `BUYABLE`（投入 991,053.20）——旧判词不再成立。本面就是把这条缺口补上，
不重算任何回测、不重新定价任何标的。

## 结论（今日，钱包 1,000,000）
| 书 | 占用 | 占钱包 | 票面判词 |
| --- | ---: | ---: | --- |
| ETF 复合书（去债 + 8% 波动目标） | 750,475.30 | 75.05% | FITS |
| 转债双低袖（20 名等权） | 991,053.20 | 99.11% | BUYABLE |
| 指数期货 carry 书 | 0.00 | 0.00% | WITHDRAW_FROM_TICKET |

- 判词 `TWO_BOOKS_CONTEND_FOR_THE_SAME_WALLET`：两本合开需 1,741,528.50 元，比钱包多 741,528.50。
- 采纳常量 `adopted_book_today=cb_book`（口径＝占用/钱包高者），备选数字不删、可复核。
- carry 书开最便宜的 IC 腿需 1,137,862.50 元（差 137,862.50 = 13.79%）。

## 验收
- `python scripts\cb_union_lens.py selftest` → **5/5 PASS**（含两条负控：采纳占用低的那本必须变红；
  篡改 stranded 恒等式必须变红；缺面不崩并印原因）。
- `python scripts\cb_union_lens.py run` → check **22/22 ok**，rc=0。
- `python scripts\cb_union_lens.py check` → `{"ok": true, "legs": 22, "failed": []}` rc=0。

## 诚实的缺口
1. 三张输入面的成本假设不一致：ETF 书每腿 5 元最低佣金已计，转债袖阶梯面未含佣金，carry 书按 8% 硬上限。
   组合合计因此是两个口径相加，只作「能不能开」的算术，不作成本预算。
2. `capital_union_decision.json` 没有自印 `generated`（只有 `evidence_cutoff`）——本面对该段标
   `generated_source="file-mtime (parent does not print one)"`，不冒充面自印。
3. 未接线：无 S6 链腿、无冒烟腿（本轮 `repo_write_contention` rc=3 CONTENTION，禁改共享面）。
   欠账已写进 state `carrier_debt_r2187`，等共享面空出当轮补。
