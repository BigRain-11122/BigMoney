# T18_DEEP_REVAL 预注册 —— 深史主轴复验批（25 年轴·6 员全量预注册复验）

> 权威链：research/BACKTEST_SCIENCE.md §10 D7（CEO 亲令 O-20260924-1141）· 票 T-2026-09-24-18 · O-20260924-1310 §3（调整视图先行序）· O-20260924-1136（算力满载令）· PREREG_TEMPLATE v2。
> **本批性质=复验（revalidation）：对 6 名在册交易员的注册配置在深史轴上重读证据。零注册变更、零新信号、zero-touch 注册件/scorecard/paper。**
> 冻结纪律：本文跑前 commit 冻结；§7 占位纪律跑前必须为空，写数字即造假；跑后只许回填 §7 与 §8。

## §0 批件身份【跑前】
- 批名 / 批号：`T18_DEEP_REVAL`（账本 batch 名 `t18_deep_reval`）
- 认领：F-04 先行——r96 已认领（T-18 claimed_at 2026-09-24 13:05，bm-b OS 循环轮）；本预注册=票面 NEXT 指针兑现（spec 轮，零引擎零账本）
- 部门归属：dept:研究+数据
- 算力预算：nulls/reval/pbo 重阶段一律**分离后台+checkpoint 跨轮**（R41/r52 轮龄律）；**BelowNormal 低优先池**（O-1136）；workers=floor(核×0.8)（bm-b=12）+RAM 护栏 freeGB/0.5；**与 XSTOCK build/post 链数据目录互斥**（票据注记：Money02 cache 竞争——重阶段点火前查 XSTOCK 构建进程态）；批报告必带 audit 段（无 audit 段不入账本）。
- 批内格数预算（N_eff 买单，实测以跑时活数为准）：6 员深轴跑 + K=50 null + 被动 2（EW 月度/BH）+ 家族网格深轴重跑（J15 10 格 + J19 4 格 + G2_FOLK 三族冻结网格）≈ **96±10 格**。

## §1 α 机制段【D6——复验批适用条款】
- 本批**不产生新信号/新函数**，机制主张原样继承各自注册件（VOLATILITY-CE-01=低波防守溢价；COMPOSITE-CE-01/-02=复合因子轮动；ENGULF/NEEDLE/DROUGHT=反转-确认谱系，见 firm/traders/ 注册件机制段）。同族相关性准入（max|corr|≥0.7 拒收）**不适用**（无新构造入队）。
- **深轴语义变体披露（诚实条款）**：增长成员制下横截面排名只在当日 warmup-valid 成员内计算（§2），2013-2019 段横截面仅 14-45 员（vs 注册证据 48 员全横截面）——深轴读数与 6.7y 注册证据的可比性为**方向性（robustness 方向）而非等价**，报告全文携带此披露。

## §2 数据与面板【跑前探针事实，非结果】
- 宇宙：core48 固定名单（注册池零变更）；面板源=**前缀孪生文件**（37/48 长于裸码、11/48 等长、0 缺失；探针 spotcheck 3/3 重叠段 close 逐位 diff=0.0）；**裸码文件零触碰**（live.paper 锚定复现面板禁漂移，探针已否决「prepend 进裸码」方案）。
- **增长成员制面板（growing-membership）**：每员 `valid_from` = 孪生起始日 + **252 交易 bar**（冻结 warmup=252，覆盖 6 员全体信号构造最大回看 high252/mom_12_1）；横截面排名只在当日 valid 成员内、且 **≥5 员门**（MIN_Z_NAMES=5 先例）；`panel_start` = 首个 ≥5 员 valid 的交易日（跑时由门计算并冻结进 manifest，禁手写）。
- **evidence_cutoff = 2026-09-22**（孪生文件实测末日，与注册锚定 cutoff 一致；裸码 09-23 bar 在窗外如实披露）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必须带 `science_gates.cutoff_meta(2026-09-22)` 字段（缺=science_audit C2 VIOLATION）。
- IS 切分（**D2 烧穿如实**）：IS1 = panel_start → 2024-12-31；IS2 = 2025-01-01 → 2026-09-22（**降格稳定窗，禁称样本外**）；full = 全轴。6.7y 注册窗读数保留为对照列。
- **数据完备门（P-1d 范式：不过门禁跑批，全部跑时活算零写死）**：
  - **GA** 孪生-裸码重叠段全量 48/48 逐位一致（max|Δclose| 容差 0；探针 spotcheck 3/3 升格为全量门）
  - **GB** 每员完备性：warmup 后有效行 ≥252、close NaN 率 <0.5%、日期严格单调、无负向跳日（本地 ETF 日历容周末/节假日）
  - **GC** bars 锚：Money02\data\bars 文件数 ==10444（数据本地核验零网络，T-01 闭环口径）
  - **GD** 断点登记册继承复derive：21 事件/0 pre-2020，与 data/consolidation/registry.json bit-match
  - **GE** manifest 确定性冻结：results/shortline/t18_deep_manifest.json（每员 twin_start/valid_from/rows + panel_start；双跑确定性）；面板缓存=Money02/data/cache/t18_deep_panel/（gitignored 可再生）
  - **GF 调整视图硬门（O-1310 §3 字面执行）**：T-19 调整视图交付（票 note 记 GM 裁决 + guard/调整面板方案落地件在盘）**或** O 册 GM 明示豁免——二者居一才放行 **nulls/reval/pbo 跑阶段**（exit 2 禁跑）；gates/build 基建阶段不受 GF 阻（防 25 年轴跑进幻影跳变=约束跑数不约束建面板）；本批跑数用 **RAW 面板**（注册语义不变）+ 每员断点暴露披露列（trade∩break 打标，复用 T-19 stage-1 机件）。

## §3 方法学【跑前冻结】
- **6 员复验跑=注册配置逐字复现机件**：live/paper.py SIGNAL_BUILDERS + ExitPatch + 比较器（P3/EW6/g25 先例，禁重写防漂移）；**锚定门 6/6（6.7y 窗注册证据逐位复现）=批前置硬门**，漂移即批无效禁跑深轴。
- **null 深轴重生成**（D7 §10「滚动全量口径」）：复用 p2_null_calibration 随机入场+引擎退出机器；seed 系 **54_000**（本日 rg 全仓空闲实证+已登记 `science_gates.SEED_REGISTRY["t18_deep_axis"]`，r49/r66 律），K=50，入场日期均匀抽取覆盖全轴（rolling full-population）；μ/σ → **深轴技能线 v2** = max(深轴被动+0.10, μ_null+σ_null·√(2·ln N_eff))，N_eff=引擎账本链头+本批格数（数据驱动活算，O-2250 计数单源）；science_gates 加性 null_pool 分支 `t18_deep_axis`（cta_futures/stock_b_layer 先例；**R53 律：分支验收=live probe 双池对照，非仅 selftest**）。
- 被动基线：深轴 EW48 月度再平衡 + 深轴 buy-hold（strict-max 唯一定义）。
- 成本口径：**V1 legacy**（注册证据复现防漂移，双轨律）；×2 成本=描述披露列。
- 引擎语义：默认 T+1/V1 费率/退出机参数=注册件契约零改动（159985 do_not_land 维持，O-1310 裁决）。
- **PBO/CI/DSR 重算**（票 deliverable 3）：每员 DSR=`science_gates.deflated_sharpe_ratio`（原始深轴收益，var_null=深轴 σ；禁 dsr_from_stats 充数）；CI=平稳 bootstrap（science_gates 机件）；PBO=家族网格深轴重跑（J15 10 格 + J19 4 格 + G2_FOLK 三族冻结网格，g25 家族矩阵先例）→ screening/pbo.py CSCV 8 块。
- 账本：`science_gates.append_ledger(batch="t18_deep_reval", batch_trials=实测格数, file_name="results/shortline/t18_deep_reval.json", evidence_cutoff=2026-09-22)`——6 员深轴跑+50 null+2 被动+家族格全计（D7 真新样本①时间深史=合法扩样；家族网格重切如实计账不折免）。

## §4 判据【跑前写死，禁看结果调线】
- **复验判决=证据重读，非晋升/降级**（票面：revalidation report is evidence, not auto-promotion/demotion）：结果只写新件 results/shortline/t18_deep_reval.json + CSV + 本文 §7；firm/traders/、scorecard、paper state 零触碰；任何注册语义变更提案=另开预注册+GM/CEO 门。
- 每员 v2 门重读：`g1_prime_v2(deep_sharpe_full, deep_returns, batch_cells, n_trades, n_entries)` 用深轴 null_pool；G2 资格列 `g2_registration_v2(g1_pass, dsr_deep, pbo_deep)` 一并重读；批报告逐列披露 skill_line_deep/bootstrap_ci/trade_gate 全输入。
- 保留描述条款（批级披露）：IS1/IS2 双正、无崩年（worst_year）、回撤、×2 成本列。
- **有效样本四必报**（D7·每员+null 中位）：IS2 交易笔数、覆盖年数、独立政体窗数=floor(有效交易日/63)、CI 宽度（95% 上-下界）。
- 门禁链损耗账 gate_attrition.json 追加一行（kind=measurement）。

## §5 跑前预测【写死于跑前；跑后对账】
1. **深轴技能线 v2 显著低于现行 0.93**：null σ 随轴长收缩 + 被动项回落（深轴覆盖 2013-2016 熊/2018 磨底），预测深轴线 ∈ [0.45, 0.85]。
2. **政体依赖复现**：6 员深轴 full Sharpe 全员低于各自 6.7y 窗 OOS 读数（2025+ 政体红利被稀释）；VOLATILITY 防守袖相对位次上升（2015-2016 熊段=防守 habitat）。
3. **增长成员窗噪声放大**：旋转类（COMPOSITE 双员）深 IS1 读数降幅 > 非旋转类（14-27 员横截面 vs 48 员全截面）。
4. **DSR 全员改善（轴长 3.8×）但仍 <0.95 @ 现链头 N_eff**（账本深度主导不变）；CI 宽度全员收窄。
5. **pre-2015 诚实边界带**（D5 指数级边界）：≥1 员 pre-2015 段 trades<10 薄样本如实披露。
6. **断点暴露不新增**：GD 门=0 pre-2020；CE-01/CE-02/DROUGHT 21 事件暴露面与 6.7y 窗一致（事件全在 2021+）。

## §6 产物
- scripts/t18_deep_axis.py（子命令 gates / build / nulls / reval / pbo / selftest；探针先行+等价门纪律）
- results/shortline/t18_deep_manifest.json（tracked）+ 面板缓存（gitignored）
- results/shortline/t18_deep_reval.json（顶层 evidence_cutoff + audit 段 + 四必报字段）+ t18_deep_reval.csv
- 本文 §7/§8 回填；STRATEGY_LIBRARY 深史轴行；HANDOVER 产物清单行

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】
（跑后回填：门禁读数逐项 / 6 员深轴 vs 6.7y 对照表 / 四必报全字段 / 工程修复双跑留痕）

## §8 批后复盘【必填·s7-T】
（跑后回填：预测对账（对/部分/错逐条）/ 门禁链损耗账行 / 判线深轴读数披露 / zero-touch 执行确认）
