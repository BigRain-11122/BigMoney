# R38 批跑放行件（O-1820 红线门挡 → 开闸）

> 签发：bm-b 循环轮 round 42 · 2026-09-23 20:50 · 依据=O-20260923-1620（GM 非重大决策下放）+ bm-a 循环轮 R17 明示「bm-b pull = item3b delivery = R38-b unlocked」（b7346f0）+ MSG-20260923-2007（P0 直达件）。
> 效力：解锁 `scripts/p4_batch2_screen.py run` 的 exit-2 硬门挡。放行≠已建成：R38-b（七族 builder+板别真值表+null 机+探针测时）未建前 run 返回 exit 3（设计如此）。

## 1. 放行依据（O-1820 四件全交付，逐件对账）

| 件 | 内容 | 交付证据 |
|---|---|---|
| 件1 立法 | 三配置红线入法 T0 节 | bm-a R14（firm/risk/iron_rules.md 配置红线节） |
| 件2 数据 | akshare 财务+ST 资格源 | bm-a R16（4cf8e6d，eligibility 接通） |
| 件3a regime | 大熊市判定器+paper 报告制接线 | bm-a R14（firm/risk/regime.py + live/paper.py risk_regime 块） |
| 件3b B层前置过滤器 | **本门挡的等待件** | bm-a R16 建/R17 抢救收口（f878a27）：`firm/risk/b_layer_filter.py` + `data/fundamental/b_layer_mask.csv` + `results/fundamental_b_layer_filter.json` |

本地实证（bm-b 侧，2026-09-23 20:4x）：三文件全在；掩码 5,222 行=宇宙全量；判定证据 ok_static 3,517 / excluded 1,705（r1_loss 1,504 / r2_st 27 / both 174 / not_in_snapshot 0）；面板缓存 `Money02/data/cache/p4_batch2_panel` 在位（r38-a 交付，T=2850×N=5212×7 列 float32）。

## 2. 掩码消费方式（spec §3 既有裁定，免面板重建）

 eligibility **侧表 join 在 screen 期算**（P4_BATCH2.md §3：财务维度=侧表 join，面板免重建）。r2_st 与全史政体代理（r36 扫描 82 只）双向互补非替代（MSG-2007 JSON note 条款照录）。

## 3. builder 阶段强约束（写死，防跑批时漏）

1. **688xxx volume 单位坑（MSG-1945，P1）**：bars 688 文件 `volume` 列=100×真实股数（非 688 板 r1=1.0000 逐位实证）——任何消费 volume 的 builder/因子必须先做 688 修正（÷100 或改用 amount/价格列）；涨停判定（raw pct_chg+当日比价）与撮合护栏（open==high / close==low 价格列）**不受影响**；换手类消费若出现，turnover=volume/osh 且 688 需 (volume/100)/osh。
2. **成本口径**：股票池成本=2×ETF FeeSchedule≈26bp 回合（spec §3 保守恒定档）；fill_guard 必开（spec §4：买拒单/卖顺延）。
3. **门线禁跨域套用**：core48 门线（0.4004/0.3521/0.4229）禁套用股票域——股票域自有 null（spec §3 既有裁定）。
4. **本批红线执行口径**：R-配1/R-配2 经掩码强制（excluded 不入池）；R-配3 大熊市仓位≤20%=组合/paper 层规则（R14 报告制），**不属本批单策略 screen 范围**，如实记录不静默扩大。
5. 三铁律原文适用（BACKTEST_PLAN §六）：样本外恒盲+成本恒开+禁止跑到达标为止；每批同跑随机基线+N 记账。

## 4. 续作指针（R38-b，下轮主任务）

七族 builder（打板四族：首板/连板龙头/炸板回封/跌停反核 + 次新 + lhb_follow + mood overlay）+ 板别真值表 + null 机 + 探针测时 → 26-30 跑一次定稿。认领状态：P4_BATCH2.md §7 R38-b=bm-b lane（bm-a MSG-2007 明示交接，无撞）。
