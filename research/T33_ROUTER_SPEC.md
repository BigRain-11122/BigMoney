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

## §7 跑后实证【2026-09-24 21:48 r71 bm-c 一次回填·runner=scripts/t33_router_validation.py·selftest 11/11 先行】

- **数据门全绿**：v3 重放逐位复现 GREEN664/YELLOW772/ORANGE35/RED161（bit-match）；roster attack=1/chop=5/defense=0；面板 cutoff 2026-09-23；日历覆盖 99.94%（分析窗 2020-01-02..2026-09-22·1631 日·成员 evidence_cutoff 2026-09-22 裁剪披露）；成员跑 18 次（6 员×x1/x2/x3·member_run 锚管线复用）；audit 段在产物内。
- **任期选择**：网格年化切换数 5→8.34 / 10→6.03 / 20→2.01，三网格全满足 ≤12/yr→最小网格 **5 入选**（无同数并列）；选中任期下切换 54 次/6.47yr。
- **V-R1 分段存活（x2 面·主判据）**：attack（1 员·663 GREEN 日）日均超额 **−9.13bp ✗**（DD 腿 −6.44% vs −5.12% 过）→ **fail 诚实零接受**（§5 预测 2「attack fail 或勉强过」命中：注册防御/反转员在 GREEN 段不敌被动）；chop（5 员·807 YELLOW∪ORANGE 日）日均超额 **+4.95bp ✓**＋段 DD −6.71% vs −44.87% 大幅优 → **pass**（防御/震荡专才画像实证）；defense 空编诚实零接受行（RED 由 V-R2 现金底仓面覆盖）。
- **V-R2 路由器对照（三面）**：x1 routed 1.88%/0.38/−7.34% vs 恒 chop 3.24%/1.06/−4.64% vs 被动 5.64%/0.39/−36.95%；x2 routed −2.11%/−0.34/−20.83%；x3 routed −5.67%/−0.88/−34.25%（routed 不要求跑赢=描述性如实）。**RED 段现金底仓主张**：x1 −1.08% vs −2.19% ✓、x2 −1.64% vs −2.32% ✓、x3 −2.70% vs −2.66% ✗（x3 切换入成本吃掉现金优势·边际 4bp）→ 三面压测下**不稳健=主张证伪面如实报**（x1/x2 成立）。
- **V-R3 切换成本可承受性**：x3 面年化拖累 **6.53% ≫ 1.5% 线 ✗**（54 次切换×双边 78.2bp/次）→ **旗标「切换过频」触发→任期规则复议单**（冻结处置·§4 逐字：复议单为后续候选批，本批零开单零接线）。
- **产物**：results/t33_router_validation.json（prereg_sha256_at_run 嵌入+audit 段+science_gates.cutoff_meta）+ research/t33_router_validation_results.csv（V-R1/V-R2/V-R3 全行）。

## §8 批后复盘【同回填】

- **预测对账（§5 四条）**：①部分未中——年化切换数预测 8-20 命中低端（tenure5=8.34），但「命中 10/20 概率高」未中：≤12/yr 约束比预期松，三网格全满足→最小网格 5 入选（预测低估了约束的松紧面）；②**命中**——attack fail（bull 段崩塌证据链延续）+chop pass（专才画像）双中；③部分中——RED 段 routed 优于恒 chop 在 x1/x2 成立但非「显著」（RED 段短驻留散布+切换入成本对冲现金优势），x3 边际证伪；④未中——切换成本预测 ≤1.0%/yr 实测 6.53%（预测同时低估了 tenure5 下的切换频次与双边成本算术）。
- **机制层结论（router v1 as-specced 判负诚实收线）**：路由器三主张两败一存——(a) attack 军团单员在目标段不存活=军团门缺口数据基座（招募线仍是 O-2012 主缺口·d2 0/20 后仍 1 员）；(b) 切换成本在 v3 状态迁移频次下不可承受（任期选择规则只限频次不限成本=规则设计缺口·复议单面）；(c) chop 军团分段存活=唯一过线主张。**激活闸维持关闭**（O-2012 s3 过渡正典：军团门过线+月界+CEO 可见报告三条件全不满足）；零 paper/engine 接线红线兑现（本批零接线零注册零账本）。
- **复议单候选面（不在本批开）**：任期规则升级候选=成本感知选择规则（在 ≤12/yr 约束上加 V-R3 1.5% 线联立→大概率落 20 网格·2.01 次/yr×78.2bp=1.57% 仍贴线）或降级为 RED-only 路由（只切现金底仓·其余态恒 chop·切换数 161→~20 次级）——任何变体须另开预注册走 G1' 类判定，禁本批内自行改线翻绿（J18）。
