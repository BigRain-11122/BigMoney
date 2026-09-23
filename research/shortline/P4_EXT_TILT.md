# P4_EXT_TILT — 扩展槽幸存者策略转化批（B 层·股票池·低频倾斜）预注册

> 跑前冻结（2026-09-24 bm-b round 67）。模板=research/PREREG_TEMPLATE.md；权威=BACKTEST_SCIENCE.md v2 判据 + BACKTEST_PLAN 三铁律。
> 认领：MSG-20260924-0610-ALL-p4-ext-tilt-claim.md（F-04 先于本件 commit 可见）。
> 开放池登记：STRATEGY_LIBRARY §九 NEW 条目「gdhs 季度幸存者策略转化批」；上游证据=P1D_EXT_SLOTS_IC r60（dzjy_amt_share_20 IS IC 0.0424/IR 0.323·OOS 留存 79%）+ P1D_GDHS_QUARTERLY r66（gdhs_chg_q −0.0263/−0.544、gdhs_chg_2q −0.0421/−0.675，OOS 深化；gdhs_level 判负不入批）。

## §0 批件身份【跑前】

- 批名/批号：`P4_EXT_TILT`（dept:研究·策略部）。**批内格数=每引擎跑一格**：主格 5 + 随机 null 40 + 被动 2 = **47 格**。
- 结构：本批=**纯 spec 冻结轮**（P-4 批二 r36 先例）；实现+跑数=后续轮（探针先行：单格计时后才定全批启动方式；>10min 必须后台化+checkpoint，R41 教训）。批报告必带 audit 段。
- 算力预算：股票面板 2850×5212 已有（P4_BATCH2 r38-a 缓存，gitignored 可再生）；预估全批 ≤ P4_BATCH2 同量级（其 70 格单轮内完成）；worker ≤ floor(16×0.8)=12。

## §1 α 机制段【D6 必填】

- [x] **行为偏差**（gdhs 双员主格）：股东户数下降=筹码从分散散户向集中知情持仓方转移；对手盘=横盘/阴跌后过早交筹的散户（处置效应镜像），知情资金吸筹后未来收益占优。因子级证据已在先验批成立（r66 双员 OOS 深化=政体存活）。
- [x] **微观结构**（dzjy 探索格）：大宗成交额占比高=机构大宗承接强度=知情订单流不平衡的可见代理；由延迟反应的普通投资者付出代价（P-A「占比类>方向类」同构）。

**同族相关性准入检查【必填·实现轮先于跑数执行】**：5 候选格 vs 在册 6 交易员（VOLATILITY/COMPOSITE-CE-01/02/ENGULF/NEEDLE/DROUGHT）日收益序列 max|corr| 逐对列出；批内 gdhs_chg_q↔chg_2q=同族双格（家族内部相关由 G2 PBO 治理，非 D6 拒收项）。预期 <0.7（股票池 vs core48 ETF·低频 vs 日频·域不同）；**max|corr| ≥ 0.7 → 拒收该格**。

## §2 数据与面板【跑前探针事实】

- **宇宙（冻结）**：`b_layer ok_static` 掩码 3517（O-1820 件3b，亏损股/ST/双红已剔）∩ **P4_BATCH2.md §2 动态资格条款逐字复用**（20 日均额≥5000 万、上市≥20 bars、价格≥1 元、末 bar≤250td、ST 滚动段剔除=双保险）——预期逐日资格 ~2900-3300 只，实现轮探针实测记入 JSON。
- **面板**：Money02 bars 前复权→P4_BATCH2 r38-a 缓存面板（T=2850×N=5212×7 列 float32，2015-01-01→**evidence_cutoff=2026-09-22**）；688xxx/689xxx volume/amount 双归一坑（r49 勘误）已内建缓存——本批消费 amount 列时按缓存口径。**结果 JSON 顶层必带 `science_gates.cutoff_meta(2026-09-22)`**。
- **因子数据源（不重建管线，复用 p1d_ext_slots_ic.py 装载规则）**：data/ext_slots/ gdhs 44/44 季、dzjy 165 月 316,436 行（r59/r60 门 PASS 记录在案）。
- **数据完备门（不过门禁跑批）**：实现轮先跑 p1d `gates`（三槽门沿用 r59 判据：dzjy≥95%/gdhs≥44 季有效）+ 本批宇宙探针（逐日资格股数中位≥2000、首再平衡日≥500 只可得因子值）；门红=诚实 exit 2 拒批。

## §3 方法学【冻结】

- **信号定义与滞后规则（逐字沿用 P1D 预注册，禁未来数据）**：
  - `gdhs_chg_q`：最近**可得**季股东户数增减比例；可用日=统计截止日+45 自然日→**严格次一交易日**（EM 更新日期列=刷新时间戳非披露日，r45 实证；+45d 保守规则冻结）。取 as-of 值（新季未出=沿用旧值，陈旧性如实披露）。
  - `gdhs_chg_2q`：最近两个可得季累计增减比例（同可用日规则）。
  - `dzjy_amt_share_20`：20 日大宗成交额/同窗 bars amount；可用日=T+1 盘后→**T+2 生效**。
- **再平衡排程（冻结）**：
  - 季频（gdhs 格）：每个季末+45 自然日后的**首个交易日**为再平衡日（面板内 2015Q3→2026Q2 ≈ 44-45 次）；该日按 as-of 因子值在当日资格股中**升序排名**（户数降幅最大=筹码集中最强=Top），做多 top_k；缺因子值的当季排除。持有至下一再平衡日，出 top_k 者在再平衡日发 exit 信号。
  - 20 日频（dzjy 格）：面板起点+20 日起每 20 交易日再平衡；**降序排名**（占比最高=Top）做多 top_k=10。
  - 引擎退出机（分层止盈/止损等）照常叠加于持有期（全项目惯例，纯引擎退出）；entry 帧仅在再平衡日为真→止损出场后须待下一再平衡日再入（写死披露）。
- **格位表（冻结）**：`gq_top5`/`gq_top10`（gdhs_chg_q）、`g2q_top5`/`g2q_top10`（gdhs_chg_2q）、`dz20_top10`（dzjy_amt_share_20）；仓位=引擎原生 initial_cash×10%/格（top10≈满仓起点、top5≈50% 现金拖累，如实披露）。
- **撮合**：fill_guard 照 P4_BATCH2 §3.1 逐字复用（买拒单 open==high&pct≥板别阈值−0.5pp 丢弃不重试；卖顺延 close==low 次一可卖收盘执行）。
- **成本（V1 域口径声明）**：股票回合 **26bp 恒定**（2×ETF FeeSchedule 工厂补丁，P4_BATCH2 §3.2 逐字；×2=52bp/×3=78bp 为幸存者描述性列）。**选 V1 不选 V2 的理由（写死）**：本域全部既有 null/被动/记录线（P4_BATCH2 vi 0.561）皆 V1-26bp 口径，换 V2=判线失去域内可比性；V2（ADV20 三层+1%ADV 帽）=G2 深化件候选非本批。
- **null 对照（同结构匹配）**：
  - 随机季频 null n=20：同再平衡排程、同资格宇宙、同 top_k=10、随机等权选股持有至下季（seed 基 **49_000**，先登记 SEED_REGISTRY 再跑）；
  - 随机 20 日频 null n=20：同结构随机选 top10 持 20td（seed 基 **49_100**）；
  - 被动 null：资格宇宙**月度等权**（P4_BATCH2 可比口径）+ **季度等权**（本批持有频率自然被动）各 1。
- **账本**：`science_gates.append_ledger('p4_ext_tilt', 47, file, evidence_cutoff='2026-09-22')`（dict schema 唯一禁手抄 prev；引擎链头现值 2858）。

## §4 判据【跑前写死·v2】

- **股票域技能线（本批自有，core48 线禁跨域套用——P4_BATCH2 §5 冻结条款沿用）**：
  - 自有 null 池=40 随机 null 全期 Sharpe → μ_null/σ_null；
  - `passive_strict = max(月度EW, 季度EW)`（本批实测，F10 strict-max）；
  - **D1 线 = max(passive_strict+0.10, μ_null+σ_null·√(2·ln N_eff))**（N_eff=账本链头+本批 47；经 `science_gates.skill_line_v2(null_pool=自有池)` 计算，**passive 项以加性扩池接 `passive_baseline(pool='stock_b_layer')` 读本批产物件**——库扩池=加性分支，无既有行为改动，selftest 全绿为门）；
  - **vi = max(D1 线, 0.561)**（P4_BATCH2 记录 vi_bar 逐位在案=域内历史地板；技能不得因降频变易，保守 max 写死）。
- **G1' v2**（主格逐格）：全期 Sharpe > vi **且** 平稳 bootstrap CI 下界>0（`science_gates.bootstrap_ci_sharpe`）**且** entries≥30（F6 双口径 (entries_ok) 为准）+ min_trades≥30；批报告逐列披露 vi 全输入（passive_strict/μ/σ/N_eff/0.561 地板）。
- **G2 注册资格 v2**：`g2_registration_v2(g1_pass, dsr, pbo)`——**幸存者另开预注册深化**（家族±邻域+×2/×3+DSR 原始收益+家族 PBO CSCV），本批只到 G1'（P-4 系全部先例）。
- 描述性条款（批级披露不替代门）：年化>0、OOS 双正（2025+）、回撤≥−35%、无崩年、×2/×3 成本列、逐年表。
- 预注册后跑数禁调线禁重跑（工程修复重跑=双跑留痕如实记账）。

## §5 跑前预测【写死】

1. **方向**：gdhs 双员做多筹码集中股=正 α；OOS 2025+ 留存为正（因子级 OOS 深化证据 r66）。
2. **量级**：4 个 gdhs 格全期 Sharpe 预计 [0.3, 0.9]；过 vi(≥0.561) 概率最高的=**g2q_top10**（chg_2q IR −0.675 最强）；预计 **1-2/4** 过线。top5 现金拖累≈减 Sharpe 0.1-0.2（VOLATILITY 现金腿先例）。
3. **dzjy 探索格**：因子余量仅 +0.023（r60 薄过线员）→ 预计不过 vi，作诚实负结果记录。
4. **随机 null 读数**：季频随机 null μ≈被动水平±0.15、σ 0.15-0.35（降频轮换≈被动附近的宽噪声带）；20 日频 null μ 类似。
5. **小盘倾斜风险**：户数集中信号天然偏小盘→资格门 5000 万均额缓解；预期回撤深于被动（-20%~-45% 区间），最深段=2018 或 2024Q1。
6. **成本弹性**：季频换手 ~30-40 笔/年 → ×2=52bp 全年增本 ≈0.2-0.3%/年 ≈ Sharpe −0.02~−0.04（J19 敞口缩放律）→ **若过 G1' 则 ×2 大概率存活**（与高频族死因谱相反，J15 上限 2× 不构成约束）。
7. **fill_guard**：季频再平衡日撞涨停开盘的拒单率预计 <5%（非打板族），对结果影响边际。
8. **engine 10% 仓位特性**（r43 记录）：equity 跌破 100k 后不开新仓——低频族影响=深回撤后重启慢，全格+null 平等待遇如实记。

## §6 产物

- `scripts/p4_ext_tilt.py`（子命令 gates/probe/run/selftest；复用 p1d 装载规则+P4_BATCH2 面板/fill_guard/CostPatch，禁重写既有件）
- `results/shortline_p4_ext_tilt.json`（顶层 evidence_cutoff + 逐格 metrics+vi 全输入+audit 段）+ `research/shortline/p4_ext_tilt_results.csv`
- 本文件 §7/§8 回填；STRATEGY_LIBRARY §九开放池行收线标注；账本 append_ledger。

## §7 跑后实证【跑前必须为空——占位纪律】

（跑后回填：主格全表/null 池读数/vi 全输入/G1' v2 判决/预测对账/机制定案。）

## §8 批后复盘【s7-T 必填】

（跑后回填：预测对账逐条+gate_attrition 登记+判线当批读数。）
