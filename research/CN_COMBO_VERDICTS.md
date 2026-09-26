# CN 组合模型链判决汇总台账（T-73 s3 收口 · O-20260926-0926）

版本 v1.0 · 2026-09-26 R264 (bm-a) · dept: 研究部/组合与资金部联合
法链：O-20260926-0926 CEO 令（国内流派调研+CN 原生组合模型）→ T-73 s3 五模型链全 prereg 冻结 → 批跑 → 本台账收口。
判据：共享库 science_gates g1_prime_v2（skill line = passive_term + null 双项基线）/ g2_registration_v2（DSR 0.95 门 + 族 PBO 0.25 门），判线冻结于各批 prereg，禁看结果改阈值。
证据窗：evidence_cutoff = 2026-09-22（五批同源同窗）。

## 一、判决矩阵（5 族 × 19 cells：0 过线，全判负）

| 族 | cell | Sharpe(全程,费后) | skill line | 线判定 | CI95 下界 | CI 下界>0 | 族 PBO | PBO 门 | g1 判定 |
|---|---|---|---|---|---|---|---|---|---|
| CN-REV-TILT | REV20_bare | 0.1976 | 0.6147 | ✗ | −0.1253 | ✗ | 0.00 | ✓ | **NEG** |
| CN-REV-TILT | REV60_bare | 0.4757 | 0.6147 | ✗ | +0.3529 | ✓ | 0.00 | ✓ | **NEG** |
| CN-REV-TILT | REV20_tilt | 0.0104 | 0.6147 | ✗ | −0.3146 | ✗ | 0.00 | ✓ | **NEG** |
| CN-REV-TILT | REV60_tilt | 0.4217 | 0.6147 | ✗ | +0.3083 | ✓ | 0.00 | ✓ | **NEG** |
| CN-DIV-LOWVOL-ROT | W63_bare | 0.4596 | 0.9527 | ✗ | −0.3084 | ✗ | 0.00 | ✓ | **NEG** |
| CN-DIV-LOWVOL-ROT | W252_bare | 0.7371 | 0.9527 | ✗ | +0.0139 | ✓ | 0.00 | ✓ | **NEG** |
| CN-DIV-LOWVOL-ROT | W63_gate | 0.1699 | 0.9527 | ✗ | −0.5528 | ✗ | 0.00 | ✓ | **NEG** |
| CN-DIV-LOWVOL-ROT | W252_gate | 0.2716 | 0.9527 | ✗ | −0.4735 | ✗ | 0.00 | ✓ | **NEG** |
| CN-REGIME-POLICY | v3_base | 0.2998 | 0.5691 | ✗ | −0.2284 | ✗ | 0.6857 | ✗ | **NEG** |
| CN-REGIME-POLICY | v3_policy | 0.2300 | 0.5691 | ✗ | −0.2774 | ✗ | 0.6857 | ✗ | **NEG** |
| CN-REGIME-POLICY | policy_only | 0.2521 | 0.5691 | ✗ | −0.2642 | ✗ | 0.6857 | ✗ | **NEG** |
| CN-CORE-SATELLITE | SAT20_bare | 0.4234 | 0.5664 | ✗ | −0.1183 | ✗ | 0.5571 | ✗ | **NEG** |
| CN-CORE-SATELLITE | SAT20_gate | 0.4084 | 0.5664 | ✗ | −0.1219 | ✗ | 0.5571 | ✗ | **NEG** |
| CN-CORE-SATELLITE | SAT40_bare | 0.4586 | 0.5664 | ✗ | −0.0843 | ✗ | 0.5571 | ✗ | **NEG** |
| CN-CORE-SATELLITE | SAT40_gate | 0.4315 | 0.5664 | ✗ | −0.1151 | ✗ | 0.5571 | ✗ | **NEG** |
| CN-CORE-DDCTL | CORE_DD10 | 0.1048 | 0.7686 | ✗ | −0.4090 | ✗ | 0.6143 | ✗ | **NEG** |
| CN-CORE-DDCTL | CORE_DD20 | 0.3086 | 0.7686 | ✗ | −0.2187 | ✗ | 0.6143 | ✗ | **NEG** |
| CN-CORE-DDCTL | SAT40_DD10 | 0.3796 | 0.7686 | ✗ | −0.1405 | ✗ | 0.6143 | ✗ | **NEG** |
| CN-CORE-DDCTL | SAT40_DD20 | 0.4477 | 0.7686 | ✗ | −0.0939 | ✗ | 0.6143 | ✗ | **NEG** |

DSR 门：19/19 cells dsr_ok=false（g2 面同样全负）。

## 二、每族一句话结论

1. **CN-REV-TILT（短期反转倾斜）**：最佳 REV60_bare 0.4757 差线 23%（CI 下界+0.3529 为正=技巧增量真实但量级不足）；政体倾斜腿整体有害（REV20_tilt 0.0104 近零、两 tilt cell 均低于对应 bare cell）。
2. **CN-DIV-LOWVOL-ROT（红利低波轮动）**：全链最接近线（W252_bare 0.7371 = 线的 77%），但其基准 buy_hold_512890 单持有即 0.7039——轮动技巧净增量 +0.033 微弱；MA200 守卫腿在已低波动资产上全面降 Sharpe（W252: 0.7371→0.2716）。
3. **CN-REGIME-POLICY（政体+政策双轴）**：三面全败（0.23-0.30 vs 0.5691）；政策轴不是 α 槽（s2 slice-B 零 RNG 普查 495 子集预判被批数字确认）；族 PBO 0.6857 = 五族最差。
4. **CN-CORE-SATELLITE（红利压舱+动量卫星）**：四 cell CI95 下界全负；其静态基准 static_8020 0.3981——卫星腿增量真实（SAT40_bare 0.4586 > 压舱单持有 0.3605 > 静态 8020）但不足以跨线；PBO 0.5571 超门。
5. **CN-CORE-DDCTL（回撤门控压舱）**：dd 门控全面劣于无门控对照（CORE_DD10 0.1048 vs 未门控压舱 0.3605；R263 判负延续）——门控在长上行段剪掉复利腿、截断后回补慢。

## 三、全链判负归因（科学面）

1. **null/passive 双项基线高企是主因**：组合轮动族的随机重平衡 null 线达 0.5691-0.9527，被动项恒 0.4792——这些构造的收益主体来自市场暴露（β）而非轮动选择技巧（α）。与 T-28 首测 NOT-DEMONSTRATED（J4=0.4854<0.70，唯一挂点）同向互证：**组合面稳定盈利仍未证明**。
2. **PBO 超门三族**（POLICY 0.6857 / SAT 0.5571 / DDCTL 0.6143 > 0.25）：族内 cell 间挑选=过拟合面，即便单 cell 数字过线也禁入册。
3. **唯二 CI 下界为正的族**（REV-TILT、DIV-LOWVOL-ROT，族 PBO=0）：技巧增量为正但量级不足跨线——是最接近可用的两族，任何重启须新证据+新预注册。

## 四、配置面参考读数（O-1145 三线三判的诚实注记，非本批判据）

本批判据为 g1_prime_v2（prereg 冻结时定，禁翻案）。配置面四指标（x1 成本面参考读数，**不改变判负判定**）：

| 族最佳 cell | 年化 | 最大回撤 | Calmar | 正收益年占比 | OOS Sharpe |
|---|---|---|---|---|---|
| REV60_bare | 31.22% | −78.37% | 0.398 | 0.622 | 0.560 |
| W252_bare | 10.70% | −19.60% | 0.546 | 0.750 | 0.202（2026 YTD −1.25%） |
| v3_base | 3.23% | −36.75% | 0.088 | 0.533 | 0.368 |
| SAT40_bare | 7.79% | −49.10% | 0.159 | 0.714 | 0.732 |
| SAT40_DD20 | 6.97% | −41.18% | 0.169 | 0.714 | 0.732 |

注：W252_bare 的 OOS 崩面（0.2021 vs IS 0.7416）是「IS 窗与 OOS 开发窗重叠」外的独立警示——2026 段年收益 −1.25%，红利低波动量读数在近窗失效。若未来以配置面判据（年化/回撤/Calmar/月度正收益率）开新 prereg，此读数面为起点参考，但须重新走 PREREG_TEMPLATE 全链。

## 五、处置（三态如实标注：立法=git 可验 / 生效=判据过 / 验收=复审 ✓）

- **零入册**：STRATEGY_LIBRARY / 组合模型登记簿本轮零新行（五族 19 cells 全 NEG）。
- **判负禁翻案**（O-1105 §③ 判负线律）：本五族不重开；新证据=新预注册（PREREG_TEMPLATE 四选一 α 机制段 + D6 同族相关性准入检查起步）。
- **纸盘裁定**（GM 自决，O-1620 下放权范围内）：五族**不进前向观察纸盘**——观察纸盘是前向证据生成器，判负模型不生成增量证据面，与 O-1105 稳定优先准入一致；AGGR 先例（激进线判负仍进纸盘）不适用于本链（激进线三判律 KPI=收益天花板，本链属稳定/配置面准入）。
- **T-73 状态**：s1/s2/s3 科学面全闭环（s2 五片实证 + s3 五模型判定全落盘）；本台账=s3 判决收口面。剩余腿=CEO 呈报（本台账即载体）+月界判决台 10-01 例行接线时引用。

## 六、指针（重 derive 用）

- 批产物（判定面字节零动的输入基）：
  - results/cn_rev_tilt/p1_results.json（577 KB）
  - results/cn_div_lowvol_rot/p1_results.json（176 KB）
  - results/cn_regime_policy/p1_results.json（206 KB）
  - results/cn_core_satellite/p1_results.json（337 KB）
  - results/cn_core_ddctl/p1_results.json（290 KB）
- 预注册（s7/s8 各批已回填）：research/CN_REV_TILT_PREREG.md / CN_DIV_LOWVOL_ROT_PREREG.md / CN_REGIME_POLICY_PREREG.md / CN_CORE_SATELLITE_PREREG.md / CN_CORE_DDCTL_PREREG.md
- 判据库：scripts/science_gates.py（g1_prime_v2 / g2_registration_v2）
- 本台账提取器：results/_r264bma_cn_verdict_extract.py --write → results/_r264bma_cn_verdict_matrix.json（19 cells 判定矩阵机读面，重 derive 恒等）
- 账本链：五批 append_ledger 187687→187845（trials_ledger 正典键，R252 修链后连续）

## 七、回填记录

- 2026-09-26 R264 (bm-a)：v1.0 初版（五批判定收口）。取数=五批 p1_results.json 字节直读，pass_v2/line_ok/ci95_low/pbo/dsr 键名与产物实文核对（R261 夹具权源原文律）。
