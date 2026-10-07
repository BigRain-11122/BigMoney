# REGIME-5 判别器 v1.0 冻结件（T-2026-10-08-177 s1 · O-20261007-2215 @bm-a ①）

- 法源：O-20261007-2215-bm-c §一（CEO 判据方向 verbatim 数值化）+ research/REGIME_STYLE_MATRIX_V1.md §一（冻结契约）。
- 可运行件：`scripts/regime5_labeler.py`（run/selftest·15 检全绿·确定性幂等）；标签面 `results/regime5_labels/REGIME5-<cutoff>.json`（契约三键·bm-c 矩阵消费取最新）；诊断面 `results/regime5_diag/REGIME5-DIAG-<cutoff>.json`。
- 全史回放：510300 日线 2012-05-28→cutoff·K=3,289（≥1000 律 ✓）；近期分布 cutoff 2026-09-30：BULL=201/CHOP=2,103/GRIND=103/BEAR=780/SUPPORT=102。
- **冻结律**：本件 v1.0 阈值=先冻结后验证——判别规则在跑任何「阶段×收益差」验证之前冻结（标签禁拟合结果）；此后修订只能走验证批预注册（slice-2）。阈值指纹=selftest t01 哈希字典（THRESHOLDS verbatim）。
- **v1.0 面效度修正（先于一切收益面消费·如实留痕）**：SUPPORT_DIST_MAX 0.03→0.15——0.03 把 2015-07-06 正典救市（z=5.41 天量+强收盘·dist +10.9%＝泡沫消化期 MA200 滞后）挡在域外；0.15 保留狂热期防误报同时收录早期崩盘救市。修正时点=零收益验证消费之前。
- 规则（优先序）：SUPPORT 事件窗（脉冲日=下跌日+amount z≥3〔510300 或 510050 120d 窗〕+强收盘〔(close−low)/range≥0.40〕+dist<+15% → 日+后 9 交易日）＞BULL（dist≥+3% 且 20 日内 ≥50% 日处于 60 日高点 ×0.995 内 且 MA5(amount)/MA60(amount)≥1.0）＞BEAR（dist≤−5%）＞GRIND（dist<0 且 r20<0 且 amt_exp<0.85 且 vol20 分位≤0.5）＞CHOP（缺省）。
- 诚实 DATA_GAP（验证批呈报面）：①尾盘脉冲需分钟数据（minute_feed 仅前向 2026-10-07 起）→ v1.0 日线代理=天量 z+强收盘；②急跌日成分稳定性需宽幅盘中面板→缺。候选误报窗（验证批定量）：2017-08-31/2023-11-17。
- 验证批（slice-2·另窗预注册）：2020→今各阶段历史收益差+显著性+K≥1000+N_CONF 校准（矩阵消费端缺省 3）+过渡成本判据（Σ|Δw|×COST_X1 吃得过）+随机标签 null 对照。判据节按 PREREG_TEMPLATE/science_gates 共享库起草。
- 大限：≤2026-10-14 12:00（O-2215 §三）；判据回访 10-21。本面零交易零注册件触碰。
