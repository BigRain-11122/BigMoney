# DIGEST 2026-11-09 r1470 — 账本上了 CEO 那张纸

## 一句话

r1468 写下执行后的账、r1469 让它逐 bar 计息，但这本账只活在 `results/etf_book_positions.json`；
CEO 页仍以「如果你今天才建仓」卖整张单——**账面上已经有 4 只票和 ￥607,599 现金，纸上却说一股没有。**

## 做了什么

`scripts/etf_book_ceo_page.py` 新增 `positions_face()` / `positions_block()`，把账本面接进今日实盘页
（位置在下单表/额度/溢价/价差之后，现金对账之前），每天 regenerate 时自动带上：

- 账本自己的账：风险腿 ￥392,401 / 现金 ￥607,599 / 持 4 名（2026-11-06 收盘）+ 逐名手数表
- 票面换仓行 3 行 vs 账本 4 行 → **￥67,289** 是「该卖却没印出来」的份额
- 下一张单从账本起算 vs 从纸起算差 **￥381,115**（被裁掉的 444/426 手已换成 920 手兄弟票）
- 20 bar 回放：腿 -6.00%、现金息 ￥563.81、两半与净值恒等
- 现金腿利息 `NO_NEW_BAR` → 「今天没有新 bar，还没有新的利息入账」（不是零利息）
- 与引擎账 k 差 0.067852 = ￥67,852 名义额：执行账按额度裁过，引擎账没裁

## 三条可复用

1. 面存在 ≠ 面被读——产出面之后第一问「谁读它」。
2. 读者面要能被一句话证伪：smoke 腿从面重新 derive，不对字面量断言。
3. 缺面=「无法核验」，不是「没有」；`NO_NEW_BAR`=「还没有一天的账可记」，不是零利息。

## 验证

- `python scripts/etf_book_ceo_page.py selftest` → **161/161 PASS**（新增 L158–L161）
- `python scripts/etf_book_ceo_page.py run` → 页已再生（bm-c 声明接管，bm-a 心跳静默 40.1h）
- `python scripts/etf_book_positions.py check` → CHECK_OK
- `python scripts/etf_book_cut_order_gap.py check` → 7/7 OK（消费者名单未漂移）
- 新 smoke 腿单独手测通过；全量套件本轮未跑完，不宣称全绿

## 未做

- 订单页（ORDER-*.md）尚未带同一节账（r1469 的下轮指针要求两页都有）
- 生成侧 `etf_book_order` 仍按自己的引擎账推进，￥67,852 的分叉会随每个决策 bar 复现
