# QA · r2208 · CEO 页三行终于压在同一把尺子上

日期 2026-11-28 · 机 bm-c · 轮 2208 · 竞争探针 rc0 CLEAN（单宿主）

## 这一轮要回答的问题

r2207 收轮时留了两条红与一条「未清」：

1. `k_grid --check` 说「identity arm does not reproduce held/causal/ticket ticket_window cagr」，差 0.27pp；
2. CEO 页自检 475/479，其中 L228a 看到 band 表里 11-26 与 11-27 两根 bar 混在一起；
3. `band_ruler` 自称 `ROWS_NOT_COMPARABLE`，而它的三条身份臂全部 `priced_bar = 2026-11-26`。

## 根因（一条，不是三条）

CEO 页第一行「5 名·可执行单口径（本单这份账）」的数值出自 **window_label 面**
（`results/etf_book_window_label.json`），那一面停在 **2026-11-26T23:12**；另两行出自卡片面，已到 11-27。

- `python scripts\etf_book_window_label.py check` → **CHECK FAIL: the panel moved under this face -- stale:
  it priced panel fdb64c20030d2fb9, the live panel is 612e4257cd37fe8c**（它自检只重算自己，所以旧检查一直是绿的）；
- 于是页头写 11-27、第一行却按 11-26 定价：`k_grid` 拿这把残尺去对票的 2024+，差 0.27pp；
  `band_ruler` 的票臂按页面的 bar 复现，复现出 12.03 而页面印 11.76 → `IDENTITY_FAILED`，四个旋钮价格一律拒绝报价。

## 修法（自下而上，不改读数）

1. `etf_book_window_label.py run` 重 derive：last_bar / cutoff **11-26 → 11-27**，
   ticket 行 `2024+ 11.76% → 12.03%`、`full 7.32% → 7.44%`（同一条引擎，多了一根 bar），
   `check` 转 `CHECK OK: ROW_LABELED_BY_WINDOW | gap +4.59 pp/yr`。
2. `etf_book_ceo_page.py` 重发：三行 `priced_bar` 全部 **2026-11-27**，页头 `priced_bar 2026-11-27`。
3. `etf_book_band_ruler.py` 重 derive：身份门 **3/3 PASS，三条 delta 全 0.000**
   （票 12.03 / 卡片 8.94 / 卡片 2024+ 16.44，measured == published），
   判词回到 `ROWS_NOT_COMPARABLE`，四个旋钮重新可报价：
   起点 **+4.56**、股票池 **+0.43**、信号时点 **-0.26**、成本 **-0.15**（pp/年）。
4. `k_grid --check` → **rc0**，`verdict=GRID_COSTS delta=-0.28pp spread=0.45pp`，36/36 笔离开决策网格。

## 两条自检红（与上面同轮收掉）

| 腿 | 现象 | 根因 | 处置 |
|---|---|---|---|
| L75 成本带 | 「缺面/控制臂失败必须写无法核验且不许印算数」红 | **假红**：断言在整页做子串，而同一页的回购梯上另有「5 年 +5.9 bp」，与成本带无关（判据没切到它要判的那一节） | 断言切到成本带小节（`## 「每一分钱按 10bp 扣」` 到下一个 `## `），缺面时该节 length 144/147 且无算数；标题改名则切片为空 → 仍然红（fail-closed） |
| L240 | `do_or_wait` 面 `status=stale, stale_receipts=["cut_order_gap"]` | 该面把上游面字节 digest 记进 inputs，上游被重 derive 后自己就成了陈旧面（r1311 族） | `etf_book_do_or_wait.py` 重 derive → `check 13/13` |

页级自检：**479/479 PASS**（r2207 为 475/479）。

## 链腿复核（`--only`，6 腿 6/6 rc0）

```
0 etf_book_band_ruler    39.2s check OK: ROWS_NOT_COMPARABLE | window +4.56pp, universe +0.43pp, ordering -0.26pp, cost -0.15pp
0 etf_book_window_label   1.3s check OK: ROW_LABELED_BY_WINDOW | gap +4.59 pp/yr | full 7.44% / 2020-2023 3.71 / 2024+ 12.03% | 2026-11-27
0 etf_book_ceo_page      42.6s [live_book_section_bars] wrote results/live_book_section_bars.json
0 cut_order_gap           3.0s [check] 9/9 OK
0 k_grid                  1.4s [check] OK verdict=GRID_COSTS delta=-0.28pp spread=0.45pp
0 do_or_wait              2.5s check 13/13
```

## 读者今天能用的数（CEO 页）

第一行「本单这份账」：全窗 **7.44%** / 夏普 1.29 / 最大回撤 -5.78%，2020-2023 **3.71%**，2024+ **12.03%**。
四个旋钮告诉读者这张表为什么不能跨行相减：起点换一根 bar 值 **4.56pp/年**，比「股票池」「信号时点」「成本」三者之和还大。

## 诚实未清（下一轮）

- `live_book_section_bars` 判 **PAGE_MIXES_BARS**：75 个带日期的小节只有 35 节真在 11-27，
  最旧停在 **2026-11-17**（`alias_census`，落后 8 个交易日），另 3 节根本没有日期。这是页内代差，本轮未动。
- 全量冒烟未跑（~950s 超轮预算）；红数**不宣称下降**——上表只证明本族六条腿与页自检 479/479。
- `etf_book_band_ruler` 的判词 `ROWS_NOT_COMPARABLE` 是它的**正常态**（三行本来就不同尺），不是缺陷。
