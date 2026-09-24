# T33_ROUTER_SPEC 预注册（军团路由器 v1 规约）· T-2026-09-24-33 deliverable-3 · O-20260924-2012

> 冻结时点=本文件跑前 commit（sha 记入 T-33 票面，d4 runner 运行时嵌入 `prereg_sha256_at_run`）。
> 本件=规约+判定判据双载体：§1-§5 为路由器规约（frozen），§6 为 d4 验证批判据（frozen，跑后禁改）。
> 红线重申：本批 **零 paper/engine 接线**——激活闸=军团门过线+月界+CEO 可见报告（O-2012 s3 过渡正典）。

## §0 批件身份【跑前】

- 批名：T33_ROUTER_SPEC（规约冻结）；消费批=T33_ROUTER_VALIDATION（d4，另按本件 §6 判据跑）
- 认领：F-04 先行已随 T-33 r68 认领 MSG 覆盖（同票同车道·bm-c）；任务单=T-2026-09-24-33-P1
- 部门归属：dept:策略+风控（路由=配置层；RED cash floor=风控面）
- 算力预算：规约件零算力；d4 验证批=确定性聚合+路由回放，预估 <10min（轻批·轮内合法），audit 段必带

## §1 α 机制段【四选一】

- [x] **结构性**：REGIME_GUARD v3 状态机是对波动/趋势结构的持续性度量（hs300 vs MA200+波动分层），
  状态迁移存在制度性惰性（指数成分调整滞后+机构调仓周期）；路由器在状态持续期内持有对应风格军团、
  在迁移点支付一次换仓成本。**由谁付出代价**=迁移点的即时流动性需求方（趋势追逐者被迫在翻转日成交）
  与 GREEN 期过度保守者（把溢价让给 attack 持有人）。配置层主张成立的前提=分段风格差存在（T-22 分段表
  bear/chop/bull 三段已量化），本件不引入新信号族（**D6 豁免论证**：路由层仅重排**在册成员**权重，
  零新收益序列入池，max|corr| 检查对象不存在；新成员招募仍走 T-33 d2 G1' 通道不受本件豁免影响）。

## §2 状态源与数据【跑前事实】

- 状态源：REGIME_GUARD v3 四态序列（GREEN/YELLOW/ORANGE/RED）——`scripts/regime_calibration.py`
  原语 import-replay（无缓存每跑现算·T-21 同源同法），决策日状态→次一执行日门控（无未来数据）。
- 窗口与 evidence_cutoff：v3 校准窗（~1632 交易日，as_of=2026-09-23，legacy 轴）；d4 结果 JSON 顶层
  必带 `science_gates.cutoff_meta` 合法键。
- 数据完备门（d4 跑前）：core48 面板 cutoff≥2026-09-23；v3 重放逐位复现校准批记录
  （GREEN664/YELLOW772/ORANGE35/RED161，bm-b r98-99 权威）；corps_roster.json v1 在位。
- 军团成员面（frozen 输入）：results/corps_roster.json v1——attack=1（COMPOSITE-CE-01）/
  chop=5 / defense=0（诚实缺口 O-2012）；进攻招募 d2 0/20 后 attack 仍=1。

## §3 路由规则【规约本体·frozen】

1. **映射**（四态全覆盖）：
   - GREEN → attack 军团；YELLOW → chop 军团；ORANGE → chop 军团；RED → defense 军团+**现金底仓**
     （RED 期 mapped 军团仓位上限=0%——即全现金；非 RED 状态无现金底仓条款，军团内部分散照旧）。
2. **空军团回退**（结构性诚实条款）：
   - 映射军团为空 → 回退次保守非空军团（序：attack→chop→defense→cash；chop→defense→cash）；
   - defense 空（现况）→ **RED=100% cash floor**（回退终点），报告必带「defense 空编」披露行；
   - 回退不产生递归循环（序有限）。
3. **最小任期反抖动**（min-tenure）：网格 **{5, 10, 20} 交易日**；选择规则（frozen，d4 执行）：
   在全 v3 序列上模拟军团切换次数，取**满足 年化切换数 ≤12 的最小网格值**；并列取更保守（更大值）；
   任期语义=新状态须**连续持续 ≥ tenure** 才生效，否则维持前军团（滞回），未生效期状态记录为 pending-flip 披露。
4. **换仓成本面**：切换日整组合换手，成本恒开；压测面=**x2 与 x3 双面**（CostPatch(2.0)/(3.0)，
   P5C/T-22 先例）；x1 基面同报三面披露。
5. **因果律**：T 收盘状态 → T+1 开盘生效（引擎 T-close 信号→T+1-open 成交契约同构；T-21 决策日门控语义）。
6. **月界**：路由变更（映射/任期/成员集任一）生效须过月界（前向锁月惯例）；本规约冻结即记版本 v1。

## §4 d4 验证批判据【跑前写死·禁看结果调线】

- **V-R1 分段存活**（逐军团·主判据）：军团在其目标段（attack: GREEN 段日；chop: YELLOW∪ORANGE 段日；
  defense: RED 段日）的等权组合**跑赢被动 EW-48**（同段、x2 成本面）——分段日均超额>0 且分段最长回撤
  不劣于被动段回撤 5pp 以上恶化；逐军团报 pass/fail，**诚实零接受**（attack=1 员小样本须披露 n_days）。
- **V-R2 路由器对照**（描述性·非注册门）：routed 组合（映射+任期+成本三面）vs **恒 chop 基线**
  （最保守非空替代）vs 恒被动——年化/Sharpe/maxDD 三面披露；routed 不要求跑赢（配置层价值=RED 段
  避损为主张面），但 **RED 段 routed 回撤必须优于恒 chop 基线**（否则现金底仓主张证伪，如实报）。
- **V-R3 切换成本可承受性**：x3 面年化切换成本拖累 ≤1.5%（超出=旗标「切换过频」→ 任期规则复议单）。
- 注册律不受本件影响：成员注册仍恒走 G1' v2/G2 v2 共享库判据（本批零注册零接线零账本 N 增量——
  聚合先例 r68/r69）。

## §5 跑前预测【写死于跑前】

1. v3 序列年化切换数（无任期）预测 8-20 次/yr → tenure 网格命中 10 或 20 的概率高（ORANGE/RED 短驻留）。
2. attack 军团（1 员）GREEN 段：T-22 bull 段证据=进攻员 bull 段崩塌（0.471/0.266），预测 V-R1 attack
   **fail 或勉强过**（小样本披露在先）；chop 5 员在 YELLOW∪ORANGE 段预测 pass 概率高（防御/震荡专才画像）。
3. RED 段现金底仓 vs 恒 chop：预测 routed 回撤显著优于恒 chop（RED 段=2024-02 型踩踏日集中段）。
4. 换仓成本：x3 面预测 ≤1.0%/yr（切换稀疏· tenure≥10）——若 >1.5% 则 §4 V-R3 旗标触发。

## §6 产物【d4】

- runner：scripts/t33_router_validation.py（selftest 离线先行；import-replay v3 状态+消费
  t22 分段表+corps_roster v1）；
- results/t33_router_validation.json（顶层 evidence_cutoff+audit 段+cutoff_meta）+
  research/t33_router_validation_results.csv + 本件 §7/§8 回填（本件即 prereg，跑后只回填）。

## §7 跑后实证【跑前为空——写数字即造假】

（d4 跑后一次回填）

## §8 批后复盘【占位】

（d4 跑后回填：预测对账+损耗账+skill_line 读数如适用）
