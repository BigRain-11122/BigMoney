# ENFORCE PROPOSAL — REGIME_GUARD v3（呈 GM 批）

- 状态：**FILED（待 GM 批 + 7 天否决窗）**；呈报人=风控部（bm-b 循环轮 r95）；
  证据链= prereg `research/REGIME_GUARD_VALIDATION_V3.md`（冻结 a25f47a）+
  `results/regime_calibration_v3.json` + T-10（done）。
- 判定链：v1 校准 FAIL（R+O 61.6%）→ v2 FAIL（26.53%，差 1.5pp）→
  **v3 PASS 三门全过**（拧法 B=RED 首绿释放 + C=橙级多维确认，阈值零改动）：
  G1 R+O=196 日=**12.01% ∈ [2%,25%]**；G2 橙级 FA=**0.0%** ≤60%；
  G3 零空档。

## 必呈条款（冻结原文，禁省略）

1. **G2 低统计力注记（§4.2 小样本标注条款原文触发）**：ORANGE 回合数=1
   （main=1 < 8）——G2 为机械 PASS，橙级误报率 0.0% 系单回合样本，统计力
   不足；本 PASS 判定不因小样本回撤，但提案裁决必须知情此点。
2. **反事实腿（12 引擎腿，r95 一次定稿）分族读数**：
   - 危机窗掩蔽真实代价集中在**反转确认双族**——ENGULF ΔSharpe −0.3221
     /Δ年化 −1.11pp（被禁 entry 26.9%）、NEEDLE −0.2540/−0.76pp（39.9%
     全员最高）＝「α 栖息地」第三次实证（enforce 后这两族的开新仓流量
     在危机日被实质截断）；
   - 防守/复合族代价近零或转正——VOLATILITY +0.0168、CE-02 +0.0048、
     CE-01 +0.2168、DROUGHT +0.3268（窄掩蔽下停开新仓反而滤掉低质 entry）。
3. **黄级 ×0.5 sizing 经济权重高于橙红条款**（黄级普查，引擎 sizing 仿真
   未实现=census 口径）：黄日 entry 吸收 CE-02 5608 / VOLATILITY 3855 /
   CE-01 3505 / ENGULF 653 / DROUGHT 552 / NEEDLE 160——高换手员黄级影响
   面为橙红掩蔽的 ~5-7×。若 GM 只批部分条款，黄级 sizing 条款的经济面
   权重最大。
4. **#10 趋势维度维持去收编**（v3 语义：hs300<MA200 不再触发状态机，其
   T0 执行接线=另案署名单）；RED 语义收窄为纯急跌/恐慌。

## 若批准，enforce 实装面（独立实现票，非本提案自带）

- live 探测器 `scripts/market_regime.py` probe 从 v1 口径切 v3
  （`raw_level_v3`/`resolve_state_v3` 已在库，加性在位，live 零触碰至今）；
- 响应矩阵接线（黄=新仓名义 ×0.5+禁加仓 / 橙=停开新仓 / 红=停开新仓+
  新资金停泊）→ paper 层 additive enforce flag（现 shadow-only）；
- 法文件 `firm/risk/REGIME_GUARD.md` §1 修订 + iron_rules 指针同步（T2 ·
  7 天否决窗）；science_audit C6 指纹联动更新；
- 首年 shadow→enforce 过渡期=双轨记录（enforce 信号与 shadow 信号并行
  留痕 1 个月）作为实盘开闸前置证据。

## 若否决/7 天否决窗内被否

- v3 状态机维持 shadow-only 记录（现行为零变化）；防线由 iron_rules 三红线
  + 熔断继续承担；不自主迭代 v4（§9 收线条款：两拧法已用尽）。
