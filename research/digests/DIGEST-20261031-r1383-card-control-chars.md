# DIGEST 2026-10-31 r1383 bm-c — 卡片账本的控制字符：登记过的腐蚀类无人读，等于没登记

**一句话**：r1380 查明账本里有 7 个控制字符并写下「本轮不修」，之后没有任何机制去读它；
本轮回补全部 7 处，并把「会读它」变成一条 smoke 腿 + 一个带冻结表与行级断言的工具。

## 事实面

| 站点（原文） | 现文 | 证据 |
|---|---|---|
| `落 \x08reak_guard` | `落 break_guard` | `scripts/e39_panel_census.py` 定义 break_guard |
| `断言 \x07bs(ser.iloc[0] - 1.0)` | `断言 abs(...)` | 有符号序列上 abs() 是唯一读法 |
| `只改主面 \x1btf_breadth_sweep.py` | `etf_breadth_sweep.py` | 文件在盘 |
| `out of \x1btf_book_production.run()` | `etf_book_production.run()` | 文件在盘 |
| `publishes \x08book_decided_at` | `book_decided_at` | `scripts/etf_book_order.py` 输出该键 |
| `\x1btf_vol_delivery_audit.py --selftest` | `etf_vol_delivery_audit.py` | 文件在盘 |
| `Here \x08urncontrol` | `Here burncontrol` | `scripts/e110_burncontrol_close.py` 等 7 源拼 burncontrol |

- 控制字符字节分布：0x08×3 / 0x07×1 / 0x1b×3；账本 UTF-8、无 BOM、纯 LF（726,177 B）。
- 修复后：411 个 corpus 文件（账本 + 全部 digest）**0 处**控制字符。
- `git diff --numstat` = **7 行 +/7 行 −**，其余字节不动（工具内行级并集断言复验）。

## 为什么「记录」不算处理

r1380 的轮报告与卡片都写了这件事，落到了账本里，然后——没有读者。这正是
「自学习转化律」的反面案例：一条发现只有在**有机器会因为它红**的时候才算被接住。
本轮因此不满足于改字：`Tools/card_text_hygiene.py` 的 `scan` 就是那条机器，
smoke 腿 `config: no card or digest carries a control character` 每轮跑它，
且腿与工具共用同一 corpus / 同一字符集（抄一份规则=下一个缺陷）。

## 工具要点（selftest 11/11）

- **冻结表 + proof**：每条修复都带证据（文件名或代码里真实使用的标识符），
  表外一律不猜。
- **恰好一次**：0 次或 2 次 = exit 2 且零写（歧义不修）。
- **行级并集断言**：行数不变 + 变动行集合恰好等于修复行集合 + 每行内可逐字逆向复原。
  三条都过才写盘。
- **treasure_guard**：对本面 prescan rc3 硬拒（登记簿命中）。这是设计如此——登记簿
  的合法通路只有行级并集或摘录存旁，本工具即那条通路，并落 `results/card_text_hygiene.json` 回执。

## 首版自踩

行级校验最初用全文件 `find(restored)` 做逆向，遇到 `book_decided_at` 这类在账本里
多次出现的标识符就找错位置，健康文件被自己的断言判红（exit 3）。改为**按行复原**后
通过。规则同 E300：同一个词在多处出现时，不能用全文件搜索当身份。

## 未修 / 待办

- corpus 只覆盖 `knowledge/*.md` 与 `research/digests/*.md`；`research/*.md`、`docs/` 未纳入，
  扩面前须先量假阳性。
- 被吃掉中间字母或整段截断的形态，scan 能看见但冻结表没有对应行——属人判范围。
- 供给面仍未解决：`fill_ladder --dry-run` 报 `compatible_ready=0 floor=3`，catalog 23 条全消费，
  唯一 blocked 行是已判负的 INNOVATION-QUOTA-SLOT-3。真供给须写新家族（prereg + runner +
  G-ANCHOR 预验），是下一里程碑而不是本轮。