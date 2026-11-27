# 这张单的两个词：整手可下 vs 许不准持有（etf_book_permission_vs_size）

证据截止 **2026-11-26**；判词 **SIZE_IS_THE_ONLY_KNOB**。题：同一档上，改尺寸能不能把年份检验买回来。

## 一句话

- 在 2026-11-26 这一档，同一张 ¥1,000,000 的单有两个词：整手面读 **TRADABLE_AT_1000000**（5 名各至少 1 手、残差 0.1266% NAV），供给闸读 **ADMIT**（唯一没过的是 （闸没写哪条））——前者数的是 100 份一手，后者才是「这本书准不准持有」。
- 本条要回答的是「改尺寸能不能换来许可」：从 250,000 到 4,000,000，两年份额恒为 73.78%（线 70.00%），到线的距离恒为 -9.84pp——换成本金只是同一段距离值不同的钱（-34,753 → -556,051），所以**缩放这张单不会让判词翻面**。
- 要翻面，改的是**年形状**不是本金：2025 那一年少 9.84pp，换成当时 100 万本金上就是 -139,013 元，top-2 才回到线下——这与「等几年再说」是两件事，也与「买小一点」是两件事。
- 哪张回执说话：**etf_book_wrapper_year_gate**（cutoff 2026-11-26），因为它读的是这张单所在的那一档；etf_book_partial_year_caliber 也留着，但它回答的是另一个问题（换口径会不会换词）——在三种口径下这本书都读 ADMIT，所以它没有资格把词改回 ADMIT。

## 两张回执，各带自己的日子

| 回执 | 回答什么 | 它读的那一档 | 它说的词 | 出处 |
|---|---|---|---|---|
| etf_book_wrapper_year_gate | what word does the object the desk executes get on this close | 2026-11-26 | ADMIT | `results/etf_book_year_gate/WRAPPER-GATE.json` |
| etf_book_partial_year_caliber | does swapping the partial-year caliber change the word | 2026-11-06 | CONDITIONAL | `results/etf_book_partial_year_caliber/CALIBER.json` |

采纳规则：the receipt reading the executed object on the close the ticket is priced on outranks an older reading, and an older reading that answers a different question cannot outrank it。

## 表一：份额不随本金动，钱随本金动（现算 5 档）

| 本金 | 最好一年 | 该年收益 | top-2 份额 | 到线的距离 | 该距离值多少钱 |
|---|---|---|---|---|---|
| 250,000 | 2025 | 43.06% | 73.7818% | -9.8433pp | -34,753 |
| 500,000 | 2025 | 43.06% | 73.7818% | -9.8433pp | -69,506 |
| 1,000,000 | 2025 | 43.06% | 73.7818% | -9.8433pp | -139,013 |
| 2,000,000 | 2025 | 43.06% | 73.7818% | -9.8433pp | -278,026 |
| 4,000,000 | 2025 | 43.06% | 73.7818% | -9.8433pp | -556,051 |

自证：份额恒等=True / pp 恒等=True / 金额线性=True（每 100 万值 -139,013 元）。

## 表二：同一批本金进整手面，词会变（这才是尺寸管得着的地方）

| 本金 | 整手判词 | 残差% NAV | 装不下的名字 |
|---|---|---|---|
| 250,000 | TRADABLE_AT_250000 | 0.396 | 无 |
| 500,000 | TRADABLE_AT_500000 | 0.2535 | 无 |
| 1,000,000 | TRADABLE_AT_1000000 | 0.1266 | 无 |
| 2,000,000 | TRADABLE_AT_2000000 | 0.0751 | 无 |
| 4,000,000 | TRADABLE_AT_4000000 | 0.03 | 无 |

## 诚实话（逐条）
- 本面不动任何判词：许可词以 WRAPPER-GATE 为正身，整手词以 etf_book_ticket_floor 为正身，本面只把它们并排印出来并量「尺寸能不能换许可」。
- 两个词都不是「能不能赚」：CONDITIONAL 说的是这本书的年份集中度超过了自己的线，TRADABLE_AT_1000000 说的是 100 份一手买得进去——两个问题都不是收益预测。
- 份额在本金上是恒等的，因为它是「年收益 ÷ 全期总赚」的比值；金额是本金的线性函数。表里 5 档都是现算的（build(capital=…)），不是把 1 档乘出来。
- 整手面随本金会换词（表二），这正说明「尺寸」只对整手摩擦有话语权：把它当成许可旋钮就会读出一个假的通过。
- 年集口径含部分年（本批 2026），已由源面逐行标注；本面不改口径。
- 本面口径截止 = 源面截止：2026-11-26。若源面推进而本面未重跑，本面的 cutoff 会落后——check 会先说 STALE。
