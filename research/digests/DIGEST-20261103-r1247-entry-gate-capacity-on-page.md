# DIGEST-20261103-r1247 · 入场闸的读数上了读者面：这个门槛不是收益来源，是容量来源

轮次 r1247 · bm-a · 研究/工程 · evidence_cutoff 2026-10-30（面板末根 bar）· 2026-11-03T04:1x +08:00

## 1. 产品：操作者页新增一节「这本书的票池是被一个数选出来的，那个数是从哪来的？」

r1246 量出了那道闸的判决（`GATE_SITS_ON_PLATEAU`），但它只活在 `research/ETF_BOOK_ENTRY_GATE.md`
与 `results/etf_book_entry_gate.json` 里——读这一页纸的人不会去翻研究档，所以对他来说这个
20M 仍然是「继承来的」。本节把它接上读者面，并且**不重算任何数**：`entry_gate_face()`
读已发布的六行，用被扫面的**同一个 `classify()`（import，不是第二份实现）**当场把判词
重算一遍；存盘判词与重算不一致 → `drifted`，页面印「这一问答不了」，不印平台。

页面现在印两件事、并排：

- **收益这一轴是平的**：砍一半或翻一倍，年化只动 ±0.53 pp（判据 1.0 pp 内），最好的那一档
  也只多 +0.21 pp → 「20M 不是一个结果，是一段平台，可以是任何人的默认值」。
- **宽度这一轴不是平的**：同一个门槛从最松到最紧，可选名数中位从 **462 只**掉到 **56 只**
  （8.2 倍）→ 「这道闸不是你的收益来源，**它是你的容量来源**」。

第二句是**从行里算出来的**（`width_ratio ≥ 2.0` 才印），不是写死的文案：页面自己的自检
（L140）用一份宽度不收窄的夹具证明，行不宽时这句话必须消失。

## 2. 拒绝条件随面上移

搬一次敏感性扫描到读者面，最容易丢的不是数字而是**拒绝条件**——研究档里写着「控制臂复现
不了就 CANNOT_JUDGE」，而页面如果只抄结论，就变成了「陈旧 payload 最像权威的地方」。
本面把三条拒绝一起搬上来，各有自检腿：

| 拒绝 | 触发 | 腿 |
|---|---|---|
| 无控制臂 | `control.delta_pp is None` | L139 |
| 控制臂复现不了已发布格 | `abs(delta_pp) > tol_pp`（0.25pp） | L139 |
| 存盘判词与自己的六行不一致 | `classify(rows) != stored` | L138 |

## 3. 落地的遗产（机检后落账，非信摘要）

轮首树里躺着前一窗做完没提交的**现金腿三个口径上页**（`cash_money_face` /
`cash_money_block`，L133-L137，`docs/live_book` 的「同一笔现金，三种利率口径差多少钱」）。
本窗不信它的自报：`etf_book_ceo_page.py selftest` 实跑 **140/140 PASS** 之后才随本轮一起入 git。

## 4. 验证

- `python scripts/etf_book_ceo_page.py selftest` → **143/143 PASS**（新增 L138/L139/L140）
- `python scripts/etf_book_ceo_page.py run` → LIVE-BOOK 重生成，新节在盘（正文核对过表行与两句判词）
- 全量 smoke **见轮报告**（含新腿 `product: the operator page says the entry gate sets capacity, not return`）
- `orders_ack` CLEAN 114/123/0 ｜ D-19 MATCH（decisions 未变，零新行零动作）｜ attrition CLEAN 4 账本
- 孤儿面 0（`results/_orphan_face_probe.bm-a.json`）

## 5. 没做的事（如实）

- 卡片（`results/etf_book_production/CARD.md`）与可执行单**尚未**印这条读数，本轮只上了操作者页；
  两面口径对齐是下一指针。
- 供给地板仍 **AGENDA_DEBT**（startable 0 / shortfall 3）：引擎 idle 是缺活不是缺产能。