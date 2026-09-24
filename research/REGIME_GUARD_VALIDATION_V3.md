# REGIME_GUARD_VALIDATION_V3 — 行情防线 v3 结构重预注册（T-10 deliverable-2 正式件）

> 权威通路：fleet/tasks/T-2026-09-24-10-P1（GM 派单 O-20260924-1045 裁决，claim 52cc2c9 r90）
> ＋ research/T10_REGIME_V3_DESIGN.md（r90 设计定案备忘：deliverable-1 归因＋§2/§3 两拧法，本件逐字收录）
> ＋ research/REGIME_GUARD_VALIDATION_V2.md §8（v2 G1 差 1.5pp 判负＋GM/CEO 重审证据包）
> ＋ firm/risk/REGIME_GUARD.md §3.4（未过门修阈值须重新预注册重测）。
> 本件=v3 正式预注册，**跑前写死**；replay（deliverable-3）=下一早龄轮一次定稿。
> shadow-live 探测器（market_regime.py probe()）继续 v1 口径不动——法文件 §1 修订在
> 「校准过门 + GM 批 + 7 天否决窗」之后另轮；本批零行为改动、纯测量。
> 执行体：bm-b OS 循环轮（T-10 认领延续）。
> 元数据：evidence_cutoff（交易员面板侧）=2026-09-22；回放 bench 尾=2026-09-23（v2 同款双口径）。
> 路径规范化：设计备忘 §五 写 `research/shortline/REGIME_GUARD_V3.md`，本件按 v1/v2 家族惯例
> 落 `research/REGIME_GUARD_VALIDATION_V3.md`（同族文件同目录、命名连续性优先，如实记）。

## §0 批件身份【模板必填】

- 批名/批号：REGIME_GUARD_VALIDATION_V3（replay 腿）；批内引擎跑=0（状态机回放=纯测量，
  ledger_trials_added=0，corr-watch R36「记录格复现类」先例）。反事实腿（§4.5 分段）=
  +12 引擎跑，`append_ledger(batch="regime_guard_calibration_v3", 12, evidence_cutoff="2026-09-22")`。
- 认领：T-2026-09-24-10-P1 claimed by bm-b（OS 循环轮 r90，claim commit 52cc2c9）——本批在
  该任务单内，无新 MSG 认领需求（任务单即车道锁）；本机 XSTOCK 收割车道（r88 起）与本批
  文件面零重叠。
- 部门归属：dept:风控+研究（org_chart v3：风控部=行情防线 mandate，研究部=回放方法学）。
- 算力预算：replay=单确定性回放＋单元门（v2 实测分钟级）；反事实 12 腿（r58 实测分钟级）
  ——均 <10min 可轮内，无后台化强制项。
- 机制段（模板 §1 适配声明）：本批=风险状态机校准批，非策略批——勾选**结构性**
  （状态机立法语义再设计：B 部分释放＋C 多维确认，机制论证见 §1 表），α/D6 同族准入
  **结构性 N/A**（无新交易信号函数入池；反事实腿 1:1 复用在册六员，无新函数）。

## §1 v2→v3 变更清单（两拧法并用·阈值数值零改动·T10_DESIGN §二逐字收录）

| 项 | v2 映射 | v3 映射 | 依据（T10_DESIGN §二） |
|---|---|---|---|
| **拧法 C：橙级多维确认** | ORANGE=crash −8%档 ｜ vol>p95 ｜ 广度崩塌，任一单维即橙 | ORANGE 触发需 **≥2 维同日同框**（维度集={crash10d∈(−12%,−8%], vol20>3y p95, 广度≥80%+负斜率}）；**单维触发日=YELLOW**（×0.5 sizing 仍生效） | FA 8/14 集中在单维慢烧政权；真危机（2020.3/2022.3-4/2022.9-10/2024.1）全多维同框——多维确认是危机的教科书签名 |
| **拧法 B：RED 部分释放** | 降级一律需连续 2 绿信号日（多级直落绿） | **RED→ORANGE 降级改「首绿日即可降橙」**（首绿日 state=ORANGE, streak=1）；RED→GREEN 仍需连续 2 绿（第 2 绿日多级直落绿保留）；ORANGE/YELLOW→GREEN 降级语义**逐字不变** | RED 是急性危机态，−12% 十日速度急性期数日内自愈，急性期后残险=橙级非现金停泊级；r58 反事实实证 RED 掩蔽=α 代价最高态，应只覆盖急性期 |
| RED 触发 | crash ≤−12% ｜ panic ≤−5% | **逐字不变**（RED 不需多维确认——急性危机语义本身即签名） | 同上 |
| YELLOW 触发 | crash ≤−5% ｜ vol>p80 ｜ 广度 ≥65% ｜ 事件窗 ｜ R-配3 大熊市 | **逐字不变** ＋ C 降格的单维橙日落点=YELLOW | — |
| R-配3 大熊市 | YELLOW（T0 ≤20% 帽零触碰，iron_rules 独立治理） | **逐字不变** | v2 §0 裁定延续 |
| #10 hs300<MA200 | 去收编（不映射任何级；T0 独立存续，接线=另案署名单） | **逐字不变** | v2 §0 裁定延续 |
| 阈值/窗口/事件日历/防抖素材 | v1 常量 | **逐字不变**（−12/−8/−5%、恐慌 −5%、实波 p95/p80、广度 80%/65%+负斜率、FOMC+长假冻结清单全不动） | 禁看结果调线红线（ticket spec「same frozen gates」排除拧法 A=G1 25% 上限本身） |

**两拧法并用理由（memo 原文）**：单用 B 只缩 RED 尾（−40±20 日）不够关 1.53pp 门；单用 C 缩
ORANGE 但 RED 尾不动；B+C 合计预测 R+O 385-430 日带，穿门概率 ~55-70%（诚实带，非达标保证）。

## §2 v3 状态机矩阵（冻结）

- **RED**：crash10d ≤ −12% ｜ panic1d ≤ −5%（任意其一）。
- **ORANGE**：{crash10d ∈ (−12%, −8%]、vol20 > 3y(756) 滚动 p95（基线窗排除当日）、
  广度崩塌（core48 close<MA20 占比 ≥80% 且 5 日斜率 <0）} 中 **≥2 维同日同框**。
- **YELLOW**：crash10d ≤ −5% ｜ vol20 > 3y p80 ｜ 广度 ≥65% ｜ 事件窗（附录 A=v1 §1.1
  冻结清单）｜ R-配3 大熊市 ｜ **单维橙级日（C 降格落点）**。
- **GREEN**：以上皆无；#10（hs300<MA200）**不参与**本状态机任何级（v2 去收编逐字）。
- 全部数值阈值逐字 scripts/market_regime.py v1 常量；v3 决策函数 `raw_level_v3()` +
  `resolve_state_v3()` 加性新增于 market_regime.py（probe()/raw_level()/raw_level_v2()/
  resolve_state() 零触碰，live 仍 v1）。

**防抖精确语义（resolve_state_v3，冻结）**：
1. raw > prev：→ raw（升级即时，v1/v2 逐字）。
2. raw == GREEN：
   - streak+1 后 ≥2：→ GREEN（多级直落绿保留，RED→GREEN 仍需连续 2 绿）；
   - streak==1 且 prev==RED：→ **ORANGE（B 部分释放）**；
   - streak==1 且 prev∈{ORANGE, YELLOW}：保持 prev（v1/v2 逐字不变）。
3. raw < prev 且 raw != GREEN：保持 prev，streak=0（**RED 在非绿日不降级**——字面 B=
   只认绿信号日，保守向；熊市下 R-配3 活跃使 raw 地板=YELLOW 时 RED 降级顺延=已知交互，
   如实冻结不修）。
4. raw == prev：保持（raw==GREEN 时 streak 续累计，同 v1/v2）。

## §3 等价与单元门（跑批前置硬门）

1. **维度序列等价门=v1/v2 §2 复跑**：同 dim 序列供三矩阵消费；8 采样日逐项断言 vs v2
   bench bit-match，不过=批无效。
2. **窗口恒等门**：回放窗 2020-01-02→2026-09-23＝1632 交易日，与 v2 记录（window.days=1632）
   逐位一致；若日线已前向增长（今晚 sweep 后）则 bench 截断到 2026-09-23 再比（R27 数据
   漂移坑律），不一致=批无效。
3. **v3 映射单元门（合成用例，离线，任一不过=批无效）**：
   (a) B 主修复点：prev=RED, raw=GREEN, streak=0 → ORANGE, streak=1；
   (b) 连续第 2 绿：prev=ORANGE(B 释放), raw=GREEN, streak=1 → GREEN；
   (c) 释放后危机回潮：prev=ORANGE(B), raw=RED → RED（升级即时, streak=0）；
   (d) 真橙降级不变：prev=ORANGE(2 维), raw=GREEN, streak=0 → 保持 ORANGE；次日再绿 → GREEN；
   (e) RED 非绿日不降级：prev=RED, raw=ORANGE → 保持 RED, streak=0；
   (f) 单维橙日降黄：crash −9%（无其他维）→ YELLOW；
   (g) 双维橙：crash −9% + vol>p95 → ORANGE；
   (h) 双维橙：crash −9% + 广度崩塌 → ORANGE；
   (i) 单维 vol>p95 → YELLOW；
   (j) 单维广度崩塌 → YELLOW；
   (k) crash ≤−12% 单维 → RED（不需多维确认）；
   (l) panic ≤−5% 单维 → RED；
   (m) R-配3 大熊+其余平静 → YELLOW；
   (n) #10 成立+其余平静 → GREEN（去收编实证）；
   (o) 事件窗 → YELLOW；
   (p) 已知交互：prev=RED, raw=YELLOW（R-配3 活跃地板）→ 保持 RED, streak=0。

## §4 度量与门禁（same frozen gates·T-10 spec 逐字沿用 v1/v2 §3）

1. 状态分布/占比＋转移矩阵（v1 §3.1 同法）。
2. 误报率定义逐字 v1 §3.2：升橙 20 日内再跌幅 <5% 记误报；升黄 10 日内最大回撤 <3% 记
   误报；截断回合单列不入主率；ORANGE 回合 <8=FA 主率统计力不足，主率照报＋小样本标注
   （v2 §4.9 条款延续）。
3. **披露列（测量非门禁）**：单维橙日降黄日数（C 削减面）；RED 首绿释放日数（B 释放面）；
   R-配3 raw 黄日数；#10 成立日数；事件腿黄日数；v1/v2/v3 三表对照。
4. **过门判据（enforce 前置，逐字冻结）**：G1 RED+ORANGE ∈ [2%, 25%]；G2 ORANGE 误报率
   ≤60%（主率）；G3 状态序列零空档。三门全过=校准 PASS → enforce 提案**独立呈 GM**
   （+7 天否决窗＋法文件 §1 修订轮）；任一不过=诚实 FAIL → **防线立法失败呈 CEO**
   （两拧法已用尽，不再有 v4 自主迭代——T10_DESIGN §三收线条款逐字）。
5. **反事实（分段腿，下轮同本 prereg 续跑，r58 先例）**：6 员 × {baseline,
   v3-ORANGE/RED 日禁开新仓} 12 引擎跑（同一 harness；掩蔽=entry 在 v3 状态 ORANGE/RED
   日清零、状态只用 ≤t 数据；锚定门 6/6 先行）；YELLOW 入场普查披露（×0.5 sizing 影响
   面，引擎 sizing 仿真延至 GM 批阶段）；账本 `append_ledger(+12,
   batch="regime_guard_calibration_v3")`；v2 对照值=r58 实测引用非重跑。

## §5 跑前预测（T10_DESIGN §四逐字收录·跑后 §8 对账）

1. RED 179→**120-150 日**（急性期剥离，4 簇尾驻留被 B 切走 30-60 日）。
2. ORANGE 254→**140-220 日**（C 删单维日 −60~−110；B 从 RED 尾回收 +30~+50；净额不确定
   度大，如实带）。
3. R+O 合计 **385-430 日（23.6-26.3%）**：G1 PASS 概率 ~55-70%；**若 C 的单维日削减被
   B 的回收抵消则 FAIL**。
4. ORANGE FA **30-55%**：episode 数降至 8-12、FA 计数降或平 → G2 PASS 概率 ~80%。
5. G3 PASS=确定性（状态机每日必归属）。
6. 反事实：R+O 掩蔽面收缩 → 六员 Δ年化负幅全面收窄（vs v2 −0.63~−1.80pp）但方向不变
   （反转确认族 α 栖息地规律不变）。

## §6 工程纪律

- `scripts/market_regime.py` 仅加性：`raw_level_v3()`（决策逻辑单源）＋`resolve_state_v3()`；
  probe()/raw_level()/raw_level_v2()/resolve_state()/既有 selftest 零改动；阈值指纹与
  science_audit C6 预注册指纹保持一致（零阈值改动即零指纹漂移）。
- `scripts/regime_calibration.py` 加性：`replay(matrix="v3")` → `results/regime_calibration_v3.json`
  （独立产物，不覆写 v1/v2 件）；selftest 扩 v3 单元门 §3.3 全用例；**CLI 分发一律
  `startswith` 前缀匹配**（r58 覆写事故坑律：回退分支重写产物文件=数据丢失类事故，
  分发条件与写路径必须成对审查）。
- 分段执行合法：replay 腿=一次定稿；反事实 12 腿=下一轮同 prereg 续跑（v2 §5 先例）。
- 零阈值改动；跑后禁重跑禁翻案（产物写坏=确定性重执行合法口径）；工程修复重跑=双跑留痕
  如实记账（G2_FOLK 先例）。
- live shadow 探测器、iron_rules、REGIME_GUARD.md 法文件、paper/交易员注册件：零触碰。
- 结果 JSON 顶层必带 `evidence_cutoff="2026-09-22"`（C2 合同，v2 同款）＋`prereg` sha
  记录（冻结 commit sha 随跑注入）。

## §7 实证结果（跑前必须为空——占位纪律：写数字即造假）

**replay 腿（2026-09-24 r94 bm-b 一次定稿+一次确定性重执行，见下）**：

- 硬门全过：维度序列等价门 8 采样日 vs 点函数逐项一致（ok=true）；窗口恒等门
  1632 交易日（2020-01-02→2026-09-23）与 v2 记录 bit-match。
- 状态分布（占比）：GREEN 664（40.69%）｜YELLOW 772（47.30%）｜ORANGE 35
  （2.14%）｜RED 161（9.87%）。**R+O=196 日=12.01% ∈ [2%, 25%] → G1 PASS**。
- 转移结构：RED 入口 5 次（YELLOW→RED ×4＋ORANGE→RED ×1=释放后危机回潮，
  §3.3(c) 单元场景实弹）；**全部 5 个 RED 回合经 B 首绿释放收尾（RED→ORANGE×5），
  逐一兑现「急性期后残险=橙级」设计假设**；ORANGE 35 日=B 释放驻留＋唯一一个
  多维橙回合（入口 2021-03-05），出口 ORANGE→GREEN×5＋ORANGE→RED×1。
- 误报率：ORANGE 回合=1（main=1，**<8=统计力不足小样本标注触发**）、FA=0.0%
  → **G2 PASS（机械判）＋低统计力注记**；YELLOW 回合 81、FA 82.72%（不设门，
  披露——黄级吸收 C 降格 120 日＋R-配3 187＋事件 65 后主形态=慢烧政权预警）。
  **G3 零空档 PASS**。
- 披露列（§4.3）：C 削减面=单维橙日降黄 120 日；B 释放面=5 日（首绿释放次数）；
  R-配3 raw 黄日 187；#10 成立日 799（状态机失明面不变）；事件腿黄日 65。
- 三表对照：R+O 占比 v1 61.6% → v2 26.53% → **v3 12.01%（首个过 G1 门）**；
  ORANGE FA v1 81.8% → v2 57.1% → v3 0.0%（回合数 14→1）。
- **verdict=PASS（三门全过）= 行情防线立法线首个校准过门**（v1 FAIL/v2 FAIL 后）。
  enforce 提案仍须先补反事实腿（§4.5）再独立呈 GM——G2 低统计力注记（ORANGE
  回合=1）必须随提案原文呈现，PASS 判定不因小样本回撤（冻结判据逐字）。
- 工程留痕：首跑产物 v3_disclosures.red_first_green_release_days=19 系披露列
  bug（对对计数误含 2012-2019 预窗链日），修复为窗口对计数后确定性重执行一次
  （§6「产物写坏=确定性重执行合法口径」），核心数字（counts/share/FA/转移/三门）
  双跑逐位相同，仅该披露列 19→5（=转移矩阵 RED→ORANGE 精确一致）。两跑如实记账。
- 账本：replay 腿 ledger_trials_added=0（状态机回放=纯测量）；反事实腿 +12
  （batch=regime_guard_calibration_v3）=分段腿下轮续跑（§4.5）。

**反事实腿（2026-09-24 r95 bm-b 一次定稿，`counterfactual-v3` 12 腿，15s）**：

- 硬门全过：六员 baseline 锚定 6/6 逐位复现注册证据（anchor gate）；状态序列
  重推导 counts 与 replay 记录逐位一致（防漂移门）；掩蔽面=v3 ORANGE/RED
  196 状态日全落面板（mask_days_window=mask_days_panel=196）。
- 主读数（ΔSharpe / Δ年化 / Δ笔数 / 被禁 entry 占比）：CE-01 **+0.2168 /
  +0.46pp / −31 / 10.4%**；CE-02 +0.0048 / −0.42pp / −61 / 10.4%；
  DROUGHT **+0.3268 / +0.38pp / −11 / 11.9%**；ENGULF **−0.3221 / −1.11pp /
  −34 / 26.9%**；NEEDLE **−0.2540 / −0.76pp / −20 / 39.9%**（全员最高）；
  VOLATILITY +0.0168 / −0.11pp / −30 / 9.7%。
- 三表对照（掩蔽面 v1 1005 → v2 433 → v3 196 日）：ΔSharpe 负员 4/6 →
  4/6 → **2/6**；Δ年化全负带 −1.36~−3.80pp → −0.63~−1.80pp → **−1.11~−0.76pp
  （仅 ENGULF/NEEDLE 双员负）+0.38~+0.46pp（CE-01/DROUGHT 转正）**；
  Δ笔数 −62~−415 → −415 附近 → **−11~−61 全面轻量化**。
- 黄级普查（x0.5 sizing 影响面，引擎 sizing 仿真按 §3.5 延至 GM 阶段未实现）：
  黄日 entry 吸收 CE-02 5608 / VOLATILITY 3855 / CE-01 3505 / ENGULF 653 /
  DROUGHT 552 / NEEDLE 160——高换手员（CE-02/VOLATILITY）黄级 sizing 影响
  面为橙红掩蔽面的 ~5-7×，enforce 提案的黄级条款（×0.5 sizing）经济权重
  **高于**橙红停开新仓条款，提案必呈本普查。
- 账本：+12 落账（prev 3065 → total 3077，evidence_cutoff=2026-09-22，
  top-level trials_ledger 单源）。

## §8 跑后对账（§5 预测逐条 vs 实证·replay 腿）

1. RED 179→120-150 预测 vs **实际 161**：**偏高侧 MISS**（+11 越带）。B 实切
   −18 日（179→161），设计备忘「簇尾被 B 切走 30-60 日」高估——RED 驻留的
   削减只来自更早出口（首绿 vs 次绿），R-配3 黄地板仍阻多日 RED 驻留截断。
2. ORANGE 254→140-220 预测 vs **实际 35**：**大幅低侧 MISS**。C 削减面 120 日
   ＋v2 橙态中的防抖驻留日随 C 降格同步离开橙级；「B 从 RED 尾回收 +30~+50」
   方向对量级错（实际回收仅 5 次释放＋短驻留）。C 主导、B 边际。
3. R+O 385-430 日（23.6-26.3%）预测 vs **实际 196 日（12.01%）**：**低侧 MISS
   但方向有利**——G1 PASS 靠比设计预期深得多的削减拿下，过门成立而预测模型
   （防抖交互的量化先验）连续第三次失准（v1 §4.5 全错、v2 §4 低估、本条）。
4. ORANGE FA 30-55%、回合 8-12 预测 vs **实际 FA 0.0%、回合 1**：**低侧 MISS**。
   C 多维确认削得只剩 2021-03-05 一个多维回合；G2 机械 PASS＋冻结低统计力
   条款如实触发（§4.2 小样本标注），提案呈现时不得省略。
5. G3 PASS=确定性：**✓ 应验**。
6. 反事实六员 Δ年化收窄方向：**半对**。收窄侧 ✓——负幅全面收窄且深于预期
   （v2 −0.63~−1.80pp → 仅双员负 −0.76/−1.11pp，且 CE-01/DROUGHT 转正
   +0.38/+0.46pp=掩蔽在 v3 危机簇上对 4/6 员中性偏正）。方向侧部分
   MISS——「方向不变」对深负确认族成立（ENGULF −0.32/NEEDLE −0.25 保号，
   α 栖息地规律在其栖息族内第三次实证），但「六员」全称主张过宽：v2 微负员
   （CE-02 −0.012/VOLATILITY −0.304）在 v3 窄掩蔽下回到噪声带（+0.005/+0.017），
   v1 的 VOLATILITY −0.304 深 Δ 系 1005 日宽掩蔽的产物。**净读数=危机窗
   掩蔽的真实代价集中在反转确认双族（ENGULF/NEEDLE），防守/复合族代价在
   v3 收窄后近零**——enforce 提案按此分族表述。

## §9 结论与法定后续（收线条款·冻结）

- replay 一次定稿诚实判定：PASS → enforce 提案独立呈 GM（GM 批＋7 天否决窗＋法文件
  §1 修订另轮）；FAIL → 诚实 park 呈证据包，**防线立法失败呈 CEO，本节点不再自主迭代**
  （两拧法已用尽；三门两 FAIL 三连即防线立法失败——T10_DESIGN §三逐字）。
- s7-T 批后复盘：预测对账＋`results/gate_attrition.json` 追加一行（measurement 型）＋
  回执入轮报告＋CODELY.md 行级追加；反事实腿完成后账本对账（+12）。
- T-13（深史主轴复验）与本批关系=lane-affine 素材共享（510300 深史），互不阻塞；
  XSTOCK 收割车道（本机主车道）优先级高于本批 replay 排程（T10_DESIGN §五）。
