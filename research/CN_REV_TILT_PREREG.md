# CN_REV_TILT_PREREG — CN-REVERSAL-TILT 组合模型·s3 切片 1 预注册（跑前冻结）

> 令：O-20260926-0926（CEO「去调研国内市场的各个流派……建立起适合国内情况的组合模型」）· 票：T-2026-09-26-73（P1·immediate·bm-a）s3 首模型切片。s2 切片A 实证地基：DIGEST-20260926-t73-s2-sliceA（REV20/h10 OOS ic +7.0bp=44×null 阈、MOM 镜像同窗亏损、**v2 不过=定律政体依赖→本模型必须带政体轴**）。
> 跑前冻结：本文件 commit 先于任何跑批（R99 律）；跑后只许回填 §7/§8，禁改判据禁重跑。冻结时点=2026-09-26 R245（bm-a）。
> F-04 先行声明：fleet/inbox/MSG-20260926-1211-bm-a-claim-t73-s3-slice1.md（同轮 commit）。

## §0 批件身份【跑前】

- 批名：CN-REV-TILT-P1；判断格=**4 策略格**（{REV20, REV60} × {裸反转, 政体倾斜}）+ K=50 nulls 面成本压测不入 skill 格（J2 式披露）；per-cell N 计入 N_eff。
- 认领：F-04 MSG 在案（上）＋票 T-73 在册 bm-a；本批=组合与资金部（装配/判决）+研究部（机制/信号）+工程部（runner）joint。
- 算力预算：census 面板（T=8792×N=5222）截面批预估 5-15min → **池提交**（>5min 长活纪律·runnable_pool+checkpoint 幂等）；worker ≤25（floor(32×0.8)）；批报告必带 audit 段（elapsed/worker/瞎跑白跑旗自检）。

## §1 α 机制段【D6——四选一】

- [x] **行为偏差**：A 股散户主导市场的处置效应+过度反应——追涨杀跌者对近期跌深股过度抛售（锚定于前高），短期均衡回归时由「杀跌者」支付溢价给「接跌者」；s2 切片A 已实证该溢价 OOS 存活（ic=+7.0bp/日）且动量同窗为负（付费方=动量追涨者）。结构性放大器（副选·注记）：T+1+涨跌停制度使单边过冲隔日才可兑现→过冲更易留存后回归。
- **政体依赖诚实注记（s2 冻结面）**：v2 判线不过=2017-2020 动量风格期反转被压制 → 本模型政体轴非可选件是构成件（§3.3）。
- **同族相关性准入【跑时必填】**：新信号函数=股票域截面 REV 面（zoo 在册反转族=ETF 域形态/择时面不同域；#79 micro_cap=市值族；#85 salience_panic=P-1c IC 消费面）→ 入批时对在册交易员全员+同批函数逐对算 `max|corr|`（日收益口径）：______（§7 回填）；`max|corr| ≥ 0.7 → 拒收`。

## §2 数据与面板【跑前探针事实·实现切片首步冻结具体值】

- 宇宙：全 A census（N=5222·close ffill·P1C 缓存同源=scripts/t73_s2_reversal_momentum.py 同装载器，零新拉取零网络）。
- **evidence_cutoff（D2 前向锁盒）**：实现切片首步用同源装载器实读面板末完整 bar 日并**回填本节具体数值后 commit 冻结**（预期=2026-09-24 或最近完整交易日）；runner 断言面板 cutoff==冻结值，不等即 fail-closed exit 2 零产物；cutoff 后新 bar 不回流本批。结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`。
- 数据完备门：cutoff ≥ 2026-09-22 且 覆盖股票 ≥5000 且 T≥8000 交易日，缺一即不跑。

## §3 方法学【冻结】

### §3.1 信号（s2 切片A 冻结面直用·零新参数搜索）

- REV20(t) = −(C_t/C_{t−20} − 1)；REV60(t) = −(C_t/C_{t−60} − 1)。截面降序排名（跌最深=信号最强），t 日收盘算信号、t+1 日执行（T+1 禁未来数据）。

### §3.2 组合构造（百万资金日线可建模性·s1 表「高」档）

- 持有池=信号前 10% 分位池内取 **top 20 名等权（各 5%）**；持有 10 交易日（h10 主口径·s2 同窗）到期再平衡；退池资金入现金腿（零收益，逆回购面另票）。
- 成本口径：**V1 legacy 13bp×2**（P1C close-only 面无 ADV 面，V2 不可算=如实声明）+ **×2/×3 压测双轨**（BACKTEST_PLAN 三铁律）。

### §3.3 政体轴（构成件·s2 v2-fail 实证驱动）

- **风格政体探测器（前向锁）**：trail(t−1)=过去 252 交易日 REV 主面裸袖净收益 − MOM 镜像裸袖净收益（同构造同窗，t−1 因果·shift(1)·首 252 日 warmup=袖空仓如实披露）。
- **倾斜规则**：trail>0（反转政体）→ 反转腿 0.9 + 现金 0.1；trail≤0（动量政体）→ 反转腿 0.1 + 现金 0.9。无调参面（阈值 0 与窗 252 冻结）；REGIME_GUARD v3 四态序列随批输出=描述性披露列（市场政体 vs 风格政体两轴对照诚实呈现，不作切换门）。

### §3.4 null 与基线

- null：K=50 同掩码随机信号组合（同宇宙同窗同再平衡节律）；**新 seed 基 `cn_rev_tilt_p1`=20260926**——跑前先登记 `science_gates.SEED_REGISTRY` 再跑（模板 §3 律）。
- 被动基线：census 等权组合（全 N 等权·同再平衡节律）+ 随机信号基线同跑记录试验总数 N（BACKTEST_PLAN 铁律三）。

## §4 判据【跑前写死·共享库调用禁手抄判线】

- **G1' v2** = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=4, n_trades, n_entries)`：全期 Sharpe > skill_line_v2（max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）且平稳 bootstrap CI 下界>0 且 entries≥30；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2** = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑）且 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·4 格网格）。
- 描述性条款（批级披露不替代 v2 门）：年化>0、OOS（≥2025-01-01·composite_ic 共享分割）双正、|maxDD|≤35%、无崩年、×2/×3 成本逐年稳定。
- **硬界设计三件套【D-20260925-01①】**：极端日判读以 median/p99.9 分布界承担主责；max 硬界配危机日感知（2015-06/07 股灾、2016-01 熔断、2024-01/02 微盘踩踏窗命中→记危机日志+单点豁免单列披露，单点删除优先于整批判负）；§5 跑前预测给极端日先验。
- 判负即收线：本批 4 格全负=CN-REVERSAL-TILT 模型判负照登（新证据=新预注册，禁翻案）。

## §5 跑前预测【写死于跑前·跑后对账】

1. **REV60 裸袖 OOS 最厚**（s2 最强面 8.9bp 地基）：预测 OOS 净 x1 Sharpe REV60 ∈ [0.5, 1.5]、REV20 ∈ [0.3, 1.2]；IS 全期裸袖正但 2017-2020 段被稀释（v2 fail 同面）。
2. **政体轴有效假设**：倾斜格 vs 裸格全期 Sharpe 提升 ≥0.15 且最差年回撤收窄 ≥30%（动量政体年降权 0.9→0.1 的机制主张）；若倾斜格反而更差=政体探测器窗 252 失效的诚实可能（预测对账按此判）。
3. **成本面**：×2 压测下 REV20 净 edge 腰斩以上（20 名月级换手重）、REV60 更耐成本（预测 REV60 x2 存活 > REV20 x2）。
4. **极端日先验**：2015-07 救市窗与 2016-01 熔断窗 loser 篮子单日 |r| 可达 ≥9%（跌深篮子在崩盘窗再跌+反弹双极端）；2024-02 微盘踩踏窗小盘跌深股集中重灾——max|d1| 硬界按三件套走分布界+危机豁免，禁裸 max 判负。

## §6 产物

- 脚本：`scripts/cn_rev_tilt_p1.py`（实现切片·P1C 同源装载器+checkpoint 幂等+selftest 腿+audit 段）；
- 结果：`results/cn_rev_tilt/p1_results.json`（顶层 evidence_cutoff + science_gates.cutoff_meta + 4 格×{x1,x2,x3} 全输入输出 + nulls50 + 基线 + corr 清单）+ CSV 明细；
- 账本：`science_gates.append_ledger('CN-REV-TILT-P1', batch_trials, file_name, evidence_cutoff=...)`（dict schema 唯一禁手抄 prev）。

## §7 跑后实证【跑前为空——写数字即造假】

（占位）

## §8 批后复盘【跑后必填·s7-T】

（占位：预测对账+gate_attrition 追加+skill_line_v2 当批读数+过闸则 CN-* 纸盘族接线切片开票）

---

**过闸后续链（声明·不属本批判据）**：过 G2 → CN-REVERSAL-TILT 纸盘账户（¥1M·results/cn_paper/ 独立车道·PROS 白名单范式·不入 t35/CEO 面直到晋升）+ 组合判决台入池（T-28 W-CUR 窗对照面·B_MAXDIV/EW-48 基线）；不过=判负照登。s3 其余模型（CORE-SATELLITE/REGIME-POLICY/DIV-LOWVOL-ROT）各另开 prereg。

—— bm-a 组合与资金部+研究部 R245（2026-09-26 12:1x · 跑前冻结 · 零结果零编数）
