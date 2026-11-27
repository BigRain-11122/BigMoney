# 两个流动性面停在一周前的面板上，而且它们的 check 说不出口

r2167（2026-11-27）。修的是**契约**，不是数字：这两张面一直没有「外面动了」这个概念。

## 一、病灶

`scripts/etf_book_liquidity_select.py` 与 `scripts/etf_book_liquidity_era.py` 都在
`results/` 里发布了一张面，链里各自有写者腿（`liquidity_select_write` /
`liquidity_era_write`）。它们的 `check()` 只做一件事：把**自己发布的行**拿回来重算
一遍减法/分区。这种检查有一个永远成立的性质——**只要没有人重跑写者，它就一直绿**
（r1935 族在两张面上的第 N 次实例）。

实测：两张面的 `evidence_cutoff` 停在 **2026-11-19**，而 core48 面板当时已经在
**2026-11-26**；`check` 依然打印 `{"ok": true, ...}`。

为什么链不去重修它：`Tools/s6_chain_bmc.py::run_leg` 只在探针文本里出现 **stale**（或
"face missing"）时才付钱跑写者。这两张面的源码里连 `stale` 这个词都没有——
`chain_contract_word_audit` 把它们列在「结构风险」里，`drift_words` 一栏是**空的**：
它们连"上游动了"这种话都不说。

## 二、修法（两件面同一把尺）

1. **写者记录它定价的是谁**（`inputs`）：
   - `panel_last_bar`：跑面那一刻，冻结 core48 的 48 个 CSV 尾行取最大日期（**0.3s**，
     对比 `S.nobond_universe()` 重建面板的秒级成本——这就是"能便宜问的问题"）；
   - `gate`：这张面的「每名需求 = 每名仓位 / 1% 线」是从门面读来的，所以门面的
     `line_frac` / `lens_cny` 也一起记下（`EC.load_gate()` 是一次 JSON 读）；
   - `data_end`：这本书实际算到哪一根（信息位，不参与判词）。
2. **检查先说"外面动了没有"**（`drift()`）：
   - 面板滚了一根 bar → `check STALE: ...` **rc3**；
   - 门面重发了标尺（line/lens 变了）→ 同样 rc3；
   - 面里根本没记锚 → 也 rc3（"不知道在跟谁比"不等于"我很好"）；
   - 锚一致、但发布出来的数字自己重算不出来 → `check FAIL:` **rc1**，且这一行**不带
     STALE**（r1934 双词判例：缺陷不许去骗一次重建）。
3. 顺手补一处自相矛盾：`era` 的 `full_window` 里 `rebalances` 与
   `substitution.rebalances` 是同一个数的两处抄写，过去只校验了前者；现在两处不一致
   直接判 FAIL（这条是被本轮探针第 4 腿逼出来的，见 §四）。

## 三、重建后的读数（bar 2026-11-26）

`etf_book_liquidity_select`（判词未变：**SUBSTITUTION_NOT_SEPARABLE**）

| 臂 | 年化 | 夏普 | 最大回撤 | 容量中位 |
|---|---|---|---|---|
| A 已发布（纯 top-5） | 10.89% | 1.076 | −10.56% | 1,339,474 |
| B 加深度地板 | 11.00% | 1.087 | −10.56% | 1,450,101 |
| R 随机替换同样多 | 10.76% | 1.065 | −10.56% | 1,385,307 |

84 次调仓里 15 次触发替换（17.9%），共换掉 20 个名字，没有一次凑不满五个名额。
配对月度：B−A **+0.0083 pp**（t=0.386）、B−R **+0.0183 pp**（t=0.442）。
结论还是那句：**容量是机械买到的，收益读不出，别当 alpha 卖。**

`etf_book_liquidity_era`（判词未变：**NOT_SEPARABLE_IN_THIS_ERA**）

| 时段 | 调仓 | 触发 | B−A pp/月 (t) | B−R pp/月 (t) |
|---|---|---|---|---|
| 2020-2023 | 49 | 9 | −0.0147 (−0.671) | −0.0526 (−1.291) |
| 2024-2026 | 35 | 6 | +0.0393 (0.955) | +0.1134 (1.457) |

晚段两个方向都对，但都没有过自己的噪声线（t_min=2.0）——这正是"分期读"要挡的东西。

## 四、验证（可复跑）

- `python scripts/etf_book_liquidity_select.py selftest` → **18/18**（新增 L13-L18：
  锚一致无话可说 / 面板滚 bar 有漂移 / 门面改尺有漂移 / 没记锚不冒充健康 /
  端到端 rc3 且印 STALE / 端到端 rc1 且不含 STALE）；
- `python scripts/etf_book_liquidity_era.py selftest` → **16/16**（新增 L14-L16 同族）；
- `python results/_r2167bmc_liquidity_drift_probe.py` → **10/10**：每张面四问，
  全部打在**盘上真面**上——毒化 `panel_last_bar` → rc3 且首行 `check STALE`；
  毒化 `gate.lens_cny` → rc3；毒化一个发布数字 → rc1 且**不含** STALE；
  每次毒化后按原字节复原并断言逐位相同。
- **链会付钱**（这才是修法成立的地方）：把 select 的 `panel_last_bar` 钉成
  `1999-01-01` 后跑 `python Tools\s6_chain_bmc.py --only=liquidity_select_write`，
  同一把链直接印 `+refresh(rc=0,55.1s)` 并 rc0——过去它只会红着不动；
  era 腿 fresh 1.5s 结算。
- 契约词审计面复算：`chain_contract_word_audit` 候选 **16 → 14**（这两条腿移出）。

## 五、未做 / 未验证（如实）

- **全量冒烟没有被完整跑完**：本机 CLI 宿主跑 `python -m smoke_test` 会在 200-370 腿
  之间静默消失（r2162/r2164/r2165/r2166 同型），本轮改为后台分离进程另跑一份；
  四条相关冒烟腿（两面 selftest + 两面 check）已用手跑**同一条命令**验证通过，
  但**不宣称套件总数**。
- 这两张面仍只认「面板尾 bar」与「门面标尺」两个外部锚：票面（`etf_book_order`）改了
  而这两项不动时，它们读不到（与 r2164 的 toll 同族限制）。
- 面里 `data_end` 只是信息位：这本书是否该把最后一根 bar 用上，仍是书自己的设计，
  本面无判断。
- 剩余 **14 条**结构风险腿未动（审计面 rows 里逐条点名，按 r2164/r2165/r2166 的节奏
  一条一条解冻）。
