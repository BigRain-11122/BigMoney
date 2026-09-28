# INNOVATION_QUOTA_W2_PREREG · 创新配额槽-2：逆回购日历期限摆动族长期限扩展（REPO-CALENDAR-P2）judged 判决批

## §0 批件身份。【跑前。】

- 批名 `REPO_CALENDAR_P2`；批内格数 `batch_cells`=**4002**（2 judged 格 + 2000 随机日历掩码 × 2 格结构 null 评估=4000 null draws·每格自有 2000 抽 null 池）——扩容即买单。
- 认领：F-04 先行=本批 MSG `fleet/inbox/MSG-20260928-2140-bmc-all-innovation-slot2-prereg-freeze.md`（r183 bm-c·2026-09-28 21:4x）；梯目录条目 `Tools/fill_ladder_catalog.json` `INNOVATION-QUOTA-SLOT-2`（T-2026-09-28-107 §4(d) 槽位制·catalog tranche-2）。
- 部门归属：dept:研究。
- 算力预算：null 4000 draws+虚拟起点 2000 窗+分窗 200 面≈W1 量级（分钟级~十分钟级）→ 梯子入池后台烧（runner_exists 门自开后 autofill 消化·>5min 批禁轮内内联）；批报告必带 audit 段。
- 供给律锚：r182 轮指针主针（supply_floor ready=0<3 破线·streak 274.6min GM 升级面）+ TRIAL_LABOR_LAW §1 常供律（板空/池饿=默认起草下一波）。

## §1 α 机制段。【四选一+论证·D6 门槛。】

- [x] **结构性**：逆回购期限利率=资金借方（机构）为跨日历紧点融资支付的结构性溢价——月末/季末监管考核+长假前备付=日历紧点资金需求尖峰（隔夜利率尖峰）+期限锁定的流动性让渡溢价（term premium）。由谁付出代价=跨紧点借资金的机构借方（监管/备付约束刚性需求方）。P1 批内新事实「锁定期溢价须够长才可检」（GC007 19.35<μ_null 判负 vs GC014 29.20/GC028 34.83 过线）=本批直接证据驱动：检验期限梯度是否延续到 91/182 天。

**同族相关性准入检查【必填·D6】**：
- 与在册 6 CE 员（core48 股票面·`cn_rev_tilt_p1.load_member_rets` 复用）：跨资产预期 |corr|<0.1（先验披露·W1 同款）；runner 实测 `max|corr|` ≥0.7 → **拒收**（对 CE 员面）。
- 与 P1 在册 3 eligible 格（CAL-SWITCH-GC014/QW5-GC014/CAL-SWITCH-GC028·现金腿袖候选池同族）：**族内高相关=预期事实**（同一现金腿袖家族扩展），族内 corr 逐对披露**不拒收**——袖内塌缩语义：若 P2 格过格，入册并入同一现金腿袖候选池（非独立成员主张·防 N 膨胀）；批内 2 格 pairwise |corr| 照测披露。

## §2 数据与面板。【跑前探针事实·冻结引用件=本节锚（r183 bm-c 实测探针·2026-09-28 21:3x-21:4x）。】

- **G-ANCHOR-FACE 四元组**（每个数字探针锚·O-20260928-1712 律）：
  - GC001 历权威面：`data/repo_daily/GC001.csv` / raw `pd.read_csv` 直读截 cutoff / 2011-05-13 起算（面板首行）/ 无预热窗（利率序列直读零预热）——rows=**3735**、last=**2026-09-22**（cutoff·W1 冻结同面）。
  - GC091 全史面：`data/repo_daily/GC091.csv` / raw `pd.read_csv` 直读截 cutoff / 2006-11-01 起算 / 无预热——rows=**3689**、last=**2026-09-22**、close 带 [**0.5150, 5.9500**]、中位 **2.6950**。
  - GC182 全史面：`data/repo_daily/GC182.csv` / raw `pd.read_csv` 直读截 cutoff / 2009-01-13 起算 / 无预热——rows=**3376**、last=**2026-09-22**、close 带 [**0.0250, 5.8000**]、中位 **2.6000**。
  - **GC091 格窗**（=GC001 交易历截到 GC091 窗内首日）：`data/repo_daily/GC001.csv` 历 / raw `pd.read_csv` / **2011-06-16** 起算 / 无预热——cal_rows=**3712**、month-end last-2=**368**、pre-longholiday last-2=**192**、union=**454**、**期限缺日=145**（GC001 历上有、GC091 无成交行的交易日）。
  - **GC182 格窗**：同历 / raw `pd.read_csv` / **2011-09-08** 起算 / 无预热——cal_rows=**3652**、month-end last-2=**362**、pre-longholiday last-2=**192**、union=**448**、**期限缺日=281**。
  - 历外日=**0**（GC091/GC182 全部日期 ⊆ GC001 交易历·r183 探针实测）——runner fail-closed 复验。
- **探针-锚同面断言**：runner 探针实载路径与上述锚声明路径逐位比对——一面不相等=**面错配 VOID**（fail-closed 拒烧·报「面错配」非「数据腐坏」·INCIDENT-20260928 立法）；计数锚（rows/窗掩码计数/缺日数）全不相等即拒烧。
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板一律截断到 cutoff **2026-09-22**；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必须带 `science_gates.cutoff_meta("2026-09-22")` 字段（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批）：①GC001/GC091/GC182 last row==cutoff；②rows 锚逐位相等（3735/3689/3376）；③close 带 (0,200) 且全有限值；④历外日=0；⑤截窗掩码计数锚逐位相等（368/192/454/145 与 362/192/448/281）。

## §3 方法学。【必填。】

- **引擎（W1 冻结态机扩展·长期限缺日回退律·本节冻结）**：决策发生在交易日收盘；窗口日（月末末2+长节前末2·格窗自身历上再推导·W1 同法函数复刻）→隔夜 GC001（d 决策→d+1 单日计息 close/365）；非窗口日→期限 GC-k 锁定 close_k(d)/365 × k 自然日（GC091 k=91/GC182 k=182·到期后首个严格晚于到期日的交易日再决策·无中途解约）；**期限缺日回退律**=非窗口决策日遇期限无成交行→回退隔夜 GC001（真实约束=当日该期限不可得·零编造零 ffill·回退日计数锚披露 145/281）；日收益=逐自然日计息累乘·无持仓自然日计 0；Sharpe 年化=共享库 PERIODS_PER_YEAR（口径单源）。
- **judged 格（2 格冻结·批内零选优）**：`CAL-SWITCH-GC091`（窗口日滚隔夜·余日 GC091 期限滚动·格窗 2011-06-16 起）；`CAL-SWITCH-GC182`（同窗口·GC182·格窗 2011-09-08 起）。passive 基线=各格自身窗上 `PASSIVE-GC001-ROLL`（每日滚隔夜·格窗历再推导）。
- **null 对照**：K=2000 随机日历摆动掩码——保各年 union 窗日数（摆动强度保真）毁日历位置；每掩码在**两格结构**上各评估一次（每格自有 2000 抽 null 池·skill_line 逐格自有 μ/σ）；seed 基 `innovation_quota_w2_repo`=**20298500**（rng([20298500,k])·k<2000 掩码；k∈[2000,3000) 虚拟起点·k∈[3000,3100) 分窗）；**RANDOM_LARGE_SAMPLE_LAW**：虚拟起点 K=1000（6m/12m/24m=183/365/730 自然日窗·beat=格窗累计>passive 同窗）+随机分窗 100（半窗 Sharpe 同号率 ≥80%=segment-stable）。
- **成本口径**：费前口径（W1 §3 同款诚实披露：回购佣金极低）；**若判正入册前费后复核=冻结条件**（T-112 先例·FEE-RECHECK 机制·b*≥1bp/次 判读线·入册必过）。
- 账本：`science_gates.append_ledger("REPO_CALENDAR_P2", 4002, "results/innovation_quota/REPO-CALENDAR-P2.json", evidence_cutoff="2026-09-22")`（dict schema 唯一禁手抄 prev）。

## §4 判据。【跑前写死，禁看结果调线。】

- **G1' v2**：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=4002, n_trades, n_entries)` 逐格（skill_line_v2=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))·passive=该格自身窗 PASSIVE-GC001-ROLL 年化）；批报告逐列披露 skill_line/passive_term/null_term 全输入；胜率+回合期望双披露（O-1524 KPI 律）。
- **G2 注册资格 v2**：G1' 过 ∧ DSR≥0.95（`deflated_sharpe_ratio` 原始收益）∧ 族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·2 格矩阵）——过格=并入现金腿袖候选池（**袖内塌缩语义·非独立成员**·D6 族内披露面）；不过=judged-negative 族关单+新证据重开注记（RANDOM_LARGE_SAMPLE_LAW §5）。
- **RANDOM_LARGE_SAMPLE_LAW 绑定**：K=1000 虚拟起点 beat_rate 三窗全披露；100 随机分窗同号率 ≥80%。
- 硬界设计三件套：判线=分布界口径（null p95/中位承载）；利率上尾=收益有利向（2013-06 钱荒/2015-02 春节前 53.44/2015-07 股灾周窗口日隔夜尖峰=正尾·逐日单列披露）；跑前极端日先验=§5。

## §5 跑前预测。【写死于跑前·≥3 条。】

1. **期限梯度延续性**：若「锁定期溢价须够长才可检」梯度延续，CAL-SWITCH-GC091 s 预测 ∈ **[26, 36]**（过线带）；GC182 受缺日回退侵蚀（281 日≈7.7%）+放置稀疏（~2 次/年）→ s 预测 ∈ **[20, 30]** 边缘带（不过线风险如实=「过长锁定=结构衰变回随机」族边界事实候选）。
2. **放置数/门风险**：GC091 决策放置预测 **60-100**（≥30 门稳过）；GC182 预测 **31-45**（F6 ≥30 门**边缘风险披露**——若 <30=trade gate 诚实拒收非机制证伪）。
3. **pickup 预测**：GC091 年化 vs passive pickup ∈ **[+300, +900]bp**；GC182 pickup < GC091（缺日回退+低换手侵蚀日历溢价·可能 <+300bp）。
4. **null 面**：两格各对自有 null p95——GC091 预测 ≥p95（期限溢价 91d 尺度日历可检）；GC182 若 <p95=预测的族边界读数如实。
5. **极端日先验**：2013-06 钱荒窗+2015-02-10（GC001 53.44 正典锚）+2015-07 股灾周的窗口日隔夜单日年化可破 30%——正尾逐日单列；2015 后利率中枢下移→GC091 分窗同号率预测 ≥80%；GC182 同号率可能 <80%（锁定跨段平滑+缺日集中段）。

## §6 产物。

- runner `scripts/innovation_quota_w2.py`（**下轮建·selftest 先行**·梯 runner_exists 门届时自开）→ `results/innovation_quota/REPO-CALENDAR-P2.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+两格全量+nulls/虚拟起点/分窗+D6 表+缺日回退计数锚+funnel 双列）。
- 本冻结 commit 面：本件+SEED_REGISTRY 新行+F-04 MSG+梯目录条目 append。

## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假。】

（一次定稿；工程修复重跑须双跑留痕如实记账。）

## §8 批后复盘。【必填·s7-T。】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数；judged-negative 族=关单+重开注记；回执入轮报告＋CODELY.md 行级追加；若 G2 过格=并入现金腿袖候选池 intake（袖内塌缩·非独立成员）＋**费后复核先行**（T-112 先例·FEE-RECHECK-P2 件承载）。

## §2-补 数据门④历外面冻结时点探针错修法追记。【2026-09-28 r185 bm-c·首燃 GATE-REFUSE(exit2) 后即办·零燃烧零结果预承诺窗内修正·append-only 原文零删。】

- **实况**：SLOT-2 首燃（autofill claim 22:18:49）GATE-REFUSE(exit2)「outside-cal GC091: 122 term dates not on the GC001 trading calendar (first 2006-11-01)」——§2 ④「历外日=0（r183 探针实测）」为**冻结时点探针错**：rows 锚 3735/3689/3376、窗掩码锚 368/192/454/145 与 362/192/448/281、缺日锚 145/281 全部与实数据逐位吻合（真探针跑过），唯历外面误报 0。
- **r185 实测**（raw `pd.read_csv` 截 cutoff 2026-09-22）：GC091 史前段 **122** 行（2006-11-01..2011-03-11·全部早于 GC001 面板首行 2011-05-13）；GC182 史前段 **5** 行（2009-01-13..2010-09-02·同前于 2011-05-13）；**GC001 历程内 [2011-05-13, 2026-09-22] 历外日=0 实证**（两期限序列全部落在 GC001 交易日历上）。
- **根因**：期限面板史起早于隔夜面板（GC091 2006-11-01/GC182 2009-01-13 vs GC001 2011-05-13）——§2 ④ 原文把「窗构建一致性」误写成「全史子集关系」。
- **修法（本节冻结替代 §2 ④「历外日=0」条款·其余条款零改动）**：④' **历程内历外日=0**（GC001 首行..cutoff 内每 GC091/GC182 日期 ⊆ GC001 交易历）∧ **史前段行数锚**=GC091 **122**/GC182 **5**（fail-closed 计数锚·漂移即拒烧）；史前段行**永不入窗**（窗=GC001 交易历截到格窗首日·§2 格窗锚不变）·face 计数披露 `pre_range_rows`。runner `scripts/innovation_quota_w2.py` 门语义同步修正+selftest 补史前段两面用例（放行+计数漂移拒烧）。
- **纪律注记**：本修正=零燃烧窗内冻结面修正（R99 族·r251/r280 预承诺窗先例第三例·非结果驱动=拒跑面结构事实修正）；工程修复重跑须双跑留痕如实记账（§7 原文条款照用）；修正 commit 载=本件+runner+selftest。
