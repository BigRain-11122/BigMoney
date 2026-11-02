# DIGEST 2026-11-02 · r1243 bm-a · 空心 bar 的账要记在台账里

**一句话**：覆盖率闸已经把 2026-11-02 那根只有 5 个收盘价的空心 bar 拒掉了，但**拒绝本身没有
留下任何痕迹**——于是「序列比书多一天」（判 0 = 没滞后）、「台账最后一根是幻影 bar」（永久
provisional）、「三面同一本书记了两个面板」三件事同时挂在盘上。正法不是改断言，而是让闸的自报
进入产物、让「序列走在书前面」变成可治愈的 lag（-1），并给幻影 bar 一个**带痕迹的撤回**。

## 现场（继承窗，机检复核）

上一窗（21:2x 死亡）留下的三条红：

1. `the book envelope says whose book it describes | series 2026-11-02 vs book 2026-10-30
   | same_object 0.0959 vs 0.096` —— 序列面在空心 bar 上 bootstrap，与书差 0.01pp，
   判词居然是 `same_object`（容差 0.25pp 把它盖住了），**真正对不上的证据是 cutoff，不是幅度**。
2. `three faces of one book price one panel | 2 panels: a1a42aee / dba12856` —— 台账的面板块
   还是加闸前那次构建（5271 根，到 11-02），卡的 5270 根到 10-30。
3. `dashboard says which bar the three papers were priced on | card 2026-11-02 != reader 2026-10-30`
   —— 总控面板读的是旧的 reader 面。

## 改法（四条，都在判据层）

1. `scripts/etf_composite_pf.py`：`drop_hollow_tail()` 的拒绝写入模块级 `PANEL_TAIL`
   （拒了几行 / 被拒的日期 / 参照覆盖 / 地板），`build_panel` 每次重置。
   **静默丢弃与「源丢了一天」在盘上长得一模一样**，这条就是让它们不再一样。
2. `scripts/etf_book_forward.py`：`_panel_block()` 增写 `refused_trailing_rows` /
   `refused_last_bar` / `coverage_floor` / `reference_coverage`——台账自己说清楚它拒了哪一根。
3. `scripts/etf_book_forward.py` `series_lag_bars()` 由单边改**符号三态**：
   `+1` 落后 / `-1` **超前** / `0` 同日 / `None` 未知。原实现 `>=` 直接返回 0，
   于是「序列多一根书买不到的 bar」被读成「没滞后」，envelope 照旧 bootstrap 那根幻影 bar。
   `run()` 现在对两个方向都付 refresh，并打印 `direction=behind|ahead`。
   selftest L30 也一并改（该腿的注释写着「lag reads both ways」，断言却只实现了一边）。
4. `scripts/etf_book_forward.py` 新增 `withdraw_provisional()` + `published_bars()`：
   `restate_provisional` 只覆盖「面板还在长、之后定格成另一个数」这一种结局；另一种结局是
   **那个日期从来不是可定价的会话**（空心 bar，闸事后把它拒了），它的 face 永远是 `missing`，
   于是它永远是最新的已发布 bar → 后一根真 bar 也被连带判 provisional → 台账再也合不上一根。
   正法：撤回一次、留痕（保留 published nav/dd/cash + 原因 + 面板末日），`withdrawn: true`
   之后退出 settled/provisional 分区（`published_bars()` 单一读器，settle audit 同源 import）。

## 读数

- 序列：`NAV-2026-10-30`（1652 根，cagr 9.60% / Sharpe 0.99），与生产 cell `n12_vt08` 9.60%
  **逐字相等**；envelope 判词句自带「these are the published book's own numbers」。
- 台账：`panel` = 5270 根 / last_bar 2026-10-30 / digest `a1a42aee64453839`（与卡、票同面板）+
  `refused_trailing_rows: 1, refused_last_bar: 2026-11-02, reference_coverage: 1611`。
  `WITHDRAWN 2026-11-02` 一行入 `restatements`；headline 回到 `2026-10-30 nav=1.0085993056`。
- settle audit：`run` → `no_drift`，`check` → `stored=no_drift fresh=no_drift MATCH`（rc0）。
- 链：`--only` 七腿全 rc0（production / return_regime / order / order_card / ceo_page /
  daily_report / build_status，`results/_r1243bma_s6_chain.only-*.json`）。

## 教训

- **一个「差」的度量如果只在一侧符号上取值，它就不是度量**：`>= 0` 把「超前」写成了「没有」，
  而超前那一侧恰恰是幻影 bar 唯一能被抓到的地方。
- **闸的拒绝必须被印出来**：`drop_hollow_tail` 已经在拦，但拦得静默；产物里没有「拒了哪一根」，
  下游就只能用「面板少了一天」去猜「数据丢了」，而这两件事的动作方向相反。
- **撤回 ≠ 删除**：published 值留在 record 里，加 `withdrawn` 与原因；分区只认 `published_bars()`，
  于是一根幻影 bar 只会被处理一次，而不是每轮重新喊一遍（E275/E318 同族的「永久红」）。
- 判 `same_object` 的容差不能替代 cutoff 恒等：0.01pp 的「一致」是两个不同对象的一致，
  真正该红的是 `evidence_cutoff`。