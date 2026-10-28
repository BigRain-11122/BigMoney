# E201 — 符号约定只活在生产者脑里：14 张分解族面 14 张全部未声明

- 轮次：bm-b r1230（2026-10-29 02:0x）
- 证据面：`results/e79/DELTASIGN-2026-10-27.json`
- 代码：`scripts/e97_routing.py`（`deltasign`，selftest 61→70）
- 上游：E193 delta 构建立场扫描（同模块 `deltastance`，不重复实现）

## 问题

E193 量到了：这个族所有能重建的 delta 都只是 `raw − screened` 构造的**负值**，
即面面都是 `screened − raw`，而 30/30 细胞没有一个在面里写下来。E201 的问题是
读面文字能不能学到这条约定。

## 结果

**判决：`every_face_leaves_the_convention_unstated`**

| 状态 | 面数 |
|---|---|
| silent（文字里没有任何方向声明） | 14 |
| declared_and_matches（声明且与数字一致） | 0 |
| declared_but_contradicts（声明与自家数字相反） | 0 |
| states_two_directions（两种方向都写了） | 0 |

每张面都附一行 `line_to_add`，例如：

> sign convention: every delta on this face is screened minus raw
> (d = screened - raw); a positive d means the screened reading is the higher one

## 三条可复用判据

1. **「没说」是可测的**，不用猜：把面的 prose 块（spec/honest/notes/reading/
   method/class_rules）拼成一段文字，用两条互斥的正则读方向，读不到=`silent`。
   这比「我觉得它没说清」强，因为它逐面出结论、逐个给待补句。
2. **声明与实测必须分开量**：实测来自 E193 的构造匹配（`flipped`=screened−raw），
   声明来自文字。两者一交叉就多出两种真实缺陷——`declared_but_contradicts`
   （文字写反了自家数字）和 `states_two_directions`（两种都写了等于没写），
   这两类都是只看数字或只看文字都发现不了的。
3. **零 bp 成本的缺陷也是缺陷**：这条不影响任何数字，但影响整条符号——读者照
   面名理解会把方向读反，而且没有任何一页纸能纠正他。修法给出待补句即可，
   本轮不改任何已发布数字（只加一条面）。

## 诚实边界

- 本面只判「文字有没有声明」，不改任何数字；建议句是提案，不落地面。
- 实测约定继承 E193 的构造匹配，E193 匹配不上的面如实记 `unmeasurable`，
  不假设。
- 两种方向都写出来的面记 `states_two_directions`，不硬挑一个算匹配。