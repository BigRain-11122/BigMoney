# THERMO_OVERLAY_P1 · 温度计状态×题材配合面 overlay 切片【DRAFT v0 · 跑前未冻结】

> **状态横幅：DRAFT-NOT-FROZEN**。本件=T-2026-10-10-181 认领首轮产物（r825 bm-c·wm-red remediation lane）。跑前冻结 commit 前禁烧任何格；冻结时逐节回填占位并跑 banned_direction_gate。禁上线宣称、禁入册、禁 marks。任何「温度计状态→未来收益」判据宣称唯有本批过 science_gates 全起点三件套后成立（REGIME_THERMO_V1 §四诚实律）。
> 令源：O-20261009-2340-bm-a.md 循环侧承接④⑤ + O-20261006-1218 P6 消费面②。票=T-2026-10-10-181-P1（claimed bm-c r825）。

## §0 批件身份【占位·冻结时回填】

- 批名/批号：THERMO_OVERLAY_P1（格数=每「era×thermo_state×持有窗」单元格计入 N_eff；扩容即买单）
- 认领：T-181 已认领（claimed_by=bm-c @2026-10-10T03:29+08:00）。**F-04 先行未做**——冻结 commit 前 48h 窗口须落 fleet/inbox/ MSG-…-bmc-ALL-thermo-overlay-p1 声明（防双机在制撞车），未落=冻结门拒。
- 部门归属：dept:研究（题材配合面 overlay 切片·E6 情绪族供给测量面同源）
- 算力预算：轻量 pandas 面批（episode 窗×thermo 状态格集·预估 <10 min·单 worker·无需后台化）；批报告带 audit 段。
- 机队车道：bm-c 任意轮可跑（无 GPU 依赖）；与 CEO 令 O-20261010-0025 训练期错峰（RAM 守卫：>1.5GB 可用才跑）。

## §0.5 禁开方向硬闸【已填·BAN-05 命中+例外声明】

- **命中编号：BAN-05**（Market-temperature / breadth timing as a precondition；原否证=docs/audits/retail-quant-conclusions-v2-20260930.md#3）
- **例外类型：`new_data`**
- **原否证不可能看见的东西**：原否证所测的「水温/广度/涨跌家数」面=指数级宽度代理（涨跌家数/水温类指标）；本批判据面=**三轴涨停生态面板**（5,222 只全史 1996-12-16→2026-09-22 逐日封住率/连板梯队高度/恐慌跌停数，GM P6 主件 2026-10-09 才建成·results/regime_thermo/thermo_daily.csv）——原否证数据面上不存在该三轴信息（封住率≠涨跌家数：分母=触板家数非全市场；梯队高度=存量结构非流量广度）。
- **诚实披露（必录）**：机制族语义重叠真实存在——「温度调制风险敞口」与 BAN-05 前置门同族；若否证复现（温度面无前向信息），判负照报不粉饰。本批价值=把「题材配合面该不该吃温度 overlay」从直觉变成一次性受控测量。
- 冻结时必跑 `python Tools/banned_direction_gate.py --prereg research/THERMO_OVERLAY_P1.md`（rc0 放行·rc1 不受理 fail-closed）。

## §1 α 机制段【已填·D6】

四选一：**☑ 行为偏差**（锚定/注意力稀缺/追涨杀跌群体周期）
- 论证：题材 episode=散户群体注意力事件；温度计三轴=同一群体行为生态的逐日普查（封住=追涨意愿兑现率/梯队=注意力存续高度/恐慌=处置效应踩踏）。overlay 假设：题材 episode 前向结果随入场时点的群体强度状态系统分化（过热态=透支后均值回归由后进者付账；冷态=空间未耗尽）。**由谁付出代价**：过热态后进追高的散户群体（行为溢价转移面）。
- **§1.2 散户凭什么赢**：五选=**行为**。该维度散户「赢」在信息面=温度计是对自家群体（散户主导的打板生态·机构缺席该生态定价）的行为普查读数，属机构不定价的竞争真空信息；非速度/容量/制度优势主张。涉 RESEARCH 机构结论引用=无（本批纯内部数据面验证）。
- **同族相关性准入【D6·冻结时数值回填】**：本批=既有题材面的条件化 gate，非新独立 sleeve。D6 检查面=**条件差分序列**（thermo-on 减 thermo-off 的 episode 净值差）对在册交易员全体+在队/同批函数日收益序列的 max|corr|；逐对清单冻结时回填；`max|corr| ≥ 0.7 → 拒收`（确有新机制主张另开预注册论证）。结构性披露：overlay-on-题材面本体与题材族 corr 由构造正相关——D6 只约束差分面（新信息面）。

## §2 数据与面板【已填·锚四元组】

- **温度计臂锚**（判据面）：`results/regime_thermo/thermo_daily.csv` ＋ `pd.read_csv` raw 直读截断（非池面）＋起算窗 **1996-12-16**（涨跌停制度恢复日·冻结有效域）＋预热窗 **0 bar**（三轴全为当日描述计数·无指标预热；REGIME_THERMO_V1 §一冻结定义零刻度触碰）。
- **题材 episode 臂锚**（目标面）：`results/theme_persist_p1/faceB_by_theme.csv`（theme_id×n_bars×sys_net×bh_net 逐 episode 面）＋同窗源 `results/theme_persist_p1/theme_persist_p1.json` m1_t_face/faceB 结构 ＋ `pd.read_csv`/`json.load` 直读 ＋起算窗=题材批冻结 episode 格集（CYB2013..·43 波段 16 类）＋预热窗=episode 窗口自带（750 bar 窗面·无额外预热）。**冻结时回填项**：episode 精确日期格集的源面文件名（题材批 runner 的 episode 日期面——faceB 表只带 theme_id 年份标签，逐 episode 起讫日须从题材批正典件钉死并写四元组；钉不死=冻结门拒）。
- **evidence_cutoff（前向锁盒 D2）=2026-09-22（P-5C 冻结面·T-181 spec 指定）**：两臂取 min(温度计 2026-09-22, 题材批 cutoff)=2026-09-22；cutoff 后新 bar 禁回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`。
- 数据完备门：thermo_daily.csv 全史行数 ≥7,250（7,257 交易日 P-5C 面）且三轴字段零 NaN 桶外溢；题材 episode 表 ≥1,800 episode（famous16 面 n=52+rest n=1,770 同源口径）。
- **已知近似三条承袭披露**（REGIME_THERMO_V1 §四全盖）：①qfq 面板除权日相邻比率失真（少数封住/炸板误计）②历史 ST 逐日状态缺失→5% 率桶含罕见噪声（DATA_GAP 5% 桶·全史一致口径）③触板半分钱容差边界误计。影响面：温度轴读数噪声≤历史审计容差（名场面校准全对上=引擎可信度实证）；判据侧以「同噪声贯穿全 era」为前提，era 分层后噪声不构成方向性偏置主张。
- 种子选位：本批无新生成面（纯测量），无种子带占用面；若 runner 需置换检验种子，用 94_001..94_999 净袋（D-20261004-02② 禁顺爬 95_000+）。

## §3 方法学【草案·冻结时回填判线引用】

- **测量设计（face 双面）**：
  - **Face-A（主判面·overlay 信息面）**：题材 episode 净值（sys_net 与 bh_net 双口径）按入场日温度计状态分组的前向差异——温度状态分组=**三轴联合分层**（封住率 seal_rate 分位 × 梯队高度 max_height 分位 × 恐慌 n_sealed_down 门槛），分组边冻结=**era 内分位**（非全史分位·防年代漂移）。格=era×state×口径。
  - **Face-B（年代分层参照面·令源⑤）**：封住率长期衰减 21%→15%（2005→2026 年均）按 **era 分层**回填打板溢价类历史参照——era 划分=**等历法三段**（1996-12-16→2006-12-31／2007-01-01→2016-12-31／2017-01-01→2026-09-22·等长窗零偷看），era 边冻结后禁改。
- **随机基线（BACKTEST_PLAN 三铁律）**：同批同跑随机信号基线并记录试验总数 N——null=**块置换温度状态序列**（循环块置换·块长=状态段中位长度·保自相关结构·1,000 reps·种子 94_001 起），随机面与实面同格同表；N 逐格计数入 N_eff 累计台账。
- **判线**：全起点分布判据走 `science_gates.g1_prime_v2 / g2_registration_v2` 共享库 import（禁手抄判线·T-02 6/7+7/7 立法）；成本×2 面与 T+1 开盘保守代理（O-1132）按共享库默认口径；全起点=episode 全窗格集非挑窗。
- **era×state×口径 格数预估**：3 era × 状态格（三轴分层设计冻结时定·预估 8-12 状态格）× 2 口径 ≈ 48-72 格 + null 镜像格同数；扩容即买单。

## §4 出场轴显式声明【已填·TRIAL_LABOR_LAW §4 三选一】

**选② 持有到底声明**：本批=固定窗测量面（episode 750 bar 窗/前向持有窗=窗尾到期），runner **显式禁用引擎缺省出场栈**（`--no-default-exit` 面或等价开关·selftest 断言在位）；无策略自有出场、无 template_default。测量窗即终点，非交易管理面。

## §5 冻结门清单（下轮续作指针）

1. episode 精确日期格集源面钉死+四元组回填（§2 冻结时回填项）
2. F-04 inbox MSG 声明落盘（48h 窗）
3. `banned_direction_gate.py --prereg` rc0 实跑留痕
4. D6 差分面 max|corr| 数值逐对清单回填
5. 三轴分层状态格设计冻结（era 内分位边+恐慌门槛）+格数终值
6. science_gates import 路径+selftest 接线
7. 判据节逐字从共享库引用、零手抄——然后跑前 commit 冻结
8. runner=纯测量零注册零 marks；烧批错峰 CEO 训练（RAM 守卫）

---
*DRAFT v0 by bm-c r825 @2026-10-10T03:4x+08:00 — T-181 progress_r825_bmc。冻结前本件零判据资格零烧录资格；回填完成后按模板「跑前 commit 冻结」仪式进 burn。*
