# PERPETUAL-N2-W15 预注册（波级）——**DRAFT · 未冻结**

> **状态：DRAFT-NOT-FROZEN（2026-10-01 r510 bm-a slice-1 窗）。冻结门=下述五条件全过才
> 允许烧批；冻结前零 burn 零 supply 零登记（R99 跑前冻结律 / R250 one-step 律）。**
> 法：research/PERPETUAL_FACES.md v1.0 §2 N2 行 + §4 起草序（N1-W2 ✅ → N3-R1 ✅ →
> **N2-W15（本件）** → N4-B1）。
> runner：scripts/perpetual_faces_n2.py（slice-1 已落地：subspace draw + probe +
> status + selftest 8/8 ALL PASS + probe 真引擎面 2.25s 双胞实证
> results/perpetual_faces/_n2_w15_probe.json）。

## 冻结门（五条件，冻结 commit 前逐条机证）

1. runner slice-2 腿落地：generate（subspace 绘制→T-84s3 指纹去重→28 源排除面真读）+
   screen（G-PANEL..G-CNT 门链+6m beat-rate+null p95 存活线）+ screen_finalize + 分片
   run/池握手（r496 三调用点）+ finalize。selftest 腿同步扩（真路径覆盖·r494 真跑律）。
2. 三步种子法全绿：gen/scrnull/unc 三带在冻结 commit 登记 `science_gates.SEED_REGISTRY`
   （§5 带面），`banned_direction_gate --prereg` 退出 0。
3. 判据节调共享库（§4 引用面），禁手抄判线（T-02 6/7 律）。
4. D6 同族相关准入检查面在判据节显式（judge 阶段执行·§4）。
5. 意义门三问过（§0 三行作答）+ CEO 令面核对（O-2026-09-30-2340 常供面令=本 face
   授权面，无需新署名）。

## §0 批件身份【跑前填·冻结时核】

- 批名：PERPETUAL-N2-W15（常供面 N2·波 1；语法波系命名顺延 W15）。
- 认领：F-04 先行——开工前 fleet/inbox/ MSG 声明（防双机撞车）；任务单引用：
  T-133 s2 常供面票（O-2026-09-30-2340）。
- 部门归属：dept:研究。
- 算力预算：初筛面≈5,200 cell（raw 5,000 + null 200）× 单轴 6m base·分钟级/百人
  （TRIAL_LABOR_LAW §2）→ 12 分片后台化+跨轮 checkpoint（R41 教训）；批报告带 audit 段。
- 意义门三问：①研究问题=「组合空间（多 overlay 门同时激活面）是否藏有逐波单门
  系统性探不到的候选」——W1-W14 每波只把最新门当变量、其余压 none，组合域 16.9 亿
  格只被稀疏尾采样过；②消费方=初筛存活者→judge 批（另段冻结·mass_trial 先例）→
  试用期题库/在册员增补线；③语法登记簿查重=research/TRIAL_GRAMMAR_LEDGER.md 无
  random-subspace 行（2026-10-01 实读），本批=新面首烧。

## §0.5 禁开方向闸【冻结时跑 Tools/banned_direction_gate.py】

- 本批机制面=冻结语法库的轴组合采样，正文不引任何禁向词面；冻结时闸退出 0 放行。
  若闸命中外来词面（如排除面真读带来的引用），按闸 JSON missing_fields 补例外三件套
  （r494 合同律），禁绕闸。

## §1 伪机制段

- 四选一勾选（本批选择）+一句话论证：**结构性**——组合门面的结构摩擦/门叠加
  交互（14 门同时激活时的入场许可交集结构）是逐波单门探索系统性遗漏的结构面；
  探索面主张（canon §2「探索面」原注）：不预设任何单一门有超额，测量=组合空间
  是否存在存活者。
- 散户出净值证伪一句答：本批候选经组合门过滤后若出净超额，其来源只能是门结构
  交互而非任何新数据/新信息（门态序列全部为已有冻结语法库成员·零新数据面）——
  行为/数据/容量面均无法解释 → 结构交互面。
- D6 同族相关性准入检查：N2=候选漏斗面（canon §2 注原文），judge 阶段逐存活员算
  `max|corr|`（与在册交易员全部成分员+sleeve 全员，日收益序列口径）≥0.7 拒收。

## §2 数据与面板【跑前探针事实，非结果】

- 宇宙：core48（tl1 G-PANEL 48 员门同面）；leg-L = 2020-01-02..cutoff 1,631 bar
  （probe 实读 days=1631）。
- 数据锚四元组：面板 data/daily/sh<码>.csv；加载 tl1.load_core/_load_leg("L")；
  起算 2020-01-02（leg-L）；预热窗=各门首有效位（tl14 门链冻结面·A158 RESI 首可判
  120 / CNT 119 差一档诚实注记沿 W14 冻结件）。runner probe 路径与锚路径同面断言
  （G-ANCHOR-FACE 同面断裂律）。
- evidence_cutoff=**2026-09-22**（同窗律；结果 JSON 顶层+
  `science_gates.cutoff_meta("2026-09-22")` 双写，缺字段=science_audit C2 VIOLATION）。
- 数据完备门：tl14 G-PANEL..G-CNT 门链同面复用（W14 冻结口径），不过门不跑。

## §3 方法学

- 因子/信号定义：**零新信号**——冻结语法库 W1-W14 全库（18-tuple：R/X/S/T 基四轴
  + STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI/CNT 十四门）
  的组合采样；信号面=tl1 factory（A 6 锚模板+B 72 工厂函数，grammar families 实读）。
- W15 subspace 绘制层（runner 已实现+自检腿 L2/L3 机证）：每绘制单流冻结消费序
  =①k_active~U{1..14}→②活跃子集均匀无放回→③基四轴全域→④活跃门值取非 none 域；
  非活跃门钉 none；参数=family Sobol 盒（scrambled，tl14 映射原语同面）。
- 绘制量：raw **5,000**（A 500 / B 4,500·W13 波先例同裂）→ T-84s3 信号指纹去重 →
  tl14 28 源排除面真读（已判格语义恒等排除；W15 新语法格=合法不排除）→ 入册候选。
- null 对照：K=200 screen-null 族（scrnull 带；tl14 `_null_axis_draw` 同面口径）。
- 两段制（TRIAL_LABOR_LAW §2）：**廉价初筛先行**（单轴 6m base·EW48 passive beat-rate）
  → 存活者才进全量判决（双轴×{6m,12m,24m}×x2 成本×分段×双 nulls）——judge 批
  **另段冻结**（mass_trial_w1 先例），本 prereg 只冻结初筛段。
- 成本口径：V1 legacy 13.041bp×2 压测恒开（engine 默认面·tl14 同源）。
- 往返成本 bp 申报：ETF 26.082 bp/往返（面 A 恒等，13.041×2）。
- 账本：screen finalize `science_gates.append_ledger(batch_name=
  "PERPETUAL-N2-W15-SCREEN", batch_trials=<实际 enrolled+null>, file_name=…,
  evidence_cutoff="2026-09-22")`；judge 批另册。
- 闭合族对号声明：family_key=**perpetual_faces_n2（open）**——不在册=open 照烧；
  判负后若关线须附「新证据增量」声明（U3 律）。

## §4 判据【跑前写死，禁看结果调线；判线一律调共享库】

- 初筛存活线=**beat6m_rate > null 族 p95**（程序冻结、数据自适应、零手挑阈值；
  tl2._finalize_math 同面口径，w2 先例）+ n_entries≥1 诚实腿（零入场=诚实败行非
  错误）。G1'/G2/DSR=judge 批判据面（另段冻结时调
  `science_gates.g1_prime_v2` / `g2_registration_v2` / `dsr_from_stats`）。
- x2 成本压测：judge 批面（初筛段 engine 默认 V1 恒开）。
- 预注册预测（跑前填·冻结时核）：组合空间稀疏（probe A0 八门=零入场实证）→
  预测 raw 5,000 存活者 **≤ 3%**；若 ≥3%=组合面比预期富集=机制面新信息。

## §5 种子（三步法·冻结 commit 登记 SEED_REGISTRY，R250 禁冻结后再挑）

- perpetual_n2_w15_gen=**31_000**（Sobol 盒+轴流）／scrnull=**31_500**／
  unc=**32_000**；带宽 499；30_000+ 域外顺延（法典 §4 N2/N4 行）——lfc_p1_screen
  @30_000 外首个净空窗，selftest L4 机闸零命中（152 登记值+N1 全在用带+N3 70_000+
  域全 disjoint 实证）。
- probe 种子 95_004=出带设计探针（N1 95_002/95_003 先例；永不登记、永不入批账本、
  ledger +0——本窗 probe 实证已按此律落盘）。

## §6 跑后只许回填节（占位）

- [ ] §7 跑后实证（回填 source=）
- [ ] §8 判决与账本行（回填 prev_total→total）

## 附：slice 分工账（防重复开发·跨窗接力）

- **slice-1（r510 bm-a 本窗·已落地）**：runner 骨架+subspace 绘制层+probe 真跑+
  selftest 8 腿+本草案；产物 results/perpetual_faces/_n2_w15_probe.json。
- **slice-2（下窗）**：generate/screen/screen_finalize/run 分片/池握手/finalize 腿
  +selftest 扩腿（真跑冒烟=r494 律）。
- **slice-3（freeze 窗）**：三带登记+banned_gate+冻结 commit→生成器 N2 supply 物化
  →daemon 烧批→finalize→§7/§8 回填。
